from collections.abc import Callable, Sequence

import pygame

from core.settings.colors import Colors
from core.ui.text import Text
from core.ui.ui_element import UIElement


class Button(UIElement):
    def __init__(
        self,
        rect: pygame.Rect,
        text: str = "",
        font: pygame.font.Font | None = None,
        on_click: Callable[[], None] | None = None,
        bg_color: tuple = Colors.ui.button_primary,
        hover_color: tuple = Colors.ui.button_hover,
        text_color: tuple = Colors.text.on_brand,
        border_color: tuple | None = Colors.ui.border,
        border_hover_color: tuple | None = None,
        border_radius: int = 6,
        child: UIElement | None = None,
        children: Sequence[UIElement] | None = None,
        tooltip: str | None = None,
        auto_size: bool = True,
        clip_overflow: bool = True,
    ):
        super().__init__(rect, auto_size=auto_size, clip_overflow=clip_overflow)
        self.on_click = on_click
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_hover_color = border_hover_color
        self.border_radius = border_radius
        self.is_hovered: bool = False
        self.tooltip = tooltip

        self.children: list[UIElement] = list(children) if children else []
        if child:
            self.children.append(child)

        if text and font:
            self.children.append(
                Text(
                    text=text,
                    font=font,
                    color=text_color,
                )
            )

        self.update_layout()

    def get_intrinsic_size(self) -> tuple[int, int]:
        if not self.children:
            return self.rect.size

        max_w, max_h = 0, 0
        for c in self.children:
            cw, ch = c.get_intrinsic_size()
            max_w = max(max_w, cw)
            max_h = max(max_h, ch)

        padding_x, padding_y = 32, 16
        return (
            max(self.rect.width, max_w + padding_x),
            max(self.rect.height, max_h + padding_y),
        )

    def update_layout(self):
        iw, ih = self.get_intrinsic_size()
        if self.auto_size:
            self.rect.size = (max(self.rect.width, iw), max(self.rect.height, ih))
        self._update_children_rects()

    def _update_children_rects(self):
        for c in self.children:
            cw, ch = c.get_intrinsic_size()
            c.rect.size = (cw, ch)
            c.rect.center = self.rect.center
            c.update_layout()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            for c in self.children:
                if hasattr(c, "is_hovered"):
                    c.is_hovered = self.is_hovered

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True

        return False

    def update(self, dt: float):
        self._update_children_rects()
        for c in self.children:
            c.update(dt)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        current_bg = (
            Colors.ui.button_disabled
            if not self.enabled
            else (self.hover_color if self.is_hovered else self.bg_color)
        )

        has_alpha = len(current_bg) == 4 and current_bg[3] < 255
        if has_alpha:
            btn_surf = pygame.Surface(
                (self.rect.width, self.rect.height), pygame.SRCALPHA
            )
            btn_surf.fill(current_bg)
            surface.blit(btn_surf, self.rect.topleft)
        else:
            pygame.draw.rect(
                surface, current_bg, self.rect, border_radius=self.border_radius
            )

        if self.border_color:
            border_c = (
                self.border_hover_color
                if self.is_hovered and self.border_hover_color
                else self.border_color
            )
            pygame.draw.rect(
                surface, border_c, self.rect, width=1, border_radius=self.border_radius
            )

        def _draw_children(surf):
            for c in self.children:
                if c.visible:
                    c.draw(surf)

        self.draw_with_clip(surface, _draw_children)
