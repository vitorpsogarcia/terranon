import pygame

from core.manager.economy_manager import EconomyManager
from core.settings.colors import Colors
from core.ui.icon import Icon


class GameHUD:
    """Head-Up Display (HUD) para a tela de gameplay (PlayState).

    Renderiza em coordenadas fixas de tela:
    - Canto superior esquerdo: Ícone de moeda e pontos disponíveis (current_points)
    - Canto superior direito: Pontuação acumulada (total_points)
    - Canto inferior esquerdo: Avatar procedural do player e barras de status
      (Vida do jogador, Escudo condicional e Vida da base central).
    """

    def __init__(self, screen_size: tuple[int, int]):
        self.screen_size = screen_size
        self.font = pygame.font.SysFont("Arial", 13, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.economy = EconomyManager()

        # Ícones procedurais
        self.coin_icon = Icon(
            icon_type="coin",
            rect=pygame.Rect(20, 16, 26, 26),
        )
        self.avatar_icon = Icon(
            icon_type="avatar",
            rect=pygame.Rect(20, screen_size[1] - 96, 76, 76),
        )

    def draw(self, surface: pygame.Surface, player, main_base=None) -> None:
        """Renderiza todos os elementos do HUD sobre a superfície fornecida."""
        self._draw_top_bar(surface)
        if player is not None:
            self._draw_status_bars(surface, player, main_base)

    def _draw_top_bar(self, surface: pygame.Surface) -> None:
        # --- Canto superior esquerdo: Moeda e pontos ---
        self.coin_icon.draw(surface)

        points_text = str(self.economy.current_points)
        points_surf = self.header_font.render(
            points_text, True, Colors.brand.secondary
        )
        surface.blit(points_surf, (self.coin_icon.rect.right + 10, 16))

        # --- Canto superior direito: Score total ---
        score_text = f"SCORE: {self.economy.total_points:05d}"
        score_surf = self.header_font.render(
            score_text, True, Colors.text.primary
        )
        score_x = self.screen_size[0] - score_surf.get_width() - 24
        surface.blit(score_surf, (score_x, 16))

    def _draw_status_bars(self, surface: pygame.Surface, player, main_base) -> None:
        # Desenha o avatar detalhado do player
        self.avatar_icon.draw(surface)

        # Configurações das barras ampliadas
        bar_x = self.avatar_icon.rect.right + 14
        bar_w = 260
        bar_h = 22
        spacing = 5

        # Determina as barras ativas a desenhar
        bars_to_draw = []

        # 1. Barra de Vida do Jogador (sempre presente)
        if hasattr(player, "health") and player.health is not None:
            bars_to_draw.append({
                "label": "HP",
                "current": player.health.current_hp,
                "max": player.health.max_hp,
                "color": Colors.feedback.error,
            })

        # 2. Barra de Escudo (apenas quando equipado/ativo)
        if (
            hasattr(player, "shield")
            and player.shield is not None
            and getattr(player.shield, "is_active", False)
        ):
            bars_to_draw.append({
                "label": "ESCUDO",
                "current": player.shield.current_shield,
                "max": player.shield.max_shield,
                "color": Colors.feedback.info,
            })

        # 3. Barra de Integridade da Base Central
        if main_base is not None and hasattr(main_base, "health") and main_base.health is not None:
            bars_to_draw.append({
                "label": "BASE",
                "current": main_base.health.current_hp,
                "max": main_base.health.max_hp,
                "color": Colors.feedback.warning,  # Laranja brilhante
            })

        # Alinha as barras verticalmente ao lado do avatar
        total_bars_height = len(bars_to_draw) * bar_h + max(0, len(bars_to_draw) - 1) * spacing
        curr_y = self.avatar_icon.rect.centery - total_bars_height // 2

        for bar_data in bars_to_draw:
            self._render_bar(
                surface=surface,
                x=bar_x,
                y=curr_y,
                w=bar_w,
                h=bar_h,
                current=bar_data["current"],
                max_val=bar_data["max"],
                fill_color=bar_data["color"],
                label_prefix=bar_data["label"],
            )
            curr_y += bar_h + spacing

    def _render_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        current: float,
        max_val: float,
        fill_color: tuple,
        label_prefix: str = "",
    ) -> None:
        """Desenha uma barra ampliada com preenchimento proporcional, relevo e o valor 'atual | max' centralizado."""
        current = max(0.0, min(float(current), float(max_val)))
        ratio = current / max_val if max_val > 0 else 0.0

        bar_rect = pygame.Rect(x, y, w, h)

        # Fundo da barra
        pygame.draw.rect(
            surface, (20, 26, 38), bar_rect, border_radius=5
        )

        # Preenchimento proporcional
        fill_w = int(w * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(x, y, fill_w, h)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=5)

            # Brilho superior estilizado (Glossy highlight)
            if fill_w > 4:
                highlight_c = tuple(min(255, c + 50) for c in fill_color[:3])
                pygame.draw.line(
                    surface, highlight_c, (x + 3, y + 2), (x + fill_w - 3, y + 2), width=2
                )

        # Borda externa
        pygame.draw.rect(
            surface, (55, 65, 81), bar_rect, width=1, border_radius=5
        )

        # Texto "LABEL 100 | 100" centralizado com sombra de contraste
        val_text = f"{int(current)} | {int(max_val)}"
        text = f"{label_prefix}  {val_text}" if label_prefix else val_text

        text_surf = self.font.render(text, True, (255, 255, 255))
        shadow_surf = self.font.render(text, True, (10, 14, 22))

        text_x = x + (w - text_surf.get_width()) // 2
        text_y = y + (h - text_surf.get_height()) // 2

        surface.blit(shadow_surf, (text_x + 1, text_y + 1))
        surface.blit(text_surf, (text_x, text_y))
