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
        sprite: pygame.Surface | None = None,
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
        self.sprite = sprite

        if self.icon_type == "avatar" and self.sprite is None:
            self._load_avatar_sprite()

    def _load_avatar_sprite(self):
        try:
            from pathlib import Path
            from core.settings.settings import ASSETS_FOLDER
            from utils.resource_path import resource_path
            sprite_path = Path(resource_path(str(ASSETS_FOLDER / "images" / "player" / "idle" / "S.png")))
            if sprite_path.exists():
                surf = pygame.image.load(str(sprite_path))
                if pygame.display.get_surface() is not None:
                    surf = surf.convert_alpha()
                self.sprite = surf
        except Exception:
            self.sprite = None

    def get_intrinsic_size(self) -> tuple[int, int]:
        if self.icon_type == "trash":
            return (16, 16)
        elif self.icon_type == "avatar":
            return (72, 72)
        elif self.icon_type in ("coin", "shield"):
            return (24, 24)
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

        cx = self.rect.centerx
        cy = self.rect.centery

        if self.icon_type == "trash":
            self._draw_trash_icon(surface, current_color)
        elif self.icon_type == "coin":
            radius = min(self.rect.width, self.rect.height) // 2 or 12
            self._draw_coin_icon(surface, cx, cy, radius=radius)
        elif self.icon_type == "avatar":
            self._draw_player_avatar(surface, self.rect)
        elif self.icon_type == "shield":
            w = self.rect.width or 16
            h = self.rect.height or 18
            self._draw_shield_icon(surface, cx, cy, w=w, h=h)

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

    def _draw_coin_icon(self, surface: pygame.Surface, cx: int, cy: int, radius: int = 12):
        pygame.draw.circle(surface, (180, 130, 0), (cx, cy), radius)
        pygame.draw.circle(surface, (255, 215, 0), (cx, cy), radius - 2)
        pygame.draw.circle(surface, (218, 165, 32), (cx, cy), radius - 4, width=1)
        pygame.draw.rect(surface, (180, 130, 0), (cx - 1, cy - radius + 6, 2, (radius - 6) * 2))

    def _draw_player_avatar(self, surface: pygame.Surface, rect: pygame.Rect):
        # 1. Fundo do painel e moldura tática
        pygame.draw.rect(surface, (15, 20, 30), rect, border_radius=10)

        # Linhas de scanline sutis no fundo do avatar
        for y_offset in range(rect.top + 8, rect.bottom - 8, 8):
            pygame.draw.line(
                surface, (24, 32, 46), (rect.left + 6, y_offset), (rect.right - 6, y_offset), width=1
            )

        # Borda principal externa (Teal)
        pygame.draw.rect(surface, (13, 148, 136), rect, width=2, border_radius=10)

        # Cantoneiras táticas reforçadas nos 4 cantos
        c_len = 8
        # Top-Left
        pygame.draw.line(surface, (45, 212, 191), (rect.left + 3, rect.top + 3), (rect.left + 3 + c_len, rect.top + 3), width=2)
        pygame.draw.line(surface, (45, 212, 191), (rect.left + 3, rect.top + 3), (rect.left + 3, rect.top + 3 + c_len), width=2)
        # Top-Right
        pygame.draw.line(surface, (45, 212, 191), (rect.right - 4, rect.top + 3), (rect.right - 4 - c_len, rect.top + 3), width=2)
        pygame.draw.line(surface, (45, 212, 191), (rect.right - 4, rect.top + 3), (rect.right - 4, rect.top + 3 + c_len), width=2)
        # Bottom-Left
        pygame.draw.line(surface, (45, 212, 191), (rect.left + 3, rect.bottom - 4), (rect.left + 3 + c_len, rect.bottom - 4), width=2)
        pygame.draw.line(surface, (45, 212, 191), (rect.left + 3, rect.bottom - 4), (rect.left + 3, rect.bottom - 4 - c_len), width=2)
        # Bottom-Right
        pygame.draw.line(surface, (45, 212, 191), (rect.right - 4, rect.bottom - 4), (rect.right - 4 - c_len, rect.bottom - 4), width=2)
        pygame.draw.line(surface, (45, 212, 191), (rect.right - 4, rect.bottom - 4), (rect.right - 4, rect.bottom - 4 - c_len), width=2)

        # 2. Renderização do Sprite do Player (se disponível)
        if self.sprite is not None:
            avail_w = rect.width - 16
            avail_h = rect.height - 12
            orig_w, orig_h = self.sprite.get_size()
            scale_factor = max(1.0, min(avail_w / orig_w, avail_h / orig_h))

            scaled_w = int(orig_w * scale_factor)
            scaled_h = int(orig_h * scale_factor)
            scaled_sprite = pygame.transform.scale(self.sprite, (scaled_w, scaled_h))

            dest_x = rect.centerx - scaled_w // 2
            dest_y = rect.centery - scaled_h // 2

            old_clip = surface.get_clip()
            surface.set_clip(rect.inflate(-4, -4))
            surface.blit(scaled_sprite, (dest_x, dest_y))
            surface.set_clip(old_clip)
            return

        cx, cy = rect.centerx, rect.centery
        scale = min(rect.width, rect.height) / 72.0

        # 3. Fallback Procedural: Armadura / Peitoral e Ombros
        sh_w = int(48 * scale)
        sh_y = cy + int(10 * scale)

        # Placa base dos ombros
        shoulder_poly = [
            (cx - sh_w // 2, rect.bottom - 6),
            (cx - sh_w // 2 + int(6 * scale), sh_y),
            (cx - int(14 * scale), sh_y - int(4 * scale)),
            (cx + int(14 * scale), sh_y - int(4 * scale)),
            (cx + sh_w // 2 - int(6 * scale), sh_y),
            (cx + sh_w // 2, rect.bottom - 6),
        ]
        pygame.draw.polygon(surface, (51, 65, 85), shoulder_poly)
        pygame.draw.polygon(surface, (71, 85, 105), shoulder_poly, width=1)

        # Ombreiras esquerda e direita
        l_plate = [
            (cx - sh_w // 2 + 1, rect.bottom - 7),
            (cx - sh_w // 2 + int(6 * scale), sh_y + 1),
            (cx - int(18 * scale), sh_y + int(4 * scale)),
            (cx - int(18 * scale), rect.bottom - 7),
        ]
        pygame.draw.polygon(surface, (30, 41, 59), l_plate)
        r_plate = [
            (cx + sh_w // 2 - 1, rect.bottom - 7),
            (cx + sh_w // 2 - int(6 * scale), sh_y + 1),
            (cx + int(18 * scale), sh_y + int(4 * scale)),
            (cx + int(18 * scale), rect.bottom - 7),
        ]
        pygame.draw.polygon(surface, (30, 41, 59), r_plate)

        # Núcleo / Reator tático no peito
        core_y = sh_y + int(8 * scale)
        pygame.draw.circle(surface, (13, 148, 136), (cx, core_y), max(2, int(4 * scale)))
        pygame.draw.circle(surface, (45, 212, 191), (cx, core_y), max(1, int(2 * scale)))

        # 3. Capacete Espacial
        helm_r = int(18 * scale)
        helm_cy = cy - int(9 * scale)

        # Sombra posterior do capacete
        pygame.draw.circle(surface, (71, 85, 105), (cx, helm_cy + 1), helm_r + 1)
        # Cúpula principal do capacete (cinza titânio)
        pygame.draw.circle(surface, (148, 163, 184), (cx, helm_cy), helm_r)
        # Faixa superior de reforço frontal
        pygame.draw.rect(
            surface, (203, 213, 225),
            (cx - int(8 * scale), helm_cy - helm_r, int(16 * scale), int(6 * scale)),
            border_radius=int(2 * scale)
        )

        # Módulos laterais / Comunicação
        comm_w = max(3, int(4 * scale))
        comm_h = max(6, int(8 * scale))
        pygame.draw.rect(surface, (51, 65, 85), (cx - helm_r - comm_w + 2, helm_cy - comm_h // 2, comm_w, comm_h), border_radius=1)
        pygame.draw.rect(surface, (51, 65, 85), (cx + helm_r - 2, helm_cy - comm_h // 2, comm_w, comm_h), border_radius=1)
        # Antena pequena no lado esquerdo
        ant_x = cx - helm_r - comm_w + 3
        pygame.draw.line(surface, (148, 163, 184), (ant_x, helm_cy - comm_h // 2), (ant_x, helm_cy - comm_h // 2 - int(8 * scale)), width=1)
        pygame.draw.circle(surface, (239, 68, 68), (ant_x, helm_cy - comm_h // 2 - int(8 * scale)), 1)

        # 4. Máscara de respiração / Queixo
        jaw_rect = pygame.Rect(cx - int(10 * scale), helm_cy + int(6 * scale), int(20 * scale), int(10 * scale))
        pygame.draw.rect(surface, (71, 85, 105), jaw_rect, border_radius=int(3 * scale))
        # Ranhuras de ventilação
        pygame.draw.line(surface, (30, 41, 59), (cx - int(4 * scale), helm_cy + int(9 * scale)), (cx - int(4 * scale), helm_cy + int(13 * scale)), width=1)
        pygame.draw.line(surface, (30, 41, 59), (cx, helm_cy + int(9 * scale)), (cx, helm_cy + int(13 * scale)), width=1)
        pygame.draw.line(surface, (30, 41, 59), (cx + int(4 * scale), helm_cy + int(9 * scale)), (cx + int(4 * scale), helm_cy + int(13 * scale)), width=1)

        # 5. Visor Holográfico Neon
        visor_w = int(24 * scale)
        visor_h = int(12 * scale)
        visor_rect = pygame.Rect(cx - visor_w // 2, helm_cy - int(4 * scale), visor_w, visor_h)

        pygame.draw.ellipse(surface, (15, 23, 42), visor_rect.inflate(2, 2))
        pygame.draw.ellipse(surface, (6, 182, 212), visor_rect)
        pygame.draw.line(
            surface, (255, 255, 255),
            (visor_rect.left + int(4 * scale), visor_rect.top + int(3 * scale)),
            (visor_rect.centerx - int(1 * scale), visor_rect.top + int(3 * scale)),
            width=max(1, int(2 * scale))
        )
        pygame.draw.circle(
            surface, (255, 255, 255),
            (visor_rect.centerx + int(4 * scale), visor_rect.top + int(4 * scale)),
            max(1, int(1.5 * scale))
        )

        # Retículo HUD sutil no visor
        pygame.draw.line(surface, (165, 243, 252), (cx, visor_rect.centery - 2), (cx, visor_rect.centery + 2), width=1)
        pygame.draw.line(surface, (165, 243, 252), (cx - 2, visor_rect.centery), (cx + 2, visor_rect.centery), width=1)

    def _draw_shield_icon(self, surface: pygame.Surface, cx: int, cy: int, w: int = 16, h: int = 18):
        hw, hh = w // 2, h // 2
        points = [
            (cx - hw, cy - hh),      # Topo esquerdo
            (cx + hw, cy - hh),      # Topo direito
            (cx + hw, cy + hh // 4), # Lateral direita
            (cx, cy + hh),          # Ponta inferior (V)
            (cx - hw, cy + hh // 4), # Lateral esquerda
        ]
        pygame.draw.polygon(surface, (59, 130, 246), points)
        pygame.draw.polygon(surface, (147, 197, 253), points, width=1)
