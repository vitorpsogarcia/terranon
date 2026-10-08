from enum import Enum


class GameStateEnum(Enum):
    MENU = "MENU"
    INTRO = "INTRO"
    PLAY = "PLAY"
    INVENTORY = "INVENTORY"
    GAME_OVER = "GAME_OVER"
    PAUSE = "PAUSE"
    PAUSED = "PAUSED"
