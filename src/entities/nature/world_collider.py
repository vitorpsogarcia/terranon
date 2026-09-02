import pygame

from entities.obstacle import Obstacle


class WorldCollider(Obstacle):
    def __init__(
        self,
        position: pygame.Vector2,
        width: float,
        height: float,
        *groups: pygame.sprite.Group,
    ):
        super().__init__(position, *groups, width=width, height=height)
