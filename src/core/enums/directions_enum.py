from enum import Enum

import pygame


class DirectionsEnum(Enum):
    NORTH = ("N", pygame.Vector2(0, -1))
    SOUTH = ("S", pygame.Vector2(0, 1))
    EAST = ("E", pygame.Vector2(1, 0))
    WEST = ("W", pygame.Vector2(-1, 0))
    NORTH_EAST = ("NE", pygame.Vector2(1, -1))
    NORTH_WEST = ("NW", pygame.Vector2(-1, -1))
    SOUTH_EAST = ("SE", pygame.Vector2(1, 1))
    SOUTH_WEST = ("SW", pygame.Vector2(-1, 1))

    def __init__(self, text: str, direction: pygame.Vector2):
        self.text = text
        self.direction = direction


    @staticmethod
    def to_list():
        return [DirectionsEnum.NORTH, DirectionsEnum.SOUTH, DirectionsEnum.EAST, DirectionsEnum.WEST, DirectionsEnum.NORTH_EAST, DirectionsEnum.NORTH_WEST, DirectionsEnum.SOUTH_EAST, DirectionsEnum.SOUTH_WEST]

    @staticmethod
    def get_by_text(text: str):
        for direction in DirectionsEnum:
            if direction.text == text:
                return direction
        return None

    @staticmethod
    def get_by_vector(vector: pygame.Vector2):
        for direction in DirectionsEnum:
            if direction.direction == vector:
                return direction
        return None



