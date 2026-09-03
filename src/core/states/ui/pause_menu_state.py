from typing import TYPE_CHECKING
import pygame

from core.enums.game_state_enum import GameStateEnum
from core.settings.colors import Colors
from core.states.base_state import GameScene
from core.ui.button import Button

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager


class PauseMenuState(GameScene):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.btn_font = pygame.font.SysFont("Arial", 24)

        self.is_transparent = True
        self.blocks_update = True

        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        self.btn_resume = Button(
            rect=pygame.Rect(center_x - 130, center_y - 30, 260, 48),
            text="CONTINUAR",
            font=self.btn_font,
            on_click=self._resume,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_restart = Button(
            rect=pygame.Rect(center_x - 130, center_y + 30, 260, 48),
            text="REINICIAR",
            font=self.btn_font,
            on_click=self._restart,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_menu = Button(
            rect=pygame.Rect(center_x - 130, center_y + 90, 260, 48),
            text="MENU PRINCIPAL",
            font=self.btn_font,
            on_click=self._go_to_menu,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

    def _resume(self):
        self.state_manager.pop()

    def _restart(self):
        self.state_manager.change_to(GameStateEnum.PLAY)

    def _go_to_menu(self):
        self.state_manager.change_to(GameStateEnum.MENU)

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, dt: float):
        pass

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._resume()
                return

            if self.btn_resume.handle_event(event):
                return
            if self.btn_restart.handle_event(event):
                return
            if self.btn_menu.handle_event(event):
                return

    def draw(self, surface: pygame.Surface):
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill(Colors.ui.panel_transparent)
        surface.blit(overlay, (0, 0))

        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        panel_w = 340
        panel_h = 320
        panel_rect = pygame.Rect(center_x - panel_w // 2, center_y - 170, panel_w, panel_h)
        pygame.draw.rect(surface, Colors.ui.panel, panel_rect, border_radius=10)
        pygame.draw.rect(surface, Colors.ui.border, panel_rect, width=2, border_radius=10)

        title_surf = self.title_font.render("PAUSA", True, Colors.text.primary)
        surface.blit(title_surf, (center_x - title_surf.get_width() // 2, panel_rect.y + 24))

        self.btn_resume.draw(surface)
        self.btn_restart.draw(surface)
        self.btn_menu.draw(surface)
