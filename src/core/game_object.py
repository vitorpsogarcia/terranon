from abc import ABC, abstractmethod
import pygame
from pygame.math import Vector2

from core.entity_sprite import EntitySprite


class GameObject(ABC):
    render_layer: int = 0

    def __init__(self, initial_position: tuple[float, float], *groups: pygame.sprite.Group):
        self._sprite = EntitySprite(self, *groups)
        self.pos = Vector2(*initial_position)
        self.active = True
        self.image = None
        self.rect = None

    @property
    def image(self):
        return self._sprite.image
    
    @image.setter
    def image(self, value):
        self._sprite.image = value

    @property
    def rect(self):
        return self._sprite.rect
    
    @rect.setter
    def rect(self, value):
        self._sprite.rect = value

    @abstractmethod
    def update(self, dt: float):
        """Processamento da lógica e física do objeto."""
        pass

    def process_event(self, event: pygame.event.Event):
        """Processamento de eventos específicos (override se necessário)."""
        pass

    def kill(self):
        """Desativa o objeto e remove seu sprite do grupo."""
        self.active = False
        self._sprite.kill()

    def alive(self):
        """Verifica se o objeto ainda está ativo."""
        return self._sprite.alive()


class StaticObject(GameObject):
    def __init__(self, initial_position: tuple[float, float], *groups: pygame.sprite.Group):
        super().__init__(initial_position, *groups)

    def update(self, dt: float):
        if self.rect:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

class DynamicObject(GameObject):
    def __init__(self, initial_position: tuple[float, float], *groups: pygame.sprite.Group):
        super().__init__(initial_position, *groups)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

    def update(self, dt: float):
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt
        if self.rect:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))