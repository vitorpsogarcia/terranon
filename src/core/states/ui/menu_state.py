from typing import TYPE_CHECKING
import pygame

from core.enums.game_state_enum import GameStateEnum
from core.manager.highscore_manager import HighscoreManager, ScoreEntry
from core.settings.colors import Colors
from core.settings.settings import SCREEN_NAME
from core.states.base_state import GameScene
from core.ui.button import Button
from core.ui.text_input import TextInput

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager
    from core.states.play_state import PlayState


class MenuState(GameScene):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)

        self.title_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.score_font = pygame.font.SysFont("Arial", 18)
        self.score_header_font = pygame.font.SysFont("Arial", 20, bold=True)

        self.play_state: "PlayState | None" = None
        self.highscores: list[ScoreEntry] = []
        self.is_typing_name: bool = False

        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        self.btn_play = Button(
            rect=pygame.Rect(center_x - 120, center_y - 10, 240, 50),
            text="JOGAR",
            font=self.font,
            on_click=self._start_name_input,
        )

        self.btn_quit = Button(
            rect=pygame.Rect(center_x - 120, center_y + 55, 240, 50),
            text="SAIR",
            font=self.font,
            on_click=self._quit_game,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

        self.name_input = TextInput(
            rect=pygame.Rect(center_x - 170, center_y - 10, 340, 50),
            font=self.font,
            placeholder="Nome do Jogador",
            max_length=15,
            on_submit=self._confirm_player_name,
        )

        self.btn_confirm = Button(
            rect=pygame.Rect(center_x - 170, center_y + 55, 160, 44),
            text="CONFIRMAR",
            font=self.small_font,
            on_click=lambda: self._confirm_player_name(self.name_input.text),
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_cancel = Button(
            rect=pygame.Rect(center_x + 10, center_y + 55, 160, 44),
            text="VOLTAR",
            font=self.small_font,
            on_click=self._cancel_name_input,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

    def set_play_state(self, play_state: "PlayState"):
        self.play_state = play_state

    def enter(self):
        self.is_typing_name = False
        self.name_input.text = ""
        self.name_input.is_active = True
        self.highscores = HighscoreManager().get_top_scores(10)

    def exit(self):
        pass

    def _start_name_input(self):
        self.is_typing_name = True
        self.name_input.text = ""
        self.name_input.is_active = True

    def _cancel_name_input(self):
        self.is_typing_name = False
        self.name_input.text = ""

    def _confirm_player_name(self, name: str):
        confirmed_name = name.strip() or "Player"
        HighscoreManager().current_player_name = confirmed_name
        if self.play_state is not None:
            self.play_state.player_name = confirmed_name
        self.is_typing_name = False
        self.state_manager.change_to(GameStateEnum.PLAY)

    def _quit_game(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float):
        if self.is_typing_name:
            self.name_input.update(dt)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if not self.is_typing_name:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self._start_name_input()
                    continue

                if self.btn_play.handle_event(event):
                    continue
                if self.btn_quit.handle_event(event):
                    continue
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._cancel_name_input()
                    continue

                if self.name_input.handle_event(event):
                    continue
                if self.btn_confirm.handle_event(event):
                    continue
                if self.btn_cancel.handle_event(event):
                    continue

    def draw(self, surface: pygame.Surface):
        surface.fill(Colors.ui.background)
        self._draw_highscores(surface)

        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        title_surf = self.title_font.render(SCREEN_NAME, True, Colors.brand.primary)
        surface.blit(title_surf, (center_x - title_surf.get_width() // 2, center_y - 120))

        if not self.is_typing_name:
            self.btn_play.draw(surface)
            self.btn_quit.draw(surface)
            hint_surf = self.small_font.render("Pressione ENTER para Jogar", True, Colors.text.secondary)
            surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, center_y + 125))
        else:
            prompt_surf = self.font.render("Digite seu nome:", True, Colors.text.primary)
            surface.blit(prompt_surf, (center_x - prompt_surf.get_width() // 2, center_y - 60))

            self.name_input.draw(surface)
            self.btn_confirm.draw(surface)
            self.btn_cancel.draw(surface)

            help_surf = self.small_font.render("ENTER: Confirmar  |  ESC: Voltar", True, Colors.text.secondary)
            surface.blit(help_surf, (center_x - help_surf.get_width() // 2, center_y + 115))

    def _draw_highscores(self, surface: pygame.Surface):
        padding_x = 24
        padding_y = 20
        box_width = 250
        header_height = 32
        item_height = 24
        total_items = max(len(self.highscores), 1)
        box_height = header_height + (total_items * item_height) + 16

        panel_rect = pygame.Rect(padding_x, padding_y, box_width, box_height)
        panel_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        panel_surface.fill(Colors.ui.panel_transparent)
        surface.blit(panel_surface, (padding_x, padding_y))
        pygame.draw.rect(surface, Colors.ui.border, panel_rect, width=1, border_radius=6)

        header_surf = self.score_header_font.render("TOP 10 SCORES", True, Colors.brand.secondary)
        surface.blit(header_surf, (padding_x + 12, padding_y + 8))

        line_y = padding_y + header_height
        pygame.draw.line(surface, Colors.ui.border, (padding_x + 10, line_y), (padding_x + box_width - 10, line_y))

        curr_y = line_y + 8
        if not self.highscores:
            empty_text = self.score_font.render("Nenhum recorde ainda", True, Colors.text.disabled)
            surface.blit(empty_text, (padding_x + 12, curr_y))
        else:
            for i, entry in enumerate(self.highscores):
                rank_color = Colors.brand.secondary if i == 0 else Colors.text.primary
                name = entry.get("nome", "Player")
                if len(name) > 12:
                    name = name[:11] + "…"
                score = entry.get("score", 0)

                rank_text = f"{i+1}."
                rank_surf = self.score_font.render(rank_text, True, rank_color)
                name_surf = self.score_font.render(name, True, Colors.text.primary)
                score_surf = self.score_font.render(str(score), True, Colors.feedback.info)

                surface.blit(rank_surf, (padding_x + 12, curr_y))
                surface.blit(name_surf, (padding_x + 36, curr_y))
                score_x = padding_x + box_width - 12 - score_surf.get_width()
                surface.blit(score_surf, (score_x, curr_y))

                curr_y += item_height
