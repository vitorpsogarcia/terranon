from typing import TYPE_CHECKING
import pygame

from core.enums.game_state_enum import GameStateEnum
from core.manager.highscore_manager import HighscoreManager, ScoreEntry
from core.manager.sound_manager import SoundManager
from core.settings.colors import Colors
from core.settings.settings import SCREEN_NAME
from core.states.base_state import GameScene
from core.ui.button import Button
from core.ui.panel import UIPanel
from core.ui.text_input import TextInput

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager
    from core.states.play_state import PlayState


class TitleMenuScene(GameScene):
    """Tela do Menu Principal completa com navegação, highscores e configurações."""

    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(
            state_manager=state_manager,
            screen_size=screen_size,
            is_transparent=False,
            blocks_update=True,
        )

        self.title_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.font = pygame.font.SysFont("Arial", 26)
        self.btn_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.score_font = pygame.font.SysFont("Arial", 17)
        self.score_header_font = pygame.font.SysFont("Arial", 20, bold=True)

        self.play_state: "PlayState | None" = None
        self.highscores: list[ScoreEntry] = []
        self.view_mode: str = "main"  # 'main' | 'name_input' | 'settings' | 'highscores'

        center_x = self.screen_size[0] // 2
        btn_w = 280
        btn_h = 46
        btn_x = center_x - btn_w // 2

        # --- Botões do Menu Principal ---
        self.btn_play = Button(
            rect=pygame.Rect(btn_x, 240, btn_w, btn_h),
            text="JOGAR",
            font=self.btn_font,
            on_click=self._start_name_input,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_highscores = Button(
            rect=pygame.Rect(btn_x, 298, btn_w, btn_h),
            text="RECORDES",
            font=self.btn_font,
            on_click=self._open_highscores,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.brand.primary,
        )

        self.btn_settings = Button(
            rect=pygame.Rect(btn_x, 356, btn_w, btn_h),
            text="CONFIGURAÇÕES / ÁUDIO",
            font=self.btn_font,
            on_click=self._open_settings,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.brand.primary,
        )

        self.btn_quit = Button(
            rect=pygame.Rect(btn_x, 414, btn_w, btn_h),
            text="SAIR",
            font=self.btn_font,
            on_click=self._quit_game,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

        # --- Modal: Captura de Nome do Jogador ---
        modal_w = 420
        modal_h = 240
        modal_x = center_x - modal_w // 2
        modal_y = self.screen_size[1] // 2 - modal_h // 2

        self.name_modal_panel = UIPanel(
            rect=pygame.Rect(modal_x, modal_y, modal_w, modal_h),
            bg_color=Colors.ui.panel,
            border_color=Colors.brand.primary,
            border_width=2,
            border_radius=10,
            title="DIGITE SEU NOME",
            title_font=self.score_header_font,
            title_color=Colors.brand.secondary,
        )

        self.name_input = TextInput(
            rect=pygame.Rect(modal_x + 30, modal_y + 65, modal_w - 60, 48),
            font=self.font,
            placeholder="Nome do Jogador",
            max_length=15,
            on_submit=self._confirm_player_name,
        )

        btn_action_w = 170
        self.btn_confirm_name = Button(
            rect=pygame.Rect(modal_x + 30, modal_y + 135, btn_action_w, 44),
            text="CONFIRMAR",
            font=self.btn_font,
            on_click=lambda: self._confirm_player_name(self.name_input.text),
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_cancel_name = Button(
            rect=pygame.Rect(modal_x + modal_w - 30 - btn_action_w, modal_y + 135, btn_action_w, 44),
            text="VOLTAR",
            font=self.btn_font,
            on_click=self._back_to_main,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

        self.name_modal_panel.add_child(self.name_input)
        self.name_modal_panel.add_child(self.btn_confirm_name)
        self.name_modal_panel.add_child(self.btn_cancel_name)

        # --- Modal: Configurações / Áudio ---
        cfg_w = 440
        cfg_h = 280
        cfg_x = center_x - cfg_w // 2
        cfg_y = self.screen_size[1] // 2 - cfg_h // 2

        self.settings_panel = UIPanel(
            rect=pygame.Rect(cfg_x, cfg_y, cfg_w, cfg_h),
            bg_color=Colors.ui.panel,
            border_color=Colors.brand.primary,
            border_width=2,
            border_radius=10,
            title="CONFIGURAÇÕES DE ÁUDIO",
            title_font=self.score_header_font,
            title_color=Colors.brand.secondary,
        )

        self.btn_toggle_music = Button(
            rect=pygame.Rect(cfg_x + 40, cfg_y + 65, cfg_w - 80, 44),
            text="MÚSICA: LIGADA",
            font=self.btn_font,
            on_click=self._toggle_music,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_toggle_sfx = Button(
            rect=pygame.Rect(cfg_x + 40, cfg_y + 125, cfg_w - 80, 44),
            text="EFEITOS (SFX): LIGADOS",
            font=self.btn_font,
            on_click=self._toggle_sfx,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_close_settings = Button(
            rect=pygame.Rect(cfg_x + 40, cfg_y + 195, cfg_w - 80, 44),
            text="VOLTAR",
            font=self.btn_font,
            on_click=self._back_to_main,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

        self.settings_panel.add_child(self.btn_toggle_music)
        self.settings_panel.add_child(self.btn_toggle_sfx)
        self.settings_panel.add_child(self.btn_close_settings)

        # --- Modal Dedicado de Recordes ---
        hs_w = 460
        hs_h = 420
        hs_x = center_x - hs_w // 2
        hs_y = self.screen_size[1] // 2 - hs_h // 2

        self.highscores_modal_panel = UIPanel(
            rect=pygame.Rect(hs_x, hs_y, hs_w, hs_h),
            bg_color=Colors.ui.panel,
            border_color=Colors.brand.primary,
            border_width=2,
            border_radius=10,
            title="TOP 10 HIGHSCORES",
            title_font=self.score_header_font,
            title_color=Colors.brand.secondary,
        )

        self.btn_close_highscores = Button(
            rect=pygame.Rect(hs_x + 40, hs_y + hs_h - 60, hs_w - 80, 44),
            text="VOLTAR",
            font=self.btn_font,
            on_click=self._back_to_main,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )
        self.highscores_modal_panel.add_child(self.btn_close_highscores)

        # --- Painel Lateral Esquerdo de Highscores (Visível no Menu) ---
        side_x = 30
        side_y = 120
        side_w = 260
        side_h = 460
        self.side_highscores_panel = UIPanel(
            rect=pygame.Rect(side_x, side_y, side_w, side_h),
            bg_color=Colors.ui.panel_transparent,
            border_color=Colors.ui.border,
            border_width=1,
            border_radius=8,
            title="TOP 10 SCORES",
            title_font=self.score_header_font,
            title_color=Colors.brand.secondary,
        )

    def set_play_state(self, play_state: "PlayState"):
        self.play_state = play_state

    def enter(self) -> None:
        self.view_mode = "main"
        self.name_input.text = ""
        self.name_input.is_active = True
        self.highscores = HighscoreManager().get_top_scores(10)
        self._update_sound_button_labels()

    def exit(self) -> None:
        pass

    def _start_name_input(self):
        self.view_mode = "name_input"
        self.name_input.text = ""
        self.name_input.is_active = True

    def _open_highscores(self):
        self.highscores = HighscoreManager().get_top_scores(10)
        self.view_mode = "highscores"

    def _open_settings(self):
        self._update_sound_button_labels()
        self.view_mode = "settings"

    def _back_to_main(self):
        self.view_mode = "main"
        self.name_input.text = ""

    def _confirm_player_name(self, name: str):
        confirmed_name = name.strip() or "Player"
        HighscoreManager().current_player_name = confirmed_name
        if self.play_state is not None:
            self.play_state.player_name = confirmed_name
        self.view_mode = "main"
        self.state_manager.change_to(GameStateEnum.PLAY)

    def _quit_game(self):
        if self.state_manager and self.state_manager.game_manager:
            self.state_manager.game_manager._running = False
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _toggle_music(self):
        sound = SoundManager()
        current_music = sound.volumes.get("music", 1.0)
        if current_music > 0:
            sound.set_volume("music", 0.0)
        else:
            sound.set_volume("music", 1.0)
        self._update_sound_button_labels()

    def _toggle_sfx(self):
        sound = SoundManager()
        current_sfx = sound.volumes.get("sfx", 0.8)
        if current_sfx > 0:
            sound.set_volume("sfx", 0.0)
        else:
            sound.set_volume("sfx", 0.8)
        self._update_sound_button_labels()

    def _update_sound_button_labels(self):
        sound = SoundManager()
        is_music_on = sound.volumes.get("music", 1.0) > 0
        is_sfx_on = sound.volumes.get("sfx", 0.8) > 0

        self.btn_toggle_music.text = f"MÚSICA: {'LIGADA' if is_music_on else 'DESLIGADA'}"
        self.btn_toggle_music.bg_color = (
            Colors.brand.primary if is_music_on else Colors.ui.button_disabled
        )

        self.btn_toggle_sfx.text = f"EFEITOS (SFX): {'LIGADOS' if is_sfx_on else 'DESLIGADOS'}"
        self.btn_toggle_sfx.bg_color = (
            Colors.brand.primary if is_sfx_on else Colors.ui.button_disabled
        )

    def update(self, dt: float) -> None:
        if self.view_mode == "name_input":
            self.name_modal_panel.update(dt)
        elif self.view_mode == "settings":
            self.settings_panel.update(dt)
        elif self.view_mode == "highscores":
            self.highscores_modal_panel.update(dt)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if self.view_mode == "main":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._start_name_input()
                        continue
                    elif event.key == pygame.K_ESCAPE:
                        self._quit_game()
                        continue

                if self.btn_play.handle_event(event):
                    continue
                if self.btn_highscores.handle_event(event):
                    continue
                if self.btn_settings.handle_event(event):
                    continue
                if self.btn_quit.handle_event(event):
                    continue

            elif self.view_mode == "name_input":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._back_to_main()
                    continue
                if self.name_modal_panel.handle_event(event):
                    continue

            elif self.view_mode == "settings":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._back_to_main()
                    continue
                if self.settings_panel.handle_event(event):
                    continue

            elif self.view_mode == "highscores":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._back_to_main()
                    continue
                if self.highscores_modal_panel.handle_event(event):
                    continue

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(Colors.ui.background)

        # Painel lateral de Highscores
        self.side_highscores_panel.draw(surface)
        self._draw_scores_list(
            surface,
            start_x=self.side_highscores_panel.rect.x + 14,
            start_y=self.side_highscores_panel.rect.y + 45,
            width=self.side_highscores_panel.rect.width - 28,
            max_items=10,
        )

        center_x = self.screen_size[0] // 2

        # Título principal do jogo
        title_surf = self.title_font.render(SCREEN_NAME, True, Colors.brand.primary)
        surface.blit(title_surf, (center_x - title_surf.get_width() // 2, 120))

        subtitle_surf = self.small_font.render(
            "Top-Down Action / Base Defense", True, Colors.text.secondary
        )
        surface.blit(subtitle_surf, (center_x - subtitle_surf.get_width() // 2, 185))

        # Botões do menu principal
        self.btn_play.draw(surface)
        self.btn_highscores.draw(surface)
        self.btn_settings.draw(surface)
        self.btn_quit.draw(surface)

        hint_surf = self.small_font.render(
            "Pressione ENTER para Jogar  |  ESC para Sair", True, Colors.text.disabled
        )
        surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, 480))

        # Modais de sobreposição
        if self.view_mode != "main":
            overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            overlay.fill((10, 15, 25, 180))
            surface.blit(overlay, (0, 0))

            if self.view_mode == "name_input":
                self.name_modal_panel.draw(surface)
                hint = self.small_font.render(
                    "ENTER: Confirmar  |  ESC: Voltar", True, Colors.text.secondary
                )
                surface.blit(
                    hint,
                    (center_x - hint.get_width() // 2, self.name_modal_panel.rect.bottom + 12),
                )

            elif self.view_mode == "settings":
                self.settings_panel.draw(surface)

            elif self.view_mode == "highscores":
                self.highscores_modal_panel.draw(surface)
                self._draw_scores_list(
                    surface,
                    start_x=self.highscores_modal_panel.rect.x + 24,
                    start_y=self.highscores_modal_panel.rect.y + 50,
                    width=self.highscores_modal_panel.rect.width - 48,
                    max_items=10,
                )

    def _draw_scores_list(
        self,
        surface: pygame.Surface,
        start_x: int,
        start_y: int,
        width: int,
        max_items: int = 10,
    ) -> None:
        divider_y = start_y - 6
        pygame.draw.line(
            surface,
            Colors.ui.border,
            (start_x, divider_y),
            (start_x + width, divider_y),
            width=1,
        )

        item_height = 26
        curr_y = start_y + 4

        if not self.highscores:
            empty_text = self.score_font.render("Nenhum recorde ainda", True, Colors.text.disabled)
            surface.blit(empty_text, (start_x, curr_y))
            return

        for i, entry in enumerate(self.highscores[:max_items]):
            rank_color = Colors.brand.secondary if i == 0 else Colors.text.primary
            name = entry.get("nome", "Player")
            if len(name) > 12:
                name = name[:11] + "…"
            score = entry.get("score", 0)

            rank_text = f"{i+1}."
            rank_surf = self.score_font.render(rank_text, True, rank_color)
            name_surf = self.score_font.render(name, True, Colors.text.primary)
            score_surf = self.score_font.render(str(score), True, Colors.feedback.info)

            surface.blit(rank_surf, (start_x, curr_y))
            surface.blit(name_surf, (start_x + 24, curr_y))
            score_x = start_x + width - score_surf.get_width()
            surface.blit(score_surf, (score_x, curr_y))

            curr_y += item_height


# Alias para retrocompatibilidade
MenuState = TitleMenuScene
