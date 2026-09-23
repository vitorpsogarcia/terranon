import logging
from typing import TYPE_CHECKING

import pygame

from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.enums.game_event_enum import GameEventEnum
from core.enums.wave_state_enum import WaveStateEnum
from core.manager.event_manager import EventManager
from core.ui.wave_hud import WaveHUD
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
        self._valid_spawner_ids: list[str] = []

        self._hud = WaveHUD()

        EventManager().subscribe(event=GameEventEnum.RESET_WAVES, listener=self.reset)
        EventManager().subscribe(
            event=GameEventEnum.SKIP_WAVE_COUNTDOWN, listener=self.skip_countdown
        )

    def reset(self, *args, **kwargs):
        """Reinicia o ciclo completo de ondas, eliminando inimigos remanescentes e voltando ao aquecimento inicial."""
        for enemy in self.current_wave_enemies:
            if enemy.alive():
                enemy.kill()
        self.current_wave_enemies.clear()

        self.state = WaveStateEnum.WARMUP
        self.current_wave_number = 1
        self.timer = self.warmup_duration
        self.current_wave_data = None
        self.spawned_in_current_wave = 0
        self.current_delay_timer = 0.0
        self.active_spawner_index = 0
        self._valid_spawner_ids.clear()

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

        # Mantém apenas os inimigos que continuam vivos de waves anteriores
        self.current_wave_enemies = [
            e for e in self.current_wave_enemies if e.alive() and getattr(e, "active", True)
        ]

        # Pré-computa os spawners válidos para esta onda
        if self.current_wave_data.active_spawners:
            self._valid_spawner_ids = [
                s.value for s in self.current_wave_data.active_spawners if s.value in self.spawners
            ]
        else:
            self._valid_spawner_ids = []

        if not self._valid_spawner_ids:
            self._valid_spawner_ids = list(self.spawners.keys())

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

    def skip_countdown(self, *args, **kwargs) -> bool:
        """Pula a contagem regressiva de warmup ou intervalo para iniciar a onda imediatamente."""
        if self.state == WaveStateEnum.WARMUP:
            self.start_wave(1)
            return True
        elif self.state == WaveStateEnum.INTERVAL:
            self.start_wave(self.current_wave_number + 1)
            return True
        return False

    def alive_enemies_count(self) -> int:
        """Retorna a quantidade de inimigos gerados que continuam vivos, limpando referências mortas."""
        self.current_wave_enemies = [
            e for e in self.current_wave_enemies if e.alive() and getattr(e, "active", True)
        ]
        return len(self.current_wave_enemies)

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
                        self.current_delay_timer -= self.spawn_delay

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
        if not self._valid_spawner_ids:
            return

        # Seleção em Round-Robin
        spawner_id = self._valid_spawner_ids[
            self.active_spawner_index % len(self._valid_spawner_ids)
        ]
        self.active_spawner_index += 1

        spawner = self.spawners.get(spawner_id)
        if spawner is not None:
            enemy = spawner.spawn_enemy(
                enemy_type=data.enemy_type, points=data.enemy_points
            )
            if enemy is not None:
                self.current_wave_enemies.append(enemy)
            self.spawned_in_current_wave += 1

    def draw(self, surface: pygame.Surface):
        """Desenha o contador e status das ondas centralizado no topo da tela via WaveHUD."""
        total = self.current_wave_data.total_enemies if self.current_wave_data else 0
        self._hud.draw(
            surface=surface,
            state=self.state,
            current_wave_number=self.current_wave_number,
            timer=self.timer,
            alive_enemies=self.alive_enemies_count(),
            total_enemies=total,
        )

    def destroy(self):
        """Remove assinaturas do barramento de eventos."""
        EventManager().unsubscribe(event=GameEventEnum.RESET_WAVES, listener=self.reset)
        EventManager().unsubscribe(
            event=GameEventEnum.SKIP_WAVE_COUNTDOWN, listener=self.skip_countdown
        )
