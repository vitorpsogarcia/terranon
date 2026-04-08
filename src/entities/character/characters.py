import pygame
from core.game_object import DynamicObject
from core.animator_component import AnimatorComponent


class Character(DynamicObject):
    def __init__(self, x: float, y: float, speed: float = 100.0, *groups: pygame.sprite.Group):
        super().__init__(x, y, *groups)
        self.animator = AnimatorComponent(self)
        self.health = 100
        self.speed = speed
        self.direction = pygame.math.Vector2(0, 0)

    def move(self, dt: float):
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.velocity = self.direction * self.speed

    def update(self, dt: float):
        self.move(dt)
        self.animator.update(dt)
        super().update(dt)
