import pygame
from core.game_object import DynamicObject


class Character(DynamicObject):
    def __init__(self, x: float, y: float, speed: float = 100.0):
        super().__init__(x, y)
        self.health = 100
        self.speed = speed
        self.direction = pygame.math.Vector2(0, 0)

    def move(self, dt: float):
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.velocity = self.direction * self.speed

    def update(self, dt: float):
        self.move(dt)
        super().update(dt)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
