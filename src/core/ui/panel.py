from collections.abc import Sequence

import pygame

from core.settings.colors import Colors
from core.ui.ui_element import UIElement


class UIPanel(UIElement):
    """Contêiner visual para agrupar e organizar elementos de interface gráfica."""

    def __init__(
        self,
        rect: pygame.Rect,
        bg_color: pygame.Color = Colors.ui.panel,
        border_color: pygame.Color = Colors.ui.border,
        border_width: int = 1,
        border_radius: int = 8,
        title: str | None = None,
        title_font: pygame.font.Font | None = None,
        title_color: pygame.Color = Colors.text.primary,
        consume_clicks: bool = True,
        children: Sequence[UIElement] | None = None,
        auto_size: bool = False,  # Panels are usually fixed size by default
        clip_overflow: bool = True,
    ):
        super().__init__(rect, auto_size=auto_size, clip_overflow=clip_overflow)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.title = title
        self.title_font = title_font
        self.title_color = title_color
        self.consume_clicks = consume_clicks
        self.children: list[UIElement] = list(children) if children else []

    def add_child(self, element: UIElement) -> UIElement:
        """Adiciona um elemento filho ao painel."""
        if element not in self.children:
            self.children.append(element)
        return element

    def remove_child(self, element: UIElement) -> None:
        """Remove um elemento filho do painel se presente."""
        if element in self.children:
            self.children.remove(element)

    def clear_children(self) -> None:
        """Remove todos os elementos filhos do painel."""
        self.children.clear()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Propaga eventos para os elementos filhos (ordem inversa) e consome cliques internos."""
        if not self.visible or not self.enabled:
            return False

        # Propaga para os filhos primeiro (do topo para baixo)
        for child in reversed(self.children):
            if child.visible and child.enabled:
                if child.handle_event(event):
                    return True

        # Se for clique do mouse dentro do painel, consome para não vazar
        if self.consume_clicks and event.type == pygame.MOUSEBUTTONDOWN:
            if hasattr(event, "pos") and self.rect.collidepoint(event.pos):
                return True

        return False

    def update(self, dt: float) -> None:
        """Atualiza todos os filhos do painel."""
        if not self.visible or not self.enabled:
            return

        for child in self.children:
            if child.visible and child.enabled:
                child.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza o painel, título e seus elementos filhos."""
        if not self.visible:
            return

        # Desenhar fundo (com suporte a transparência se houver canal alpha)
        has_alpha = len(self.bg_color) == 4 and self.bg_color[3] < 255
        if has_alpha:
            panel_surface = pygame.Surface(
                (self.rect.width, self.rect.height), pygame.SRCALPHA
            )
            panel_surface.fill(self.bg_color)
            surface.blit(panel_surface, self.rect.topleft)
        else:
            pygame.draw.rect(
                surface, self.bg_color, self.rect, border_radius=self.border_radius
            )

        # Desenhar borda
        if self.border_width > 0 and self.border_color:
            pygame.draw.rect(
                surface,
                self.border_color,
                self.rect,
                width=self.border_width,
                border_radius=self.border_radius,
            )

        # Desenhar título se configurado
        if self.title and self.title_font:
            title_surf = self.title_font.render(self.title, True, self.title_color)
            title_pos = (self.rect.x + 16, self.rect.y + 12)
            surface.blit(title_surf, title_pos)

        # Desenhar filhos

        def _draw_children(surf):
            for child in self.children:
                if child.visible:
                    child.draw(surf)

        self.draw_with_clip(surface, _draw_children)


Panel = UIPanel
