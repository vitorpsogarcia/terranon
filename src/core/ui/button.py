from collections.abc import Callable, Sequence
import math

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
        bg_color: pygame.Color | None = Colors.ui.button_primary,
        hover_color: pygame.Color | None = Colors.ui.button_hover,
        text_color: pygame.Color = Colors.text.on_brand,
        text_hover_color: pygame.Color | None = None,
        border_color: pygame.Color | None = Colors.ui.border,
        border_hover_color: pygame.Color | None = None,
        border_radius: int = 6,
        bottom_line_only: bool = False,
        bottom_line_width: int = 2,
        text_align: str = "center",
        padding_x: int = 16,
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
        self._text_color = text_color
        self.text_hover_color = text_hover_color
        self.border_color = border_color
        self.border_hover_color = border_hover_color
        self.border_radius = border_radius
        self.bottom_line_only = bottom_line_only
        self.bottom_line_width = bottom_line_width
        self.text_align = text_align
        self.padding_x = padding_x
        self.is_hovered: bool = False
        self.is_selected: bool = False
        self.selected_anim_time: float = 0.0
        self.click_anim_time: float = 0.0
        self.click_anim_duration: float = 0.16
        self.tooltip = tooltip

        self._text = text
        self.font = font
        self._text_child: Text | None = None

        self.children: list[UIElement] = list(children) if children else []
        if child:
            self.children.append(child)

        if text and font:
            self._text_child = Text(
                text=text,
                font=font,
                color=text_color,
            )
            self.children.append(self._text_child)

        self.update_layout()

    @property
    def text_color(self) -> pygame.Color:
        return self._text_color

    @text_color.setter
    def text_color(self, new_color: pygame.Color):
        self._text_color = new_color
        if self._text_child is not None and not (self.is_hovered and self.text_hover_color):
            self._text_child.color = new_color

    @property
    def text(self) -> str:
        if self._text_child is not None:
            return self._text_child.text
        for c in self.children:
            if isinstance(c, Text):
                return c.text
        return getattr(self, "_text", "")

    @text.setter
    def text(self, new_text: str):
        self._text = new_text
        if self._text_child is not None:
            self._text_child.text = new_text
            self.update_layout()
            return

        for c in self.children:
            if isinstance(c, Text):
                c.text = new_text
                self.update_layout()
                return

        if getattr(self, "font", None) is not None:
            self._text_child = Text(
                text=new_text,
                font=self.font,
                color=getattr(self, "text_color", Colors.text.on_brand),
            )
            self.children.append(self._text_child)
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

    def trigger_click(self) -> bool:
        """Aciona o clique do botão com animação de pressão e executa o callback on_click."""
        if not self.visible or not self.enabled:
            return False
        self.click_anim_time = self.click_anim_duration
        self._update_children_rects()
        if self.on_click:
            self.on_click()
        return True

    def _update_children_rects(self):
        click_ratio = (
            (self.click_anim_time / self.click_anim_duration)
            if self.click_anim_duration > 0
            else 0.0
        )
        press_offset_y = int(3 * click_ratio)
        center_x = self.rect.centerx
        center_y = self.rect.centery + press_offset_y

        for c in self.children:
            cw, ch = c.get_intrinsic_size()
            c.rect.size = (cw, ch)
            if self.text_align == "left":
                c.rect.left = self.rect.left + self.padding_x
                c.rect.centery = center_y
            elif self.text_align == "right":
                c.rect.right = self.rect.right - self.padding_x
                c.rect.centery = center_y
            else:
                c.rect.center = (center_x, center_y)
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
                return self.trigger_click()

        return False

    def update(self, dt: float):
        if self.is_selected or self.is_hovered:
            self.selected_anim_time += dt
        else:
            self.selected_anim_time = 0.0

        if self.click_anim_time > 0:
            self.click_anim_time = max(0.0, self.click_anim_time - dt)

        self._update_children_rects()
        for c in self.children:
            c.update(dt)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        click_ratio = (
            (self.click_anim_time / self.click_anim_duration)
            if self.click_anim_duration > 0
            else 0.0
        )
        press_offset_y = int(3 * click_ratio)
        draw_rect = self.rect.move(0, press_offset_y)

        is_active = self.enabled and (self.is_selected or self.is_hovered)
        current_bg = (
            Colors.ui.button_disabled
            if not self.enabled
            else (
                self.hover_color
                if (is_active and self.hover_color is not None)
                else self.bg_color
            )
        )

        if current_bg is not None:
            has_alpha = len(current_bg) == 4 and current_bg[3] < 255
            if has_alpha:
                if current_bg[3] > 0:
                    btn_surf = pygame.Surface(
                        (draw_rect.width, draw_rect.height), pygame.SRCALPHA
                    )
                    pygame.draw.rect(
                        btn_surf, current_bg, btn_surf.get_rect(), border_radius=self.border_radius
                    )
                    surface.blit(btn_surf, draw_rect.topleft)
            else:
                pygame.draw.rect(
                    surface, current_bg, draw_rect, border_radius=self.border_radius
                )

        # Animação de clique: flash branco/ciano translúcido
        if click_ratio > 0:
            flash_alpha = int(140 * click_ratio)
            flash_surf = pygame.Surface(
                (draw_rect.width, draw_rect.height), pygame.SRCALPHA
            )
            flash_surf.fill((255, 255, 255, flash_alpha))
            surface.blit(flash_surf, draw_rect.topleft)

        # Borda: linha inferior para bottom_line_only ou retângulo com pulso se selecionado/hover
        if self.bottom_line_only:
            line_c = (
                self.border_hover_color
                if is_active and self.border_hover_color
                else self.border_color
            )
            if line_c:
                line_rect = pygame.Rect(
                    draw_rect.left,
                    draw_rect.bottom - self.bottom_line_width,
                    draw_rect.width,
                    self.bottom_line_width,
                )
                pygame.draw.rect(surface, line_c, line_rect)
        elif self.border_color or is_active:
            if is_active:
                pulse = (math.sin(self.selected_anim_time * 8.0) + 1.0) / 2.0
                c1 = Colors.brand.primary
                c2 = Colors.brand.secondary
                border_c = (
                    int(c1[0] * (1.0 - pulse) + c2[0] * pulse),
                    int(c1[1] * (1.0 - pulse) + c2[1] * pulse),
                    int(c1[2] * (1.0 - pulse) + c2[2] * pulse),
                )
                border_w = 2
            else:
                border_c = (
                    self.border_hover_color
                    if self.is_hovered and self.border_hover_color
                    else self.border_color
                )
                border_w = 1

            if border_c:
                pygame.draw.rect(
                    surface, border_c, draw_rect, width=border_w, border_radius=self.border_radius
                )

        # Animação de botão selecionado: chevrons arcade dinâmicos (► e ◄)
        if self.is_selected and self.enabled and not self.bottom_line_only:
            pulse = math.sin(self.selected_anim_time * 8.0)
            bounce = int(3.0 * pulse)
            chevron_color = Colors.brand.secondary
            cy = draw_rect.centery

            # Chevron esquerdo ►
            lx = draw_rect.left - 14 - bounce
            pygame.draw.polygon(
                surface,
                chevron_color,
                [(lx - 5, cy - 6), (lx + 3, cy), (lx - 5, cy + 6)],
            )

            # Chevron direito ◄
            rx = draw_rect.right + 14 + bounce
            pygame.draw.polygon(
                surface,
                chevron_color,
                [(rx + 5, cy - 6), (rx - 3, cy), (rx + 5, cy + 6)],
            )

        if self._text_child is not None and self.text_hover_color is not None:
            self._text_child.color = (
                self.text_hover_color
                if (self.is_hovered and self.enabled)
                else self.text_color
            )

        def _draw_children(surf):
            for c in self.children:
                if c.visible:
                    c.draw(surf)

        self.draw_with_clip(surface, _draw_children)
