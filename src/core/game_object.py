from abc import ABC, abstractmethod
import pygame
from pygame.math import Vector2


class GameObject(ABC, pygame.sprite.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.pos = Vector2(x, y)
        self.active = True
        self.image = None
        self.rect = None

    @abstractmethod
    def update(self, dt: float):
        """Processamento da lógica e física do objeto."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """Renderização do objeto na tela."""
        pass

    def process_event(self, event: pygame.event.Event):
        """Processamento de eventos específicos (override se necessário)."""
        pass


class StaticObject(GameObject):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

    def update(self, dt: float):
        if self.rect:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface: pygame.Surface):
        if self.image and self.rect:
            surface.blit(self.image, self.rect)


class DynamicObject(GameObject):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

    def update(self, dt: float):
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt
        if self.rect:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface: pygame.Surface):

        if self.image and self.rect:
            surface.blit(self.image, self.rect)
