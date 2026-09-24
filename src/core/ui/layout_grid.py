from collections.abc import Sequence

import pygame

from core.ui.ui_element import UIElement


class GridLayout(UIElement):
    """Organiza elementos filhos em um grid."""

    def __init__(
        self,
        columns: int = 3,
        children: Sequence[UIElement] | None = None,
        spacing: int = 8,
        padding: int = 0,
        rect: pygame.Rect | None = None,
        auto_size: bool = True,
        clip_overflow: bool = True,
    ):
        super().__init__(
            rect or pygame.Rect(0, 0, 0, 0),
            auto_size=auto_size,
            clip_overflow=clip_overflow,
        )
        self.columns = columns
        self.children: list[UIElement] = list(children) if children else []
        self.spacing = spacing
        self.padding = padding
        self.update_layout()

    def get_intrinsic_size(self) -> tuple[int, int]:
        if not self.children:
            return (self.padding * 2, self.padding * 2)

        max_w = 0
        max_h = 0
        for c in self.children:
            w, h = c.get_intrinsic_size()
            max_w = max(max_w, w)
            max_h = max(max_h, h)

        num_rows = (len(self.children) + self.columns - 1) // self.columns

        total_width = (
            self.padding * 2
            + (max_w * self.columns)
            + (self.spacing * (self.columns - 1))
        )
        total_height = (
            self.padding * 2 + (max_h * num_rows) + (self.spacing * (num_rows - 1))
        )

        return (total_width, total_height)

    def update_layout(self):
        if not self.children:
            return

        # Encontra o tamanho máximo de célula
        max_w = 0
        max_h = 0
        for c in self.children:
            w, h = c.get_intrinsic_size()
            max_w = max(max_w, w)
            max_h = max(max_h, h)

        w, h = self.get_intrinsic_size()
        if self.auto_size:
            self.rect.size = (max(self.rect.width, w), max(self.rect.height, h))

        # Posiciona os filhos
        curr_x = self.rect.left + self.padding
        curr_y = self.rect.top + self.padding

        for i, c in enumerate(self.children):
            if i > 0 and i % self.columns == 0:
                curr_x = self.rect.left + self.padding
                curr_y += max_h + self.spacing

            c.rect.size = (max_w, max_h)
            c.rect.topleft = (curr_x, curr_y)
            c.update_layout()

            curr_x += max_w + self.spacing

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            is_hovered = self.rect.collidepoint(event.pos)
            for c in self.children:
                if hasattr(c, "is_hovered"):
                    c.is_hovered = is_hovered

        for c in reversed(self.children):
            if c.visible and c.enabled and c.handle_event(event):
                return True
        return False

    def update(self, dt: float):
        for c in self.children:
            c.update(dt)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        def _draw(surf):
            for c in self.children:
                if c.visible:
                    c.draw(surf)

        self.draw_with_clip(surface, _draw)
