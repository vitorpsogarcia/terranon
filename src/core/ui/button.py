from typing import Callable
import pygame

from core.settings.colors import Colors
from core.ui.ui_element import UIElement


class Button(UIElement):
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        on_click: Callable[[], None] | None = None,
        bg_color: tuple = Colors.ui.button_primary,
        hover_color: tuple = Colors.ui.button_hover,
        text_color: tuple = Colors.text.on_brand,
        border_radius: int = 6,
    ):
        super().__init__(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.is_hovered: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True

        return False

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        current_bg = (
            Colors.ui.button_disabled
            if not self.enabled
            else (self.hover_color if self.is_hovered else self.bg_color)
        )

        pygame.draw.rect(surface, current_bg, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, Colors.ui.border, self.rect, width=1, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_x = self.rect.centerx - text_surf.get_width() // 2
        text_y = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (text_x, text_y))
