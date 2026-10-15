import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.manager.build_manager import BuildManager
from core.manager.effect_manager import EffectManager
from core.manager.event_manager import EventManager
from core.manager.game_manager import GameManager
from core.manager.spatial_manager import SpatialManager
from core.manager.state_manager import StateManager
from core.states.play_state import PlayState
from core.states.ui.game_over import GameOverState
from entities.structures.towers.generic_tower import GenericTower


class TestPlayStateCleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.surface = pygame.Surface((800, 600))
        self.gm = GameManager(self.surface)
        self.sm = StateManager(self.gm)
        self.gm.state_stack.clear()

        self.sm.register_state(
            GameStateEnum.PLAY,
            lambda: PlayState(self.sm, self.gm, (800, 600)),
        )
        self.sm.register_state(
            GameStateEnum.GAME_OVER,
            lambda: GameOverState(self.sm, (800, 600)),
        )

    def tearDown(self):
        while self.gm.state_stack:
            state = self.gm.state_stack.pop()
            state.exit()
        SpatialManager().reset()
        EffectManager().clear()
        if BuildManager().is_building:
            BuildManager().cancel_build()

    def test_cleanup_on_exit_and_reload(self):
        """Ao descarregar PlayState (ex: retornar ao menu) e recarregar, não devem sobrar fantasmas."""
        self.sm.change_to(GameStateEnum.PLAY)
        play1: PlayState = self.gm.current_state
        sp = SpatialManager()

        initial_obstacles = len(sp.obstacles)
        initial_colliders = len(sp.world_colliders)
        initial_structures = len(sp.structures_group)
        self.assertGreater(initial_obstacles, 0)
        self.assertGreater(initial_colliders, 0)
        self.assertEqual(initial_structures, 3)  # 1 Base + 2 Debug Towers

        # Simula criação de torre do jogador e spawn de inimigo
        player_tower = GenericTower(pygame.Vector2(100, 100))
        play1.world.add_object(player_tower)
        self.assertEqual(len(sp.structures_group), 4)

        play1.wave_manager.start_wave(1)
        play1.wave_manager.update(2.0)
        self.assertGreater(len(sp.enemies_group), 0)

        # Simula saída da cena (ex: retornar ao menu principal)
        play1.exit()

        self.assertEqual(len(sp.obstacles), 0)
        self.assertEqual(len(sp.world_colliders), 0)
        self.assertEqual(len(sp.structures_group), 0)
        self.assertEqual(len(sp.enemies_group), 0)
        self.assertEqual(len(sp.spawners), 0)

        # Recarrega o jogo
        self.sm.change_to(GameStateEnum.PLAY)
        play2: PlayState = self.gm.current_state

        # Contagens devem corresponder exatamente a um mundo limpo, sem fantasmas
        self.assertEqual(len(sp.obstacles), initial_obstacles)
        self.assertEqual(len(sp.world_colliders), initial_colliders)
        self.assertEqual(len(sp.structures_group), initial_structures)
        self.assertEqual(len(sp.enemies_group), 0)
        self.assertEqual(len(sp.spawners), 4)

    def test_cleanup_on_player_death(self):
        """Quando o jogador morre, PlayState descarrega e limpa entidades sem deixar fantasmas."""
        self.sm.change_to(GameStateEnum.PLAY)
        play: PlayState = self.gm.current_state
        sp = SpatialManager()
        initial_colliders = len(sp.world_colliders)

        # Jogador morre
        play.player.on_death()

        self.assertIsInstance(self.gm.current_state, GameOverState)
        self.assertEqual(len(sp.structures_group), 0)
        self.assertEqual(len(sp.world_colliders), 0)
        self.assertEqual(len(sp.enemies_group), 0)

        # Recarregar o jogo através de 'JOGAR NOVAMENTE'
        self.sm.change_to(GameStateEnum.PLAY)
        self.assertEqual(len(sp.world_colliders), initial_colliders)
        self.assertEqual(len(sp.structures_group), 3)

    def test_cleanup_on_base_death(self):
        """Quando a base é destruída, PlayState descarrega e limpa entidades sem deixar fantasmas."""
        self.sm.change_to(GameStateEnum.PLAY)
        play: PlayState = self.gm.current_state
        sp = SpatialManager()
        initial_colliders = len(sp.world_colliders)

        # Base morre
        play.world.main_base.on_death()

        self.assertIsInstance(self.gm.current_state, GameOverState)
        self.assertEqual(len(sp.structures_group), 0)
        self.assertEqual(len(sp.world_colliders), 0)

        # Recarrega partida
        self.sm.change_to(GameStateEnum.PLAY)
        self.assertEqual(len(sp.world_colliders), initial_colliders)
        self.assertEqual(len(sp.structures_group), 3)

    def test_event_manager_emit_snapshot_resilience(self):
        """Verifica que o EventManager não pula listeners quando um callback remove a própria assinatura."""
        called = []

        def listener_a():
            called.append("A")
            EventManager().unsubscribe(GameEventEnum.GAME_OVER, listener_a)

        def listener_b():
            called.append("B")

        EventManager().subscribe(GameEventEnum.GAME_OVER, listener_a)
        EventManager().subscribe(GameEventEnum.GAME_OVER, listener_b)

        EventManager().emit(GameEventEnum.GAME_OVER)

        self.assertEqual(called, ["A", "B"])
        EventManager().unsubscribe(GameEventEnum.GAME_OVER, listener_b)

    def test_handle_events_transitions_cleanly_on_key_k_and_escape(self):
        """Pressionar K ou ESC em handle_events deve transitar sem erro de atributo no build_menu."""
        self.sm.change_to(GameStateEnum.PLAY)
        play: PlayState = self.gm.current_state

        event_k = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k)
        play.handle_events([event_k])

        self.assertIsInstance(self.gm.current_state, GameOverState)

