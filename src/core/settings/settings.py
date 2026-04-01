from os import path
from pathlib import Path

import pygame

SCREEN_WIDTH = 1056
SCREEN_HEIGHT = 720
SCREEN_NAME = "Terranon"
FPS = 60
DELTA_TIME = 0.1

FRAME_WIDTH_PLAYER = 48
FRAME_HEIGHT_PLAYER = 48
SCALE_PLAYER = 1.5

ASSETS_FOLDER = Path(path.join(path.dirname(__file__), '..', '..', 'assets'))
DIRECTIONS = ["N", "S", "W", "E", "NW", "NE", "SW", "SE"]

PLAYER_BASE_SPEED = 250
PLAYER_KEYS = {
    "UP": pygame.K_w,
    "DOWN": pygame.K_s,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "RUN": pygame.K_LSHIFT,
    "SHOOT": pygame.MOUSEBUTTONDOWN
}