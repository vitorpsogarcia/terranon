import pygame

from core.settings.colors import Colors
from core.ui.ui_element import UIElement


class Icon(UIElement):
    def __init__(
        self,
        icon_type: str = "trash",
        color: tuple = Colors.text.primary,
        hover_color: tuple | None = None,
        rect: pygame.Rect | None = None,
        auto_size: bool = True,
        clip_overflow: bool = True,
    ):
        super().__init__(
            rect or pygame.Rect(0, 0, 0, 0),
            auto_size=auto_size,
            clip_overflow=clip_overflow,
        )
        self.icon_type = icon_type
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def get_intrinsic_size(self) -> tuple[int, int]:
        if self.icon_type == "trash":
            return (16, 16)
        return (16, 16)  # Default genérico para ícones simples

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

        if self.icon_type == "trash":
            self._draw_trash_icon(surface, current_color)

    def _draw_trash_icon(self, surface: pygame.Surface, color: tuple) -> None:
        cx = self.rect.centerx
        cy = self.rect.centery

        # Alça da tampa (topo)
        pygame.draw.rect(surface, color, (cx - 3, cy - 7, 6, 2), border_radius=1)

        # Barra da tampa (horizontal)
        pygame.draw.rect(surface, color, (cx - 7, cy - 5, 14, 2), border_radius=1)

        # Cesto da lixeira (corpo)
        body_rect = pygame.Rect(cx - 5, cy - 3, 11, 10)
        pygame.draw.rect(surface, color, body_rect, width=1, border_radius=2)

        # Nervuras verticais internas
        pygame.draw.line(surface, color, (cx - 2, cy - 1), (cx - 2, cy + 4), width=1)
        pygame.draw.line(surface, color, (cx + 2, cy - 1), (cx + 2, cy + 4), width=1)
