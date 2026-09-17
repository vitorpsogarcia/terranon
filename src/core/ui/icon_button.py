from typing import Callable
import pygame

from core.settings.colors import Colors
from core.ui.button import Button


class IconButton(Button):
    """Botão compacto para exibição de ícones gráficos (ex: lixeira)."""

    def __init__(
        self,
        rect: pygame.Rect,
        icon_type: str = "trash",
        on_click: Callable[[], None] | None = None,
        bg_color: tuple = Colors.ui.button_disabled,
        hover_color: tuple = Colors.feedback.error,
        icon_color: tuple = Colors.text.primary,
        icon_hover_color: tuple = Colors.text.on_brand,
        border_color: tuple = Colors.ui.border,
        border_radius: int = 4,
        tooltip: str | None = None,
    ):
        # Inicializa a classe base Button sem texto
        super().__init__(
            rect=rect,
            text="",
            font=None,  # type: ignore
            on_click=on_click,
            bg_color=bg_color,
            hover_color=hover_color,
            border_radius=border_radius,
        )
        self.icon_type = icon_type
        self.icon_color = icon_color
        self.icon_hover_color = icon_hover_color
        self.border_color = border_color
        self.tooltip = tooltip

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        current_bg = (
            Colors.ui.button_disabled
            if not self.enabled
            else (self.hover_color if self.is_hovered else self.bg_color)
        )
        current_icon_color = (
            Colors.text.disabled
            if not self.enabled
            else (self.icon_hover_color if self.is_hovered else self.icon_color)
        )

        # Fundo
        has_alpha = len(current_bg) == 4 and current_bg[3] < 255
        if has_alpha:
            btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            btn_surf.fill(current_bg)
            surface.blit(btn_surf, self.rect.topleft)
        else:
            pygame.draw.rect(surface, current_bg, self.rect, border_radius=self.border_radius)

        # Borda
        if self.border_color:
            border_c = self.hover_color if self.is_hovered else self.border_color
            pygame.draw.rect(surface, border_c, self.rect, width=1, border_radius=self.border_radius)

        # Renderização do ícone
        if self.icon_type == "trash":
            self._draw_trash_icon(surface, current_icon_color)

    def _draw_trash_icon(self, surface: pygame.Surface, color: tuple) -> None:
        """Desenha um ícone vetorial de lixeira centralizado no botão."""
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

