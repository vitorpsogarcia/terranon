import pygame

from core.component import Component


class TransformComponent(Component):
    def __init__(self, owner, initial_position: pygame.Vector2):
        super().__init__(owner)
        self.pos = pygame.math.Vector2(*initial_position)
