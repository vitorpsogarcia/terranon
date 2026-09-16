import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.enums.game_state_enum import GameStateEnum
from core.manager.game_manager import GameManager
from core.manager.state_manager import StateManager
from core.states.base_state import GameScene
from core.states.ui.pause_menu_state import PauseMenuScene, PauseMenuState


class TestPauseMenuScene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.screen_size = (1056, 720)
        self.surface = pygame.Surface(self.screen_size)
        self.gm = GameManager(self.surface)
        self.sm = StateManager(self.gm)
        self.pause = PauseMenuScene(self.sm, self.screen_size)
        self.pause.enter()

    def test_inheritance_and_modal_flags(self):
        """PauseMenuScene deve herdar de GameScene, ser transparente e bloquear update."""
        self.assertTrue(issubclass(PauseMenuScene, GameScene))
        self.assertIs(PauseMenuState, PauseMenuScene)
        self.assertTrue(self.pause.is_transparent, "Fundo translúcido para jogo ficar visível")
        self.assertTrue(self.pause.blocks_update, "Deve pausar a lógica do jogo")

    def test_buttons_structure(self):
        """Menu de pausa deve ter Continuar, Reiniciar e Menu Principal."""
        self.assertEqual(self.pause.btn_resume.text, "CONTINUAR")
        self.assertEqual(self.pause.btn_restart.text, "REINICIAR PARTIDA")
        self.assertEqual(self.pause.btn_menu.text, "MENU PRINCIPAL")

    def test_resume_via_click(self):
        """Clicar em CONTINUAR chama state_manager.pop()."""
        pop_called = False

        def mock_pop():
            nonlocal pop_called
            pop_called = True

        self.sm.pop = mock_pop

        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.pause.btn_resume.rect.center,
        )
        self.pause.handle_events([click_event])
        self.assertTrue(pop_called)

    def test_resume_via_esc(self):
        """Pressionar ESC chama state_manager.pop()."""
        pop_called = False

        def mock_pop():
            nonlocal pop_called
            pop_called = True

        self.sm.pop = mock_pop

        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.pause.handle_events([esc_event])
        self.assertTrue(pop_called)

    def test_resume_via_enter(self):
        """Pressionar ENTER chama state_manager.pop()."""
        pop_called = False

        def mock_pop():
            nonlocal pop_called
            pop_called = True

        self.sm.pop = mock_pop

        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.pause.handle_events([enter_event])
        self.assertTrue(pop_called)

    def test_restart_game(self):
        """Clicar em REINICIAR chama state_manager.change_to(GameStateEnum.PLAY)."""
        target_state = None

        def mock_change_to(state):
            nonlocal target_state
            target_state = state

        self.sm.change_to = mock_change_to

        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.pause.btn_restart.rect.center,
        )
        self.pause.handle_events([click_event])
        self.assertEqual(target_state, GameStateEnum.PLAY)

    def test_go_to_menu(self):
        """Clicar em MENU PRINCIPAL chama state_manager.change_to(GameStateEnum.MENU)."""
        target_state = None

        def mock_change_to(state):
            nonlocal target_state
            target_state = state

        self.sm.change_to = mock_change_to

        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.pause.btn_menu.rect.center,
        )
        self.pause.handle_events([click_event])
        self.assertEqual(target_state, GameStateEnum.MENU)

    def test_draw_renders_without_errors(self):
        """Renderização do menu de pausa deve ocorrer sem exceções."""
        self.pause.draw(self.surface)


if __name__ == "__main__":
    unittest.main()
