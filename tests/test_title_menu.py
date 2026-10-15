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
        cls.original_scores = HighscoreManager().load_scores()

    @classmethod
    def tearDownClass(cls):
        HighscoreManager().save_scores(cls.original_scores)
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
        self.assertIn("CONFIGURAÇÕES", self.menu.btn_settings.text)
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

        def mock_change_to(state):
            nonlocal called_play
            called_play = (state == GameStateEnum.PLAY)

        self.sm.change_to = mock_change_to

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

    def test_side_highscores_panel_has_clear_button(self):
        """Painel lateral de recordes deve conter o botão de lixeira para limpeza."""
        self.assertIn(self.menu.btn_clear_scores, self.menu.side_highscores_panel.children)
        self.assertEqual(self.menu.btn_clear_scores.icon_type, "trash")
        self.assertLessEqual(
            self.menu.btn_clear_scores.rect.right, self.menu.side_highscores_panel.rect.right
        )

    def test_clear_highscores_via_button(self):
        """Clicar no botão de lixeira deve limpar o arquivo de scores e a lista local."""
        hm = HighscoreManager()
        hm.add_score("JogadorTeste", 500)
        self.menu.highscores = hm.get_top_scores(10)
        self.assertTrue(len(self.menu.highscores) > 0)

        # Simula clique no botão de lixeira
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.menu.btn_clear_scores.rect.center,
        )
        self.menu.handle_events([click_event])

        self.assertEqual(self.menu.highscores, [])
        self.assertEqual(hm.load_scores(), [])

    def test_draw_renders_without_errors(self):
        """Renderização do menu em todos os modos visuais deve ocorrer sem falhas."""
        for mode in ["main", "name_input", "settings", "highscores"]:
            self.menu.view_mode = mode
            self.menu.draw(self.surface)

    def test_keyboard_navigation_main_menu(self):
        """Navegação com setas para baixo/cima e W/S deve alternar o botão selecionado ciclicamente."""
        self.assertEqual(self.menu.selected_menu_index, 0)
        self.assertTrue(self.menu.btn_play.is_selected)
        self.assertFalse(self.menu.btn_highscores.is_selected)

        # Seta para baixo -> RECORDES (índice 1)
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)])
        self.assertEqual(self.menu.selected_menu_index, 1)
        self.assertTrue(self.menu.btn_highscores.is_selected)
        self.assertFalse(self.menu.btn_play.is_selected)

        # Tecla S -> CONFIGURAÇÕES (índice 2)
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)])
        self.assertEqual(self.menu.selected_menu_index, 2)
        self.assertTrue(self.menu.btn_settings.is_selected)

        # Seta para baixo -> SAIR (índice 3)
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)])
        self.assertEqual(self.menu.selected_menu_index, 3)
        self.assertTrue(self.menu.btn_quit.is_selected)

        # Seta para baixo no último -> volta ao primeiro (JOGAR, índice 0)
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)])
        self.assertEqual(self.menu.selected_menu_index, 0)
        self.assertTrue(self.menu.btn_play.is_selected)

        # Seta para cima no primeiro -> vai ao último (SAIR, índice 3)
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)])
        self.assertEqual(self.menu.selected_menu_index, 3)
        self.assertTrue(self.menu.btn_quit.is_selected)

        # Tecla W -> CONFIGURAÇÕES (índice 2)
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)])
        self.assertEqual(self.menu.selected_menu_index, 2)
        self.assertTrue(self.menu.btn_settings.is_selected)

    def test_keyboard_activation_triggers_selected_button(self):
        """Pressionar ENTER ou ESPAÇO aciona o botão selecionado pela navegação."""
        # Navega para CONFIGURAÇÕES (índice 2)
        self.menu.handle_events([
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
        ])
        self.assertEqual(self.menu.selected_menu_index, 2)

        # Pressiona ESPAÇO para acionar CONFIGURAÇÕES
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)])
        self.assertEqual(self.menu.view_mode, "settings")

    def test_button_click_and_selection_animation_states(self):
        """Button deve atualizar timers de animação de clique e seleção e renderizar corretamente."""
        btn = self.menu.btn_play
        btn.is_selected = True
        btn.update(0.1)
        self.assertGreater(btn.selected_anim_time, 0.0)

        # Aciona clique
        btn.trigger_click()
        self.assertGreater(btn.click_anim_time, 0.0)

        # Desenha com ambos os estados ativos
        btn.draw(self.surface)

        # Avança o tempo além da duração do clique
        btn.update(0.2)
        self.assertEqual(btn.click_anim_time, 0.0)

    def test_keyboard_navigation_settings_menu(self):
        """Navegação no modal de configurações com setas e ativação com ENTER."""
        self.menu._open_settings()
        self.assertEqual(self.menu.view_mode, "settings")
        self.assertEqual(self.menu.selected_settings_index, 0)
        self.assertTrue(self.menu.btn_toggle_music.is_selected)

        # Seta para baixo -> Toggle SFX
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)])
        self.assertEqual(self.menu.selected_settings_index, 1)
        self.assertTrue(self.menu.btn_toggle_sfx.is_selected)

        # Seta para baixo -> Voltar
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)])
        self.assertEqual(self.menu.selected_settings_index, 2)
        self.assertTrue(self.menu.btn_close_settings.is_selected)

        # ENTER aciona o botão Voltar, retornando para 'main'
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        self.assertEqual(self.menu.view_mode, "main")


if __name__ == "__main__":
    unittest.main()

