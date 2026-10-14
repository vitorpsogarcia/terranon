import math
import pygame

from core.enums.wave_state_enum import WaveStateEnum
from core.settings.colors import Colors


class WaveHUD:
    """Componente de interface visual para exibição do status e contadores das ondas."""

    def __init__(self, badge_width: int = 320, badge_height: int = 48, top_margin: int = 14):
        self.badge_w = badge_width
        self.badge_h = badge_height
        self.badge_y = top_margin

        # Pré-alocação da superfície de fundo semitransparente para evitar alocações por frame
        self._bg_surface = pygame.Surface((self.badge_w, self.badge_h), pygame.SRCALPHA)
        self._bg_surface.fill((20, 28, 45, 220))

        self._font_title: pygame.font.Font | None = None
        self._font_sub: pygame.font.Font | None = None

    def _ensure_fonts(self):
        if self._font_title is None and pygame.font.get_init():
            self._font_title = pygame.font.SysFont("Arial", 18, bold=True)
            self._font_sub = pygame.font.SysFont("Arial", 12)

    def draw(
        self,
        surface: pygame.Surface,
        state: WaveStateEnum,
        current_wave_number: int,
        timer: float,
        alive_enemies: int,
        total_enemies: int,
    ) -> None:
        self._ensure_fonts()
        if self._font_title is None or self._font_sub is None:
            return

        screen_w = surface.get_width()
        badge_x = (screen_w - self.badge_w) // 2
        badge_rect = pygame.Rect(badge_x, self.badge_y, self.badge_w, self.badge_h)

        # Fundo pré-renderizado
        surface.blit(self._bg_surface, (badge_x, self.badge_y))

        # Borda estilizada
        border_color = (
            Colors.brand.secondary
            if state in (WaveStateEnum.WARMUP, WaveStateEnum.INTERVAL)
            else Colors.brand.primary
        )
        pygame.draw.rect(surface, border_color, badge_rect, width=1, border_radius=8)

        segundos = max(0, math.ceil(timer))

        if state == WaveStateEnum.WARMUP:
            main_text = f"PREPARE-SE: {segundos}s"
            main_color = Colors.brand.secondary
            sub_text = "[ESPAÇO] Iniciar Onda Agora"
            sub_color = Colors.text.secondary

        elif state == WaveStateEnum.ACTIVE:
            main_text = f"ONDA {current_wave_number}  |  {segundos}s"
            main_color = Colors.brand.primary
            sub_text = f"Inimigos Restantes: {alive_enemies} / {total_enemies}"
            sub_color = Colors.text.primary

        else:  # WaveStateEnum.INTERVAL
            main_text = f"PRÓXIMA ONDA EM: {segundos}s"
            main_color = Colors.brand.secondary
            sub_text = "[ESPAÇO] Iniciar Próxima Onda"
            sub_color = Colors.text.secondary

        title_surf = self._font_title.render(main_text, True, main_color)
        sub_surf = self._font_sub.render(sub_text, True, sub_color)

        title_pos = (
            badge_x + (self.badge_w - title_surf.get_width()) // 2,
            self.badge_y + 5,
        )
        sub_pos = (
            badge_x + (self.badge_w - sub_surf.get_width()) // 2,
            self.badge_y + 27,
        )

        surface.blit(title_surf, title_pos)
        surface.blit(sub_surf, sub_pos)
