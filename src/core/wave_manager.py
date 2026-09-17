import logging
import math
from typing import TYPE_CHECKING

import pygame

from core.enums.enemy_enum import EnemyEnum
from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.enums.game_event_enum import GameEventEnum
from core.enums.wave_state_enum import WaveStateEnum
from core.manager.event_manager import EventManager
from core.settings.colors import Colors
from core.waves.exponential_strategy import ExponentialWaveStrategy
from core.waves.wave_data import WaveData
from core.waves.wave_strategy import IWaveStrategy

if TYPE_CHECKING:
    from entities.character.goblin import Enemy
    from entities.enemy_spawner import EnemySpawner


class WaveManager:
    """Gerenciador dinâmico do ciclo de vida das ondas de inimigos."""

    _logger = logging.getLogger("WaveManager")

    def __init__(
        self,
        spawners_dict: "dict[str, EnemySpawner]",
        strategy: "IWaveStrategy | None" = None,
        warmup_duration: float = 30.0,
    ):
        self.spawners = spawners_dict
        self.strategy: IWaveStrategy = strategy or ExponentialWaveStrategy()
        self.warmup_duration = warmup_duration

        self.state: WaveStateEnum = WaveStateEnum.WARMUP
        self.current_wave_number: int = 1
        self.timer: float = self.warmup_duration
        self.current_wave_data: "WaveData | None" = None

        self.spawned_in_current_wave: int = 0
        self.spawn_delay: float = 1.2
        self.current_delay_timer: float = 0.0
        self.active_spawner_index: int = 0
        self.current_wave_enemies: list["Enemy"] = []

        # Fontes do HUD
        self._font_title: "pygame.font.Font | None" = None
        self._font_sub: "pygame.font.Font | None" = None

        EventManager().subscribe(event=GameEventEnum.RESET_WAVES, listener=self.reset)

    def _ensure_fonts(self):
        if self._font_title is None and pygame.font.get_init():
            self._font_title = pygame.font.SysFont("Arial", 18, bold=True)
            self._font_sub = pygame.font.SysFont("Arial", 12)

    def reset(self):
        """Reinicia o ciclo completo de ondas, voltando ao aquecimento inicial."""
        self.state = WaveStateEnum.WARMUP
        self.current_wave_number = 1
        self.timer = self.warmup_duration
        self.current_wave_data = None
        self.spawned_in_current_wave = 0
        self.current_delay_timer = 0.0
        self.active_spawner_index = 0
        self.current_wave_enemies.clear()

    @property
    def current_wave_index(self) -> int:
        return self.current_wave_number

    @current_wave_index.setter
    def current_wave_index(self, value: int):
        self.current_wave_number = value

    def start_wave(self, wave_number: int):
        """Inicia a onda com os parâmetros gerados pela estratégia."""
        self.current_wave_number = max(1, wave_number)
        self.current_wave_data = self.strategy.generate_wave(self.current_wave_number)
        self.state = WaveStateEnum.ACTIVE
        self.timer = self.current_wave_data.duration

        self.spawned_in_current_wave = 0
        self.current_delay_timer = 0.0
        self.active_spawner_index = 0
        self.current_wave_enemies.clear()

        # Cadência dinâmica: entre 0.3s e 1.5s por monstro
        total = self.current_wave_data.total_enemies
        self.spawn_delay = max(0.3, min(1.5, 45.0 / total if total > 0 else 1.2))

        EventManager().emit(
            GameEventEnum.WAVE_STARTED, wave_index=self.current_wave_number
        )

    def end_wave(self):
        """Conclui a onda ativa, transita para o intervalo de descanso e notifica o encerramento."""
        self.state = WaveStateEnum.INTERVAL
        interval = (
            self.current_wave_data.interval_duration
            if self.current_wave_data
            else 30.0
        )
        self.timer = interval
        EventManager().emit(
            GameEventEnum.WAVE_ENDED, wave_index=self.current_wave_number
        )

    def start_next_wave(self):
        """Inicia a próxima onda após a seleção de melhorias pós-onda."""
        self.start_wave(self.current_wave_number + 1)

    def skip_countdown(self) -> bool:
        """Pula a contagem regressiva de warmup ou intervalo para iniciar a onda imediatamente."""
        if self.state == WaveStateEnum.WARMUP:
            self.start_wave(1)
            return True
        elif self.state == WaveStateEnum.INTERVAL:
            self.start_wave(self.current_wave_number + 1)
            return True
        return False

    def alive_enemies_count(self) -> int:
        """Retorna a quantidade de inimigos gerados na onda atual que continuam vivos."""
        return sum(1 for e in self.current_wave_enemies if e.alive() and getattr(e, "active", True))

    def update(self, dt: float):
        """Atualiza a máquina de estados, cronômetros e disparos de inimigos."""
        if self.state == WaveStateEnum.WARMUP:
            self.timer -= dt
            if self.timer <= 0:
                self.start_wave(1)

        elif self.state == WaveStateEnum.ACTIVE:
            self.timer -= dt
            data = self.current_wave_data

            if data is not None:
                # Gerar inimigos com a cadência definida
                if self.spawned_in_current_wave < data.total_enemies:
                    self.current_delay_timer += dt
                    if self.current_delay_timer >= self.spawn_delay:
                        self._spawn_next_enemy(data)
                        self.current_delay_timer = 0.0

                # Condição 1: Todos os inimigos spawnados e eliminados
                all_spawned = self.spawned_in_current_wave >= data.total_enemies
                if all_spawned and self.alive_enemies_count() == 0:
                    self.end_wave()
                    return

            # Condição 2: Tempo máximo da onda expirou
            if self.timer <= 0:
                self.end_wave()

        elif self.state == WaveStateEnum.INTERVAL:
            self.timer -= dt
            if self.timer <= 0:
                self.start_wave(self.current_wave_number + 1)

    def _spawn_next_enemy(self, data: WaveData):
        """Distribui o próximo inimigo para um dos spawners ativos em Round-Robin."""
        if not data.active_spawners:
            return

        # Obter IDs dos spawners válidos e existentes no mapa
        valid_spawner_ids = [
            s.value for s in data.active_spawners if s.value in self.spawners
        ]

        if not valid_spawner_ids:
            # Fallback caso os nomes não batam: usa qualquer spawner registrado
            valid_spawner_ids = list(self.spawners.keys())

        if not valid_spawner_ids:
            return

        # Seleção em Round-Robin
        spawner_id = valid_spawner_ids[self.active_spawner_index % len(valid_spawner_ids)]
        self.active_spawner_index += 1

        spawner = self.spawners.get(spawner_id)
        if spawner is not None:
            enemy = spawner.spawn_enemy(
                enemy_type=EnemyEnum.GOBLIN, points=data.enemy_points
            )
            if enemy is not None:
                self.current_wave_enemies.append(enemy)
            self.spawned_in_current_wave += 1

    def draw(self, surface: pygame.Surface):
        """Desenha o contador e status das ondas centralizado no topo da tela."""
        self._ensure_fonts()
        if self._font_title is None or self._font_sub is None:
            return

        screen_w = surface.get_width()
        badge_w = 320
        badge_h = 48
        badge_x = (screen_w - badge_w) // 2
        badge_y = 14
        badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)

        # Fundo semitransparente
        bg_surface = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        bg_surface.fill((20, 28, 45, 220))
        surface.blit(bg_surface, (badge_x, badge_y))

        # Borda
        border_color = (
            Colors.brand.secondary
            if self.state in (WaveStateEnum.WARMUP, WaveStateEnum.INTERVAL)
            else Colors.brand.primary
        )
        pygame.draw.rect(surface, border_color, badge_rect, width=1, border_radius=8)

        # Textos de acordo com o estado
        segundos = max(0, math.ceil(self.timer))

        if self.state == WaveStateEnum.WARMUP:
            main_text = f"PREPARE-SE: {segundos}s"
            main_color = Colors.brand.secondary
            sub_text = "[ESPAÇO] Iniciar Onda Agora"
            sub_color = Colors.text.secondary

        elif self.state == WaveStateEnum.ACTIVE:
            main_text = f"ONDA {self.current_wave_number}  |  {segundos}s"
            main_color = Colors.brand.primary
            total = self.current_wave_data.total_enemies if self.current_wave_data else 0
            sub_text = f"Inimigos Restantes: {self.alive_enemies_count()} / {total}"
            sub_color = Colors.text.primary

        else:  # WaveStateEnum.INTERVAL
            main_text = f"PRÓXIMA ONDA EM: {segundos}s"
            main_color = Colors.brand.secondary
            sub_text = "[ESPAÇO] Iniciar Próxima Onda"
            sub_color = Colors.text.secondary

        # Renderização e centralização dos textos
        title_surf = self._font_title.render(main_text, True, main_color)
        sub_surf = self._font_sub.render(sub_text, True, sub_color)

        title_pos = (
            badge_x + (badge_w - title_surf.get_width()) // 2,
            badge_y + 5,
        )
        sub_pos = (
            badge_x + (badge_w - sub_surf.get_width()) // 2,
            badge_y + 27,
        )

        surface.blit(title_surf, title_pos)
        surface.blit(sub_surf, sub_pos)

    def destroy(self):
        """Remove assinaturas do barramento de eventos."""
        EventManager().unsubscribe(event=GameEventEnum.RESET_WAVES, listener=self.reset)
