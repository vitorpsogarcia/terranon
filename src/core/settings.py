from os import path
from pathlib import Path

SCREEN_WIDTH = 1056
SCREEN_HEIGHT = 720
SCREEN_NAME = "Terranon"
FPS = 60
DELTA_TIME = 0.1
COLORS_GAME = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0)
}

SPEED_PLAYER = 120
FRAME_WIDTH_PLAYER = 48
FRAME_HEIGHT_PLAYER = 48
SCALE_PLAYER = 2.0

ASSETS_FOLDER = Path(path.join(path.dirname(__file__), '..', '..', 'assets'))
DIRECTIONS = ["N", "S", "W", "E", "NW", "NE", "SW", "SE"]