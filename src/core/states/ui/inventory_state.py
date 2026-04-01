import pygame
from typing import TYPE_CHECKING

from core.settings.colors import Colors
from core.states.base_state import BaseState

if TYPE_CHECKING:
    from core.state_manager import StateManager
    from core.states.play_state import PlayState


class InventoryState(BaseState):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.font = pygame.font.SysFont("Arial", 48)
        self.play_state: "PlayState | None" = None
    
    def set_play_state(self, play_state: "PlayState"):
        self.play_state = play_state
    
    def enter(self):
        print("Inventory State")
    
    def exit(self):
        pass
    
    def update(self, delta_time):
        pass
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                    self.state_manager.change_to("play")
    
    def draw(self, surface: pygame.Surface):
        
        if self.play_state is not None:
            self.play_state.draw(surface)
        
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill(Colors.ui.panel_transparent)
        surface.blit(overlay, (0, 0))
        
        rect = pygame.Rect(100, 100, self.screen_size[0] - 200, self.screen_size[1] - 200)
        pygame.draw.rect(surface, Colors.ui.panel, rect)
        pygame.draw.rect(surface, Colors.ui.border, rect, 3)

        inventory_text = self.font.render("INVENTORY", True, Colors.text.primary)
        close_hint = pygame.font.SysFont("Arial", 24).render("Press ESC or I to close", True, Colors.text.secondary)
        surface.blit(inventory_text, (self.screen_size[0] // 2 - inventory_text.get_width() // 2, 120))
        surface.blit(close_hint, (self.screen_size[0] // 2 - close_hint.get_width() // 2, self.screen_size[1] - 150))