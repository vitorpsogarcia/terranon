import pygame

from core.settings.colors import Colors
from core.ui.ui_element import UIElement


class Text(UIElement):
    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        color: pygame.Color = Colors.text.primary,
        hover_color: pygame.Color | None = None,
        rect: pygame.Rect | None = None,
        auto_size: bool = True,
        clip_overflow: bool = True,
    ):
        super().__init__(
            rect or pygame.Rect(0, 0, 0, 0),
            auto_size=auto_size,
            clip_overflow=clip_overflow,
        )
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def get_intrinsic_size(self) -> tuple[int, int]:
        return self.font.size(self.text)

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        current_color = (
            self.hover_color if self.is_hovered and self.hover_color else self.color
        )

        # O text rendering pode falhar se a cor tiver alpha em fontes antigas, mas Colors geralmente é rgb.
        text_surf = self.font.render(self.text, True, current_color)

        text_x = self.rect.centerx - text_surf.get_width() // 2
        text_y = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (text_x, text_y))
