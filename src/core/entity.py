import pygame
from core.game_object import GameObject
from core.components.rigidbody_component import RigidbodyComponent

class Entity(GameObject):
    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        super().__init__(initial_position, *groups)
        self.rigidbody = self.add_component(RigidbodyComponent(self))
