from typing import TYPE_CHECKING

import pygame

from core.enums.game_state_enum import GameStateEnum
from core.manager.highscore_manager import HighscoreManager, ScoreEntry
from core.settings.colors import Colors
from core.settings.settings import SCREEN_NAME
from core.states.base_state import BaseState

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager
    from core.states.play_state import PlayState


class MenuState(BaseState):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)

        self.title_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.score_font = pygame.font.SysFont("Arial", 18)
        self.score_header_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.play_state: "PlayState | None" = None
        self.highscores: list[ScoreEntry] = []
        self.is_typing_name: bool = False
        self.player_name_input: str = ""
        self.cursor_timer: float = 0.0
        self.cursor_visible: bool = True
        self.max_name_length: int = 15

    def set_play_state(self, play_state: "PlayState"):
        self.play_state = play_state

    def enter(self):
        self.is_typing_name = False
        self.player_name_input = ""
        self.cursor_timer = 0.0
        self.cursor_visible = True
        self.highscores = HighscoreManager().get_top_scores(10)

    def exit(self):
        pass

    def update(self, delta_time: float):
        if self.is_typing_name:
            self.cursor_timer += delta_time
            if self.cursor_timer >= 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0.0

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if not self.is_typing_name:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.is_typing_name = True
                    self.player_name_input = ""
                    self.cursor_timer = 0.0
                    self.cursor_visible = True
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        confirmed_name = self.player_name_input.strip() or "Player"
                        HighscoreManager().current_player_name = confirmed_name
                        if self.play_state is not None:
                            self.play_state.player_name = confirmed_name
                        self.is_typing_name = False
                        self.state_manager.change_to(GameStateEnum.PLAY)
                    elif event.key == pygame.K_ESCAPE:
                        self.is_typing_name = False
                        self.player_name_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name_input = self.player_name_input[:-1]
                    else:
                        if len(self.player_name_input) < self.max_name_length and event.unicode.isprintable():
                            self.player_name_input += event.unicode

    def draw(self, surface: pygame.Surface):
        surface.fill(Colors.ui.background)

        self._draw_highscores(surface)

        if not self.is_typing_name:
            self._draw_main_menu(surface)
        else:
            self._draw_name_input(surface)

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
                # Alinha a pontuação à direita
                score_x = padding_x + box_width - 12 - score_surf.get_width()
                surface.blit(score_surf, (score_x, curr_y))

                curr_y += item_height

    def _draw_main_menu(self, surface: pygame.Surface):
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        title_surf = self.title_font.render(SCREEN_NAME, True, Colors.brand.primary)
        instruction_surf = self.font.render("Press Enter to Start", True, Colors.text.primary)

        surface.blit(
            title_surf,
            (center_x - title_surf.get_width() // 2, center_y - 80),
        )
        surface.blit(
            instruction_surf,
            (center_x - instruction_surf.get_width() // 2, center_y + 10),
        )

    def _draw_name_input(self, surface: pygame.Surface):
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        prompt_surf = self.font.render("Digite seu nome:", True, Colors.text.primary)
        surface.blit(prompt_surf, (center_x - prompt_surf.get_width() // 2, center_y - 70))

        input_box_w = 340
        input_box_h = 48
        box_rect = pygame.Rect(
            center_x - input_box_w // 2,
            center_y - 10,
            input_box_w,
            input_box_h,
        )
        pygame.draw.rect(surface, Colors.ui.panel, box_rect, border_radius=6)
        pygame.draw.rect(surface, Colors.brand.primary, box_rect, width=2, border_radius=6)

        display_text = self.player_name_input
        name_surf = self.font.render(display_text, True, Colors.text.on_brand)
        name_x = box_rect.x + 14
        name_y = box_rect.centery - name_surf.get_height() // 2
        surface.blit(name_surf, (name_x, name_y))

        if self.cursor_visible:
            cursor_x = name_x + name_surf.get_width() + 3
            cursor_y_start = box_rect.y + 8
            cursor_y_end = box_rect.bottom - 8
            pygame.draw.line(
                surface,
                Colors.brand.secondary,
                (cursor_x, cursor_y_start),
                (cursor_x, cursor_y_end),
                width=2,
            )

        help_surf = self.small_font.render(
            "Pressione ENTER para Confirmar  |  ESC para Voltar",
            True,
            Colors.text.secondary,
        )
        surface.blit(
            help_surf,
            (center_x - help_surf.get_width() // 2, center_y + 60),
        )
