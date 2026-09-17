from collections.abc import Sequence

import pygame

from core.ui.ui_element import UIElement


class Row(UIElement):
    """Organiza elementos filhos horizontalmente."""

    def __init__(
        self,
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
        self.children: list[UIElement] = list(children) if children else []
        self.spacing = spacing
        self.padding = padding
        self.update_layout()

    def get_intrinsic_size(self) -> tuple[int, int]:
        if not self.children:
            return (self.padding * 2, self.padding * 2)

        total_width = self.padding * 2 + self.spacing * (len(self.children) - 1)
        max_height = 0

        for c in self.children:
            w, h = c.get_intrinsic_size()
            total_width += w
            max_height = max(max_height, h)

        return (total_width, max_height + self.padding * 2)

    def update_layout(self):
        # Auto-dimensiona para englobar os filhos
        w, h = self.get_intrinsic_size()
        if self.auto_size:
            self.rect.size = (max(self.rect.width, w), max(self.rect.height, h))

        # Posiciona os filhos
        curr_x = self.rect.left + self.padding
        for c in self.children:
            cw, ch = c.get_intrinsic_size()
            c.rect.size = (cw, ch)
            # Centraliza o filho verticalmente dentro da Row
            curr_y = self.rect.centery - ch // 2
            c.rect.topleft = (curr_x, curr_y)

            c.update_layout()
            curr_x += cw + self.spacing

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        # Repassa o is_hovered
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


class Column(UIElement):
    """Organiza elementos filhos verticalmente."""

    def __init__(
        self,
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
        self.children: list[UIElement] = list(children) if children else []
        self.spacing = spacing
        self.padding = padding
        self.update_layout()

    def get_intrinsic_size(self) -> tuple[int, int]:
        if not self.children:
            return (self.padding * 2, self.padding * 2)

        total_height = self.padding * 2 + self.spacing * (len(self.children) - 1)
        max_width = 0

        for c in self.children:
            w, h = c.get_intrinsic_size()
            total_height += h
            max_width = max(max_width, w)

        return (max_width + self.padding * 2, total_height)

    def update_layout(self):
        # Auto-dimensiona para englobar os filhos
        w, h = self.get_intrinsic_size()
        if self.auto_size:
            self.rect.size = (max(self.rect.width, w), max(self.rect.height, h))

        # Posiciona os filhos
        curr_y = self.rect.top + self.padding
        for c in self.children:
            cw, ch = c.get_intrinsic_size()
            c.rect.size = (cw, ch)
            # Centraliza o filho horizontalmente dentro da Column
            curr_x = self.rect.centerx - cw // 2
            c.rect.topleft = (curr_x, curr_y)

            c.update_layout()
            curr_y += ch + self.spacing

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
