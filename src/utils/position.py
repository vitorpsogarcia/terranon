import pygame


def calculate_distance(pos1: pygame.Vector2, pos2: pygame.Vector2) -> float:
    """
    Calculate the distance between two positions.

    Args:
        pos1 (pygame.Vector2): The first position.
        pos2 (pygame.Vector2): The second position.

    Returns:
        float: The distance between the two positions.
    """
    return pos1.distance_to(pos2)
