import math

import pygame

from core.enums.directions_enum import DirectionsEnum


def get_rotation_by_directions(first_direction: DirectionsEnum, second_direction: DirectionsEnum) -> float:
    if first_direction == second_direction:
        return 0

    angle_first = math.degrees(math.atan2(-first_direction.direction.y, first_direction.direction.x))
    angle_second = math.degrees(math.atan2(-second_direction.direction.y, second_direction.direction.x))

    rotation_diff = angle_second - angle_first

    return rotation_diff % 360

def get_rotation_by_vector(start: pygame.math.Vector2, end: pygame.math.Vector2) -> float:
    direction = end - start
    return math.degrees(math.atan2(-direction.y, direction.x))