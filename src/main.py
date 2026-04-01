import pygame

from core.enums.game_state_enum import GameStateEnum
from core.game_manager import GameManager
from core.settings.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_NAME
from core.state_manager import StateManager
from core.states.ui.game_over import GameOverState
from core.states.ui.inventory_state import InventoryState
from core.states.ui.menu_state import MenuState
from core.states.play_state import PlayState

def main():
    pygame .init()
    pygame.display.set_caption(SCREEN_NAME)
    tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    game_manager = GameManager(tela)
    state_manager = StateManager(game_manager)
    
    play_state = PlayState(state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_state = MenuState(state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT))
    inventory_state = InventoryState(state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT))
    game_over_state = GameOverState(state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    inventory_state.set_play_state(play_state)
    
    state_manager.register_state(GameStateEnum.MENU, menu_state)
    state_manager.register_state(GameStateEnum.PLAY, play_state)
    state_manager.register_state(GameStateEnum.INVENTORY, inventory_state)
    state_manager.register_state(GameStateEnum.GAME_OVER, game_over_state)

    state_manager.change_to("menu")

    game_manager.on_execute()
    
if __name__ == "__main__":
    main()