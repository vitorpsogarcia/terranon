import pygame
from typing import TYPE_CHECKING

from core.states.base_state import BaseState
from core.settings.colors import Colors

if TYPE_CHECKING:
    from core.state_manager import StateManager


class MenuState(BaseState):

    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)

        self.font = pygame.font.SysFont("Arial", 56)
        self.small_font = pygame.font.SysFont("Arial", 36)

        self.title_text: pygame.Surface | None = None
        self.instruction_text: pygame.Surface | None = None

    def enter(self):
        self.title_text = self.font.render("Menu State", True, Colors.text.primary)
        self.instruction_text = self.small_font.render("Press Enter to Start", True, Colors.text.primary)

    def exit(self):
        pass

    def update(self, delta_time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state_manager.change_to("play")
                print("Enter pressed - Start Game")
        pass

    def draw(self, surface):
        if self.title_text is None or self.instruction_text is None:
            return

        surface.fill(Colors.ui.background)
        
        surface.blit(self.title_text, (self.screen_size[0] // 2 - self.title_text.get_width() // 2, self.screen_size[1] // 3))
        surface.blit(self.instruction_text, (self.screen_size[0] // 2 - self.instruction_text.get_width() // 2, self.screen_size[1] // 2))