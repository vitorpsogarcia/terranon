import pygame
from typing import TYPE_CHECKING

from core.enums.game_state_enum import GameStateEnum
from core.states.base_state import BaseState
from core.settings.colors import Colors

if TYPE_CHECKING:
    from core.state_manager import StateManager


class GameOverState(BaseState):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.font = pygame.font.SysFont("Arial", 72)
        self.small_font = pygame.font.SysFont("Arial", 36)
    
    def enter(self):
        print("Game Over State")
    
    def exit(self):
        pass
    
    def update(self, delta_time):
        pass
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state_manager.change_to(GameStateEnum.MENU)
    
    def draw(self, surface):
        surface.fill(Colors.ui.background)
        game_over_text = self.font.render("GAME OVER", True, Colors.feedback.error)
        enter_to_continue = self.small_font.render("Press ENTER to continue", True, Colors.text.primary)
        surface.blit(game_over_text, (self.screen_size[0] // 2 - game_over_text.get_width() // 2, self.screen_size[1] // 2 - enter_to_continue.get_height() // 2))
        surface.blit(enter_to_continue, (self.screen_size[0] // 2 - enter_to_continue.get_width() // 2, self.screen_size[1] // 2 + enter_to_continue.get_height() + 30))