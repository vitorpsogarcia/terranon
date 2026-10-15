from typing import TYPE_CHECKING

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.manager.event_manager import EventManager
from core.manager.highscore_manager import HighscoreManager, ScoreEntry
from core.manager.sound_manager import SoundManager
from core.settings.colors import Colors
from core.settings.settings import ASSETS_FOLDER, SCREEN_NAME
from core.states.base_state import GameScene
from core.ui.button import Button
from core.ui.icon_button import IconButton
from core.ui.layout import Column, Row
from core.ui.panel import UIPanel
from core.ui.text_input import TextInput

if TYPE_CHECKING:
    from pathlib import Path
    from core.manager.state_manager import StateManager
    from core.states.play_state import PlayState


class MenuBackgroundVideo:
    """Gerencia a reprodução em loop contínuo do vídeo de fundo do menu."""

    def __init__(self, video_path, fps: float = 30.0):
        self.video_path = video_path
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.timer = 0.0
        self.current_surface: pygame.Surface | None = None
        self._cap = None

    def start(self):
        if not self.video_path.exists():
            return
        try:
            import cv2
            if self._cap is None or not self._cap.isOpened():
                self._cap = cv2.VideoCapture(str(self.video_path))
            if self._cap.isOpened():
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self._read_next_frame(cv2)
        except Exception:
            self._cap = None

    def _read_next_frame(self, cv2_module):
        if self._cap is None or not self._cap.isOpened():
            return
        ret, frame = self._cap.read()
        if not ret or frame is None:
            self._cap.set(cv2_module.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            self.current_surface = pygame.image.frombuffer(frame.tobytes(), (w, h), "BGR")

    def update(self, dt: float):
        if self._cap is None or not self._cap.isOpened():
            return
        self.timer += dt
        if self.timer >= self.frame_interval:
            try:
                import cv2
                steps = int(self.timer / self.frame_interval)
                self.timer -= steps * self.frame_interval
                for _ in range(steps):
                    self._read_next_frame(cv2)
            except Exception:
                pass

    def draw(self, surface: pygame.Surface):
        if self.current_surface is not None:
            surface.blit(self.current_surface, (0, 0))
        else:
            surface.fill(Colors.ui.background)

    def close(self):
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None


class TitleMenuScene(GameScene):
    """Tela do Menu Principal completa com navegação, highscores e configurações."""

    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(
            state_manager=state_manager,
            screen_size=screen_size,
            is_transparent=False,
            blocks_update=True,
        )

        self.title_font = pygame.font.Font("assets/fonts/tiny.ttf", 110)
        self.font = pygame.font.SysFont("Arial", 26)
        self.btn_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.score_font = pygame.font.SysFont("Arial", 17)
        self.score_header_font = pygame.font.SysFont("Arial", 20, bold=True)

        self.play_state: "PlayState | None" = None
        self.highscores: list[ScoreEntry] = []
        self.view_mode: str = (
            "main"  # 'main' | 'name_input' | 'settings' | 'highscores'
        )

        self.bg_video = MenuBackgroundVideo(
            ASSETS_FOLDER / "videos" / "menu_background.mp4"
        )
        self.bg_video.start()

        center_x = self.screen_size[0] // 2
        btn_w = 280
        btn_h = 46

        # --- Botões do Menu Principal ---
        self.btn_play = Button(
            rect=pygame.Rect(0, 0, btn_w, btn_h),
            text="JOGAR",
            font=self.btn_font,
            on_click=self._start_name_input,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.ui.button_hover,
            auto_size=False,
        )

        self.btn_highscores = Button(
            rect=pygame.Rect(0, 0, btn_w, btn_h),
            text="RECORDES",
            font=self.btn_font,
            on_click=self._open_highscores,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.brand.primary,
            auto_size=False,
        )

        self.btn_settings = Button(
            rect=pygame.Rect(0, 0, btn_w, btn_h),
            text="CONFIGURAÇÕES",
            font=self.btn_font,
            on_click=self._open_settings,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.brand.primary,
            auto_size=False,
        )

        self.btn_quit = Button(
            rect=pygame.Rect(0, 0, btn_w, btn_h),
            text="SAIR",
            font=self.btn_font,
            on_click=self._quit_game,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
            auto_size=False,
        )

        self.main_menu_layout = Column(
            children=[
                self.btn_play,
                self.btn_highscores,
                self.btn_settings,
                self.btn_quit,
            ],
            spacing=12,
        )

        # Posiciona a Column no centro da tela com espaçamento adequado abaixo do título
        layout_w, layout_h = self.main_menu_layout.get_intrinsic_size()
        self.main_menu_layout.rect.topleft = (center_x - layout_w // 2, 300)
        self.main_menu_layout.update_layout()

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
            rect=pygame.Rect(0, 0, btn_action_w, 44),
            text="CONFIRMAR",
            font=self.btn_font,
            on_click=lambda: self._confirm_player_name(self.name_input.text),
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
            auto_size=False,
        )

        self.btn_cancel_name = Button(
            rect=pygame.Rect(0, 0, btn_action_w, 44),
            text="VOLTAR",
            font=self.btn_font,
            on_click=self._back_to_main,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
            auto_size=False,
        )

        # O espaçamento = largura total disponivel (modal_w - 60) - 2 * btn_action_w
        space_between = (modal_w - 60) - (2 * btn_action_w)

        self.name_modal_layout = Column(
            spacing=22,
            children=[
                self.name_input,
                Row(
                    spacing=space_between,
                    children=[self.btn_confirm_name, self.btn_cancel_name],
                ),
            ],
        )

        layout_w, layout_h = self.name_modal_layout.get_intrinsic_size()
        self.name_modal_layout.rect.topleft = (modal_x + 30, modal_y + 65)
        self.name_modal_layout.update_layout()

        self.name_modal_panel.add_child(self.name_modal_layout)

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
            rect=pygame.Rect(0, 0, cfg_w - 80, 44),
            text="MÚSICA: LIGADA",
            font=self.btn_font,
            on_click=self._toggle_music,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
            auto_size=False,
        )

        self.btn_toggle_sfx = Button(
            rect=pygame.Rect(0, 0, cfg_w - 80, 44),
            text="EFEITOS (SFX): LIGADOS",
            font=self.btn_font,
            on_click=self._toggle_sfx,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
            auto_size=False,
        )

        self.btn_close_settings = Button(
            rect=pygame.Rect(0, 0, cfg_w - 80, 44),
            text="VOLTAR",
            font=self.btn_font,
            on_click=self._back_to_main,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
            auto_size=False,
        )

        settings_layout = Column(
            spacing=16,
            children=[
                self.btn_toggle_music,
                self.btn_toggle_sfx,
                self.btn_close_settings,
            ],
        )
        settings_layout.rect.topleft = (cfg_x + 40, cfg_y + 65)
        settings_layout.update_layout()

        self.settings_panel.add_child(settings_layout)

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

        # Botão de limpar scores (alinhado à direita da escrita "TOP 10 SCORES")
        trash_btn_size = 26
        trash_btn_x = side_x + side_w - trash_btn_size * 2.25
        trash_btn_y = side_y + 5
        self.btn_clear_scores = IconButton(
            rect=pygame.Rect(trash_btn_x, trash_btn_y, trash_btn_size, trash_btn_size),
            icon_type="trash",
            on_click=self._clear_highscores,
            bg_color=Colors.ui.panel,
            hover_color=Colors.feedback.error,
            icon_color=Colors.text.secondary,
            icon_hover_color=Colors.text.on_brand,
            border_color=Colors.ui.border,
            border_radius=4,
            tooltip="Limpar Recordes",
        )
        self.side_highscores_panel.add_child(self.btn_clear_scores)

        # Listas de botões e índices para navegação por teclado
        self.main_menu_buttons = [
            self.btn_play,
            self.btn_highscores,
            self.btn_settings,
            self.btn_quit,
        ]
        self.selected_menu_index: int = 0

        self.settings_buttons = [
            self.btn_toggle_music,
            self.btn_toggle_sfx,
            self.btn_close_settings,
        ]
        self.selected_settings_index: int = 0

        self.name_modal_buttons = [
            self.btn_confirm_name,
            self.btn_cancel_name,
        ]
        self.selected_name_modal_index: int = -1

        self._update_main_selection()

    def _update_main_selection(self):
        for i, btn in enumerate(self.main_menu_buttons):
            btn.is_selected = (self.view_mode == "main" and i == self.selected_menu_index)

    def _update_settings_selection(self):
        for i, btn in enumerate(self.settings_buttons):
            btn.is_selected = (self.view_mode == "settings" and i == self.selected_settings_index)

    def _update_name_modal_selection(self):
        for i, btn in enumerate(self.name_modal_buttons):
            btn.is_selected = (self.view_mode == "name_input" and i == self.selected_name_modal_index)

    def set_play_state(self, play_state: "PlayState"):
        self.play_state = play_state

    def enter(self) -> None:
        self.view_mode = "main"
        self.name_input.text = ""
        self.name_input.is_active = True
        self.highscores = HighscoreManager().get_top_scores(10)
        self._update_sound_button_labels()
        self.bg_video.start()

        self.selected_menu_index = 0
        self._update_main_selection()

        EventManager().emit(
            GameEventEnum.PLAY_MUSIC,
            filename="Electricity.wav",
            loops=-1,
            fade_ms=1000,
        )

    def exit(self) -> None:
        self.bg_video.close()
        EventManager().emit(GameEventEnum.STOP_MUSIC, fade_ms=500)

    def _start_name_input(self):
        self.view_mode = "name_input"
        self.name_input.text = ""
        self.name_input.is_active = True
        self.selected_name_modal_index = -1
        self._update_name_modal_selection()
        for btn in self.main_menu_buttons:
            btn.is_selected = False

    def _open_highscores(self):
        self.highscores = HighscoreManager().get_top_scores(10)
        self.view_mode = "highscores"
        self.btn_close_highscores.is_selected = True
        for btn in self.main_menu_buttons:
            btn.is_selected = False

    def _clear_highscores(self):
        HighscoreManager().clear_scores()
        self.highscores = []

    def _open_settings(self):
        self._update_sound_button_labels()
        self.view_mode = "settings"
        self.selected_settings_index = 0
        self._update_settings_selection()
        for btn in self.main_menu_buttons:
            btn.is_selected = False

    def _back_to_main(self):
        self.view_mode = "main"
        self.name_input.text = ""
        self.btn_close_highscores.is_selected = False
        for btn in self.settings_buttons:
            btn.is_selected = False
        for btn in self.name_modal_buttons:
            btn.is_selected = False
        self._update_main_selection()

    def _confirm_player_name(self, name: str):
        confirmed_name = name.strip() or "Player"
        HighscoreManager().current_player_name = confirmed_name
        if self.play_state is not None:
            self.play_state.player_name = confirmed_name
        self.view_mode = "main"
        if (
            hasattr(GameStateEnum, "INTRO")
            and hasattr(self.state_manager, "state_factories")
            and GameStateEnum.INTRO.value in self.state_manager.state_factories
        ):
            self.state_manager.change_to(GameStateEnum.INTRO)
        else:
            self.state_manager.change_to(GameStateEnum.PLAY)

    def _quit_game(self):
        if self.state_manager and self.state_manager.game_manager:
            self.state_manager.game_manager._running = False
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _toggle_music(self):
        sound = SoundManager()
        current_music = sound.volumes.get("music", 1.0)
        if current_music > 0:
            self._saved_music_volume = current_music
            sound.set_volume("music", 0.0)
        else:
            restore_vol =getattr(self, "_saved_music_volume", 1.0)
            sound.set_volume("music", restore_vol)
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

        self.btn_toggle_music.text = (
            f"MÚSICA: {'LIGADA' if is_music_on else 'DESLIGADA'}"
        )
        self.btn_toggle_music.bg_color = (
            Colors.brand.primary if is_music_on else Colors.ui.button_disabled
        )
        self.btn_toggle_music.hover_color = (
            Colors.ui.button_hover if is_music_on else Colors.brand.primary
        )

        self.btn_toggle_sfx.text = (
            f"EFEITOS (SFX): {'LIGADOS' if is_sfx_on else 'DESLIGADOS'}"
        )
        self.btn_toggle_sfx.bg_color = (
            Colors.brand.primary if is_sfx_on else Colors.ui.button_disabled
        )
        self.btn_toggle_sfx.hover_color = (
            Colors.ui.button_hover if is_sfx_on else Colors.brand.primary
        )

    def update(self, dt: float) -> None:
        self.bg_video.update(dt)
        if self.view_mode == "main":
            self.side_highscores_panel.update(dt)
            self.main_menu_layout.update(dt)
        elif self.view_mode == "name_input":
            self.name_modal_panel.update(dt)
        elif self.view_mode == "settings":
            self.settings_panel.update(dt)
        elif self.view_mode == "highscores":
            self.highscores_modal_panel.update(dt)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if self.view_mode == "main":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_menu_index = (
                            self.selected_menu_index + 1
                        ) % len(self.main_menu_buttons)
                        self._update_main_selection()
                        continue
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_menu_index = (
                            self.selected_menu_index - 1
                        ) % len(self.main_menu_buttons)
                        self._update_main_selection()
                        continue
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.main_menu_buttons[
                            self.selected_menu_index
                        ].trigger_click()
                        continue
                    elif event.key == pygame.K_ESCAPE:
                        self._quit_game()
                        continue

                elif event.type == pygame.MOUSEMOTION:
                    for i, btn in enumerate(self.main_menu_buttons):
                        if btn.rect.collidepoint(event.pos):
                            if self.selected_menu_index != i:
                                self.selected_menu_index = i
                                self._update_main_selection()
                            break

                if self.side_highscores_panel.handle_event(event):
                    continue
                if self.main_menu_layout.handle_event(event):
                    continue

            elif self.view_mode == "name_input":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._back_to_main()
                        continue
                    elif event.key in (pygame.K_TAB, pygame.K_DOWN):
                        if self.name_input.is_active:
                            self.name_input.is_active = False
                            self.selected_name_modal_index = 0
                            self._update_name_modal_selection()
                            continue
                        elif self.selected_name_modal_index >= 0:
                            self.selected_name_modal_index = (
                                self.selected_name_modal_index + 1
                            ) % len(self.name_modal_buttons)
                            self._update_name_modal_selection()
                            continue
                    elif event.key == pygame.K_UP:
                        if not self.name_input.is_active:
                            self.name_input.is_active = True
                            self.selected_name_modal_index = -1
                            self._update_name_modal_selection()
                            continue
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if not self.name_input.is_active:
                            self.selected_name_modal_index = 0
                            self._update_name_modal_selection()
                            continue
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if not self.name_input.is_active:
                            self.selected_name_modal_index = 1
                            self._update_name_modal_selection()
                            continue
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if (
                            not self.name_input.is_active
                            and self.selected_name_modal_index >= 0
                        ):
                            self.name_modal_buttons[
                                self.selected_name_modal_index
                            ].trigger_click()
                            continue
                        elif self.name_input.is_active and event.key == pygame.K_RETURN:
                            self._confirm_player_name(self.name_input.text)
                            continue

                elif event.type == pygame.MOUSEMOTION:
                    for i, btn in enumerate(self.name_modal_buttons):
                        if btn.rect.collidepoint(event.pos):
                            self.name_input.is_active = False
                            if self.selected_name_modal_index != i:
                                self.selected_name_modal_index = i
                                self._update_name_modal_selection()
                            break

                if self.name_modal_panel.handle_event(event):
                    continue

            elif self.view_mode == "settings":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_settings_index = (
                            self.selected_settings_index + 1
                        ) % len(self.settings_buttons)
                        self._update_settings_selection()
                        continue
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_settings_index = (
                            self.selected_settings_index - 1
                        ) % len(self.settings_buttons)
                        self._update_settings_selection()
                        continue
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.settings_buttons[
                            self.selected_settings_index
                        ].trigger_click()
                        continue
                    elif event.key == pygame.K_ESCAPE:
                        self._back_to_main()
                        continue

                elif event.type == pygame.MOUSEMOTION:
                    for i, btn in enumerate(self.settings_buttons):
                        if btn.rect.collidepoint(event.pos):
                            if self.selected_settings_index != i:
                                self.selected_settings_index = i
                                self._update_settings_selection()
                            break

                if self.settings_panel.handle_event(event):
                    continue

            elif self.view_mode == "highscores":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        self.btn_close_highscores.trigger_click()
                        continue

                if self.highscores_modal_panel.handle_event(event):
                    continue

    def draw(self, surface: pygame.Surface) -> None:
        self.bg_video.draw(surface)

        # # Painel lateral de Highscores
        # self.side_highscores_panel.draw(surface)
        # self._draw_scores_list(
        #     surface,
        #     start_x=self.side_highscores_panel.rect.x + 14,
        #     start_y=self.side_highscores_panel.rect.y + 45,
        #     width=self.side_highscores_panel.rect.width - 28,
        #     max_items=10,
        # )

        center_x = self.screen_size[0] // 2

        main_color = Colors.brand.primary
        dark_color = tuple(max(0, c - 60) for c in main_color)

        text_surf = self.title_font.render(SCREEN_NAME, True, main_color)
        base_x = center_x - text_surf.get_width() // 2
        base_y = 100

        depth = 8
        for i in range(depth, 0, -1):
            layer_surf = self.title_font.render(SCREEN_NAME, True, dark_color)
            surface.blit(layer_surf, (base_x + i, base_y + i))

        

        # 4. Desenhar o texto principal por cima
        surface.blit(text_surf, (base_x, base_y))


        # Botões do menu principal
        self.main_menu_layout.draw(surface)

        hint_surf = self.small_font.render(
            "Pressione ENTER para Jogar  |  ESC para Sair", True, Colors.text.disabled
        )
        surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, 615))

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
                    (
                        center_x - hint.get_width() // 2,
                        self.name_modal_panel.rect.bottom + 12,
                    ),
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
            empty_text = self.score_font.render(
                "Nenhum recorde ainda", True, Colors.text.disabled
            )
            surface.blit(empty_text, (start_x, curr_y))
            return

        for i, entry in enumerate(self.highscores[:max_items]):
            rank_color = Colors.brand.secondary if i == 0 else Colors.text.primary
            name = entry.get("nome", "Player")
            if len(name) > 12:
                name = name[:11] + "…"
            score = entry.get("score", 0)

            rank_text = f"{i + 1}."
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
