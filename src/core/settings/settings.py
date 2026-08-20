from pathlib import Path

import pygame

from utils.resource_path import resource_path

SCREEN_WIDTH = 1056
SCREEN_HEIGHT = 720
SCREEN_NAME = "Terranon"
FPS = 60
DELTA_TIME = 0.1

FRAME_WIDTH_PLAYER = 48
FRAME_HEIGHT_PLAYER = 48
SCALE_PLAYER = 0.75

ASSETS_FOLDER = Path(resource_path("assets"))

ANIMATIONS_FRAME_COUNT = 8

PROJECTILE_BASE_SPEED = 500
PROJECTILE_BASE_ANIMATION_SPEED = 6

MAIN_BASE_SIZE = 128
MAIN_BASE_HEALTH = 500


PLAYER_BASE_SPEED = 250
PLAYER_BASE_ANIMATION_SPEED = 6
PLAYER_KEYS = {
    "UP": pygame.K_w,
    "DOWN": pygame.K_s,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "RUN": pygame.K_LSHIFT,
    "SHOOT": pygame.MOUSEBUTTONDOWN,
}
