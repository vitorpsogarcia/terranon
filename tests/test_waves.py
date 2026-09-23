import os
import sys
import unittest
from unittest.mock import MagicMock
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.enums.enemy_enum import EnemyEnum
from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.enums.game_event_enum import GameEventEnum
from core.enums.wave_state_enum import WaveStateEnum
from core.manager.event_manager import EventManager
from core.wave_manager import WaveManager
from core.waves.exponential_strategy import ExponentialWaveStrategy
from core.waves.wave_data import WaveData


class TestWaveStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = ExponentialWaveStrategy()

    def test_wave_values_match_csv_specification(self):
        """Verifica se os valores calculados correspondem exatamente à tabela do CSV."""
        expected_csv_data = {
            1: {"enemies": 3, "points": 5, "spawners_count": 1},
            2: {"enemies": 3, "points": 5, "spawners_count": 1},
            3: {"enemies": 4, "points": 5, "spawners_count": 1},
            4: {"enemies": 4, "points": 5, "spawners_count": 1},
            5: {"enemies": 4, "points": 6, "spawners_count": 2},
            6: {"enemies": 5, "points": 6, "spawners_count": 2},
            10: {"enemies": 7, "points": 7, "spawners_count": 3},
            15: {"enemies": 11, "points": 8, "spawners_count": 4},
            20: {"enemies": 18, "points": 8, "spawners_count": 4},
            25: {"enemies": 30, "points": 8, "spawners_count": 4},
            35: {"enemies": 77, "points": 8, "spawners_count": 4},
        }

        for wave_num, expected in expected_csv_data.items():
            data = self.strategy.generate_wave(wave_num)
            self.assertEqual(
                data.total_enemies,
                expected["enemies"],
                f"Falha na Wave {wave_num}: quantidade de inimigos divergente",
            )
            self.assertEqual(
                data.enemy_points,
                expected["points"],
                f"Falha na Wave {wave_num}: pontos por inimigo divergente",
            )
            self.assertEqual(
                len(data.active_spawners),
                expected["spawners_count"],
                f"Falha na Wave {wave_num}: número de spawners ativos divergente",
            )
            self.assertEqual(data.duration, 60.0)
            self.assertEqual(data.interval_duration, 30.0)

    def test_spawners_activation_sequence(self):
        """Verifica a ordem de ativação dos ninhos: BETA -> ALPHA -> GAMA -> DELTA."""
        w1 = self.strategy.generate_wave(1)
        self.assertEqual(w1.active_spawners, [EnemySpawnerEnum.SPWN_BETA])

        w5 = self.strategy.generate_wave(5)
        self.assertEqual(
            w5.active_spawners,
            [EnemySpawnerEnum.SPWN_BETA, EnemySpawnerEnum.SPWN_ALPHA],
        )

        w10 = self.strategy.generate_wave(10)
        self.assertEqual(
            w10.active_spawners,
            [
                EnemySpawnerEnum.SPWN_BETA,
                EnemySpawnerEnum.SPWN_ALPHA,
                EnemySpawnerEnum.SPWN_GAMA,
            ],
        )

        w15 = self.strategy.generate_wave(15)
        self.assertEqual(
            w15.active_spawners,
            [
                EnemySpawnerEnum.SPWN_BETA,
                EnemySpawnerEnum.SPWN_ALPHA,
                EnemySpawnerEnum.SPWN_GAMA,
                EnemySpawnerEnum.SPWN_DELTA,
            ],
        )


class MockEnemy:
    def __init__(self, is_alive: bool = True):
        self._is_alive = is_alive
        self.active = True

    def alive(self) -> bool:
        return self._is_alive


class TestWaveManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.spawner_beta = MagicMock()
        self.spawner_beta.spawn_enemy.return_value = MockEnemy(True)

        self.spawner_alpha = MagicMock()
        self.spawner_alpha.spawn_enemy.return_value = MockEnemy(True)

        self.spawners = {
            EnemySpawnerEnum.SPWN_BETA.value: self.spawner_beta,
            EnemySpawnerEnum.SPWN_ALPHA.value: self.spawner_alpha,
        }

        self.strategy = ExponentialWaveStrategy()
        self.manager = WaveManager(
            spawners_dict=self.spawners,
            strategy=self.strategy,
            warmup_duration=30.0,
        )

    def tearDown(self):
        self.manager.destroy()

    def test_initial_state_is_warmup(self):
        """WaveManager deve inicializar no estado WARMUP com 30s de contagem."""
        self.assertEqual(self.manager.state, WaveStateEnum.WARMUP)
        self.assertEqual(self.manager.current_wave_number, 1)
        self.assertEqual(self.manager.timer, 30.0)

    def test_warmup_countdown_transitions_to_active(self):
        """Ao expirar o tempo de warmup, deve transitar para a Wave 1 no estado ACTIVE."""
        self.manager.update(29.0)
        self.assertEqual(self.manager.state, WaveStateEnum.WARMUP)

        self.manager.update(1.1)
        self.assertEqual(self.manager.state, WaveStateEnum.ACTIVE)
        self.assertEqual(self.manager.current_wave_number, 1)
        self.assertEqual(self.manager.timer, 60.0)
        self.assertIsNotNone(self.manager.current_wave_data)

    def test_skip_countdown_during_warmup(self):
        """Chamar skip_countdown durante warmup deve iniciar a Wave 1 imediatamente."""
        result = self.manager.skip_countdown()
        self.assertTrue(result)
        self.assertEqual(self.manager.state, WaveStateEnum.ACTIVE)
        self.assertEqual(self.manager.current_wave_number, 1)

    def test_skip_countdown_during_active_returns_false(self):
        """Durante a onda ativa, skip_countdown não deve surtir efeito."""
        self.manager.skip_countdown()  # Entra em ACTIVE
        self.assertEqual(self.manager.state, WaveStateEnum.ACTIVE)

        result = self.manager.skip_countdown()
        self.assertFalse(result)
        self.assertEqual(self.manager.state, WaveStateEnum.ACTIVE)

    def test_skip_countdown_during_interval_advances_wave(self):
        """Durante o intervalo, skip_countdown deve iniciar a próxima onda imediatamente."""
        self.manager.start_wave(1)
        self.manager.end_wave()
        self.assertEqual(self.manager.state, WaveStateEnum.INTERVAL)

        result = self.manager.skip_countdown()
        self.assertTrue(result)
        self.assertEqual(self.manager.state, WaveStateEnum.ACTIVE)
        self.assertEqual(self.manager.current_wave_number, 2)

    def test_spawning_enemies_and_points_injection(self):
        """Inimigos devem ser gerados com a pontuação correta da wave."""
        self.manager.start_wave(1)
        self.manager.spawn_delay = 0.1

        self.manager.update(0.15)
        self.spawner_beta.spawn_enemy.assert_called_with(
            enemy_type=EnemyEnum.GOBLIN, points=5
        )
        self.assertEqual(self.manager.spawned_in_current_wave, 1)

    def test_early_wave_completion_when_all_enemies_dead(self):
        """A onda deve encerrar e ir para INTERVAL antes dos 60s se todos os monstros morrerem."""
        # Configura wave de 1 inimigo
        mock_strategy = MagicMock()
        mock_strategy.generate_wave.return_value = WaveData(
            wave_number=1,
            total_enemies=1,
            enemy_points=5,
            active_spawners=[EnemySpawnerEnum.SPWN_BETA],
            duration=60.0,
            interval_duration=30.0,
        )
        test_enemy = MockEnemy(is_alive=True)
        self.spawner_beta.spawn_enemy.return_value = test_enemy

        manager = WaveManager(self.spawners, strategy=mock_strategy, warmup_duration=1.0)
        manager.start_wave(1)
        manager.spawn_delay = 0.1

        # Spawna o único inimigo
        manager.update(0.15)
        self.assertEqual(manager.spawned_in_current_wave, 1)
        self.assertEqual(manager.state, WaveStateEnum.ACTIVE)

        # Monstro é derrotado
        test_enemy._is_alive = False
        manager.update(0.01)

        self.assertEqual(manager.state, WaveStateEnum.INTERVAL)
        self.assertEqual(manager.timer, 30.0)
        manager.destroy()

    def test_wave_timeout_transitions_to_interval(self):
        """Ao expirar os 60s, a onda deve transitar para INTERVAL."""
        self.manager.start_wave(1)
        self.manager.update(60.1)
        self.assertEqual(self.manager.state, WaveStateEnum.INTERVAL)

    def test_reset_waves_event(self):
        """Disparar RESET_WAVES deve restaurar o manager para a Wave 1 em WARMUP."""
        self.manager.start_wave(5)
        self.assertEqual(self.manager.current_wave_number, 5)

        EventManager().emit(GameEventEnum.RESET_WAVES)
        self.assertEqual(self.manager.state, WaveStateEnum.WARMUP)
        self.assertEqual(self.manager.current_wave_number, 1)
        self.assertEqual(self.manager.timer, 30.0)

    def test_skip_wave_countdown_event(self):
        """Disparar SKIP_WAVE_COUNTDOWN via EventManager deve avançar a contagem."""
        self.assertEqual(self.manager.state, WaveStateEnum.WARMUP)
        EventManager().emit(GameEventEnum.SKIP_WAVE_COUNTDOWN)
        self.assertEqual(self.manager.state, WaveStateEnum.ACTIVE)
        self.assertEqual(self.manager.current_wave_number, 1)

    def test_reset_waves_kills_alive_enemies(self):
        """Disparar RESET_WAVES deve eliminar inimigos vivos da onda antes de reiniciar."""
        mock_enemy = MagicMock()
        mock_enemy.alive.return_value = True
        self.manager.current_wave_enemies.append(mock_enemy)

        EventManager().emit(GameEventEnum.RESET_WAVES)
        mock_enemy.kill.assert_called_once()
        self.assertEqual(len(self.manager.current_wave_enemies), 0)
        self.assertEqual(self.manager.state, WaveStateEnum.WARMUP)

    def test_enemy_factory_forwards_custom_points(self):
        """EnemyFactory.create_enemy deve repassar points ao inicializar o inimigo."""
        from core.factories.enemy_factory import EnemyFactory

        mock_polyline = MagicMock()
        enemy = EnemyFactory.create_enemy(
            EnemyEnum.GOBLIN, pygame.Vector2(100, 100), mock_polyline, points=8
        )
        self.assertEqual(enemy._points, 8)

    def test_draw_renders_hud_without_error(self):
        """Renderização do HUD no topo deve ocorrer sem erros em todos os estados."""
        surface = pygame.Surface((1056, 720))

        # Teste em WARMUP
        self.manager.state = WaveStateEnum.WARMUP
        self.manager.draw(surface)

        # Teste em ACTIVE
        self.manager.start_wave(1)
        self.manager.draw(surface)

        # Teste em INTERVAL
        self.manager.end_wave()
        self.manager.draw(surface)

    def test_wave_started_and_ended_events_emitted(self):
        """Eventos WAVE_STARTED e WAVE_ENDED devem ser emitidos no início e fim de cada onda."""
        started_waves = []
        ended_waves = []

        def on_started(wave_index, *args, **kwargs):
            started_waves.append(wave_index)

        def on_ended(wave_index, *args, **kwargs):
            ended_waves.append(wave_index)

        EventManager().subscribe(GameEventEnum.WAVE_STARTED, on_started)
        EventManager().subscribe(GameEventEnum.WAVE_ENDED, on_ended)

        try:
            self.manager.start_wave(1)
            self.assertEqual(started_waves, [1])

            self.manager.end_wave()
            self.assertEqual(ended_waves, [1])

            self.manager.start_next_wave()
            self.assertEqual(started_waves, [1, 2])
            self.assertEqual(self.manager.current_wave_number, 2)
            self.assertEqual(self.manager.current_wave_index, 2)
        finally:
            EventManager().unsubscribe(GameEventEnum.WAVE_STARTED, on_started)
            EventManager().unsubscribe(GameEventEnum.WAVE_ENDED, on_ended)


class TestUpgradeSelectionIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_upgrade_selection_preserves_interval_and_allows_skip(self):
        """Selecionar card deve aplicar upgrade e preservar INTERVAL, permitindo pular contagem."""
        from core.manager.game_manager import GameManager
        from core.manager.state_manager import StateManager
        from core.states.ui.upgrade_selection_ui import UpgradeSelectionUI

        surface = pygame.Surface((1056, 720))
        gm = GameManager(surface)
        sm = StateManager(gm)

        # Mock play_state com player e wave_manager
        mock_player = MagicMock()
        mock_player.has_shield = False
        mock_player.health.damage_reduction = 0.0
        mock_player.health.max_damage_reduction = 0.75

        mock_spawners = {
            EnemySpawnerEnum.SPWN_BETA.value: MagicMock(),
        }
        wave_mgr = WaveManager(mock_spawners, warmup_duration=1.0)
        wave_mgr.start_wave(1)
        wave_mgr.end_wave()  # Entra em INTERVAL (30s)
        self.assertEqual(wave_mgr.state, WaveStateEnum.INTERVAL)

        mock_play_state = MagicMock()
        mock_play_state.player = mock_player
        mock_play_state.wave_manager = wave_mgr

        gm.state_stack = [mock_play_state]

        upgrade_ui = UpgradeSelectionUI(sm, (1056, 720))
        self.assertTrue(upgrade_ui.is_transparent)
        self.assertTrue(upgrade_ui.blocks_update)

        upgrade_ui.enter()
        self.assertEqual(len(upgrade_ui.upgrades), 3)

        # Simula seleção do primeiro card
        pop_called = False

        def mock_pop():
            nonlocal pop_called
            pop_called = True

        sm.pop = mock_pop

        upgrade_ui._select(0)
        self.assertTrue(pop_called)
        # O intervalo de preparação é preservado para o jogador construir/preparar
        self.assertEqual(wave_mgr.state, WaveStateEnum.INTERVAL)
        self.assertEqual(wave_mgr.current_wave_number, 1)

        # O jogador pode optar por pular a contagem com ESPAÇO
        EventManager().emit(GameEventEnum.SKIP_WAVE_COUNTDOWN)
        self.assertEqual(wave_mgr.current_wave_number, 2)
        self.assertEqual(wave_mgr.state, WaveStateEnum.ACTIVE)

        wave_mgr.destroy()


if __name__ == "__main__":
    unittest.main()

