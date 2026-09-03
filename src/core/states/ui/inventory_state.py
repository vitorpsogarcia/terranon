from typing import TYPE_CHECKING
import pygame

from core.manager.economy_manager import EconomyManager
from core.settings.colors import Colors
from core.states.base_state import GameScene
from core.ui.button import Button

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager


class InventoryState(GameScene):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.font = pygame.font.SysFont("Arial", 42, bold=True)
        self.section_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.item_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.is_transparent = True
        self.blocks_update = True

        panel_w = self.screen_size[0] - 200
        panel_h = self.screen_size[1] - 160
        panel_x = 100
        panel_y = 80
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        self.btn_close = Button(
            rect=pygame.Rect(panel_x + panel_w - 140, panel_y + 18, 120, 36),
            text="FECHAR",
            font=self.small_font,
            on_click=self._close,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

    def _close(self):
        self.state_manager.pop()

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, dt: float):
        pass

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN and (
                event.key == pygame.K_ESCAPE or event.key == pygame.K_i
            ):
                self._close()
                return

            if self.btn_close.handle_event(event):
                return

    def draw(self, surface: pygame.Surface):
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill(Colors.ui.panel_transparent)
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, Colors.ui.panel, self.panel_rect, border_radius=10)
        pygame.draw.rect(surface, Colors.ui.border, self.panel_rect, width=2, border_radius=10)

        title_surf = self.font.render("INVENTÁRIO & ESTRUTURAS", True, Colors.text.primary)
        surface.blit(title_surf, (self.panel_rect.x + 24, self.panel_rect.y + 18))

        self.btn_close.draw(surface)

        divider_y = self.panel_rect.y + 70
        pygame.draw.line(
            surface,
            Colors.ui.border,
            (self.panel_rect.x + 20, divider_y),
            (self.panel_rect.right - 20, divider_y),
            width=1,
        )

        economy = EconomyManager()
        points_surf = self.section_font.render(
            f"Pontos Disponíveis: {economy.current_points}  (Total: {economy.total_points})",
            True,
            Colors.brand.secondary,
        )
        surface.blit(points_surf, (self.panel_rect.x + 24, divider_y + 18))

        towers_label = self.section_font.render("Torres & Defesas:", True, Colors.text.primary)
        surface.blit(towers_label, (self.panel_rect.x + 24, divider_y + 65))

        slot_rect = pygame.Rect(self.panel_rect.x + 24, divider_y + 105, 220, 110)
        pygame.draw.rect(surface, Colors.ui.background_light, slot_rect, border_radius=8)
        pygame.draw.rect(surface, Colors.brand.primary, slot_rect, width=2, border_radius=8)

        tower_title = self.item_font.render("Torre Básica (Gatling)", True, Colors.text.on_brand)
        tower_cost = self.item_font.render("Custo: 50 pts", True, Colors.feedback.warning)
        tower_status = self.item_font.render("Status: Disponível", True, Colors.feedback.success)

        surface.blit(tower_title, (slot_rect.x + 12, slot_rect.y + 14))
        surface.blit(tower_cost, (slot_rect.x + 12, slot_rect.y + 42))
        surface.blit(tower_status, (slot_rect.x + 12, slot_rect.y + 70))

        hint_surf = self.small_font.render("Pressione I ou ESC para fechar", True, Colors.text.disabled)
        surface.blit(
            hint_surf,
            (self.panel_rect.centerx - hint_surf.get_width() // 2, self.panel_rect.bottom - 40),
        )
