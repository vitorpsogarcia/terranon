import logging

import pygame

from core.enums.game_state_enum import GameStateEnum
from core.manager.event_manager import EventManager
from core.manager.game_manager import GameManager
from core.manager.state_manager import StateManager
from core.map.map_manager import MapManager
from core.settings.settings import SCREEN_HEIGHT, SCREEN_NAME, SCREEN_WIDTH
from core.states.play_state import PlayState
from core.states.ui.game_over import GameOverState
from core.states.ui.inventory_state import InventoryState
from core.states.ui.menu_state import MenuState


def main():
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p",
        format="%(asctime)s [%(levelname)s] [%(name)s]\t%(message)s",
    )
    pygame.init()
    pygame.display.set_caption(SCREEN_NAME)
    tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    MapManager()
    EventManager()

    game_manager = GameManager(tela)
    state_manager = StateManager(game_manager)

    state_manager.register_state(
        GameStateEnum.MENU,
        lambda: MenuState(state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT)),
    )
    state_manager.register_state(
        GameStateEnum.PLAY,
        lambda: PlayState(state_manager, game_manager, (SCREEN_WIDTH, SCREEN_HEIGHT)),
    )
    state_manager.register_state(
        GameStateEnum.INVENTORY,
        lambda: InventoryState(state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT)),
    )
    state_manager.register_state(
        GameStateEnum.GAME_OVER,
        lambda: GameOverState(state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT)),
    )

    state_manager.change_to(GameStateEnum.MENU)

    game_manager.on_execute()


if __name__ == "__main__":
    main()
