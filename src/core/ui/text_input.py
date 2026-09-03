from typing import Callable
import pygame

from core.settings.colors import Colors
from core.ui.ui_element import UIElement


class TextInput(UIElement):
    def __init__(
        self,
        rect: pygame.Rect,
        font: pygame.font.Font,
        placeholder: str = "",
        max_length: int = 15,
        on_submit: Callable[[str], None] | None = None,
        bg_color: tuple = Colors.ui.panel,
        active_border: tuple = Colors.brand.primary,
        inactive_border: tuple = Colors.ui.border,
        text_color: tuple = Colors.text.on_brand,
        border_radius: int = 6,
    ):
        super().__init__(rect)
        self.font = font
        self.placeholder = placeholder
        self.max_length = max_length
        self.on_submit = on_submit
        self.bg_color = bg_color
        self.active_border = active_border
        self.inactive_border = inactive_border
        self.text_color = text_color
        self.border_radius = border_radius

        self.text: str = ""
        self.is_active: bool = True
        self.cursor_timer: float = 0.0
        self.cursor_visible: bool = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.rect.collidepoint(event.pos)
            return self.is_active

        if self.is_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.on_submit:
                    self.on_submit(self.text)
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
                return True

        return False

    def update(self, dt: float):
        if not self.is_active:
            self.cursor_visible = False
            return

        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        border_color = self.active_border if self.is_active else self.inactive_border
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=self.border_radius)

        display_text = self.text if self.text else (self.placeholder if not self.is_active else "")
        display_color = self.text_color if self.text else Colors.text.disabled

        text_surf = self.font.render(display_text, True, display_color)
        text_x = self.rect.x + 14
        text_y = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (text_x, text_y))

        if self.is_active and self.cursor_visible:
            cursor_offset = self.font.size(self.text)[0] if self.text else 0
            cursor_x = text_x + cursor_offset + 2
            cursor_y_start = self.rect.y + 8
            cursor_y_end = self.rect.bottom - 8
            pygame.draw.line(
                surface,
                Colors.brand.secondary,
                (cursor_x, cursor_y_start),
                (cursor_x, cursor_y_end),
                width=2,
            )
