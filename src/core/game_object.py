from abc import ABC, abstractmethod
import pygame
from pygame.math import Vector2

from core.entity_sprite import EntitySprite


class GameObject(ABC):
    render_layer: int = 0
    pos: Vector2
    active: bool
    relative_hitboxes: list[pygame.Rect]
    _sprite: EntitySprite

    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        self._sprite = EntitySprite(self, *groups)
        self.pos = Vector2(*initial_position)
        self.active = True
        self.image = None
        self.rect = None
        self.relative_hitboxes = []

    @property
    def image(self):
        return self._sprite.image
    

    @image.setter
    def image(self, value: pygame.Surface | None):
        self._sprite.image = value

        if value is not None:
            self.rect = value.get_rect()
        else:
            self.rect = None


    @property
    def rect(self):
        return self._sprite.rect
    
    @rect.setter
    def rect(self, value):
        self._sprite.rect = value


    @property
    def hitboxes(self) -> list[pygame.Rect]:
        """
        Calcula as posições absolutas das hitboxes com base na posição atual do objeto e retorna uma nova lista de Rects.
        """
        if self.rect is None:
            return []
        
        absolute_hitboxes = []
        for rel_box in self.relative_hitboxes:
            abs_box = rel_box.move(self.rect.topleft)
            absolute_hitboxes.append(abs_box)
        return absolute_hitboxes


    def sync_colliders(self):
        if self.rect is None:
            return

        self.rect.center = (round(self.pos.x), round(self.pos.y))


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
    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        super().__init__(initial_position, *groups)

    def update(self, dt: float):
        if self.rect:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

class DynamicObject(GameObject):
    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        super().__init__(initial_position, *groups)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.friction = 0.85
        self.prev_pos = self.pos.copy()

    def update(self, dt: float):
        self.velocity += self.acceleration * dt
        self.velocity *= self.friction

        if self.velocity.length() < 0.01:
            self.velocity = Vector2(0, 0)

        self.pos += self.velocity * dt
        if self.rect:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))