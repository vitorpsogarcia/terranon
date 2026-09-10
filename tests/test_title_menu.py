import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.enums.game_state_enum import GameStateEnum
from core.manager.game_manager import GameManager
from core.manager.highscore_manager import HighscoreManager
from core.manager.sound_manager import SoundManager
from core.manager.state_manager import StateManager
from core.states.base_state import GameScene
from core.states.ui.menu_state import MenuState, TitleMenuScene


class TestTitleMenuScene(unittest.TestCase):
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
        self.menu = TitleMenuScene(self.sm, self.screen_size)
        self.menu.enter()

    def test_inheritance_and_alias(self):
        """TitleMenuScene deve herdar de GameScene e ser alias de MenuState."""
        self.assertTrue(issubclass(TitleMenuScene, GameScene))
        self.assertIs(MenuState, TitleMenuScene)

    def test_main_buttons_structure(self):
        """Menu deve conter os botões Jogar, Recordes, Configurações e Sair."""
        self.assertEqual(self.menu.btn_play.text, "JOGAR")
        self.assertEqual(self.menu.btn_highscores.text, "RECORDES")
        self.assertEqual(self.menu.btn_settings.text, "CONFIGURAÇÕES / ÁUDIO")
        self.assertEqual(self.menu.btn_quit.text, "SAIR")
        self.assertEqual(self.menu.view_mode, "main")

    def test_click_play_opens_name_input_modal(self):
        """Clicar em JOGAR deve abrir o modal de input de nome."""
        # Simula clique no botão de Jogar
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.menu.btn_play.rect.center,
        )
        self.menu.handle_events([click_event])
        self.assertEqual(self.menu.view_mode, "name_input")
        self.assertTrue(self.menu.name_input.is_active)

    def test_enter_key_opens_name_input_modal(self):
        """Pressionar ENTER no menu principal abre o modal de nome."""
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.menu.handle_events([enter_event])
        self.assertEqual(self.menu.view_mode, "name_input")

    def test_confirm_name_transitions_to_play(self):
        """Confirmar o nome deve registrar no HighscoreManager e transitar para PLAY."""
        called_play = False

        def mock_change_state(scene):
            nonlocal called_play
            called_play = True

        self.gm.change_state = mock_change_state
        self.sm.register_state(GameStateEnum.PLAY, lambda: None)

        self.menu._start_name_input()
        self.menu.name_input.text = "Guerreiro"
        self.menu._confirm_player_name("Guerreiro")

        self.assertEqual(HighscoreManager().current_player_name, "Guerreiro")
        self.assertEqual(self.menu.view_mode, "main")
        self.assertTrue(called_play)

    def test_cancel_name_returns_to_main(self):
        """Cancelar a digitação de nome via ESC deve voltar ao menu principal."""
        self.menu._start_name_input()
        self.assertEqual(self.menu.view_mode, "name_input")

        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.menu.handle_events([esc_event])
        self.assertEqual(self.menu.view_mode, "main")

    def test_click_highscores_opens_highscores_modal(self):
        """Clicar em RECORDES abre o modal dedicado de Highscores."""
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.menu.btn_highscores.rect.center,
        )
        self.menu.handle_events([click_event])
        self.assertEqual(self.menu.view_mode, "highscores")

        # Pressionar ESC volta para o menu principal
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.menu.handle_events([esc_event])
        self.assertEqual(self.menu.view_mode, "main")

    def test_click_settings_opens_settings_modal_and_toggles_audio(self):
        """Clicar em CONFIGURAÇÕES abre o modal e permite alternar áudio."""
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.menu.btn_settings.rect.center,
        )
        self.menu.handle_events([click_event])
        self.assertEqual(self.menu.view_mode, "settings")

        sound = SoundManager()
        # Testar toggle da música
        orig_music = sound.volumes.get("music", 1.0)
        self.menu._toggle_music()
        new_music = sound.volumes.get("music", 1.0)
        self.assertNotEqual(orig_music, new_music)

        # Restaurar volume
        sound.set_volume("music", 1.0)

    def test_quit_game_terminates_gracefully(self):
        """Clicar em SAIR sinaliza o GameManager para parar."""
        self.gm._running = True
        self.menu._quit_game()
        self.assertFalse(self.gm._running)

    def test_draw_renders_without_errors(self):
        """Renderização do menu em todos os modos visuais deve ocorrer sem falhas."""
        for mode in ["main", "name_input", "settings", "highscores"]:
            self.menu.view_mode = mode
            self.menu.draw(self.surface)


if __name__ == "__main__":
    unittest.main()

