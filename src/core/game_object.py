from abc import ABC, abstractmethod

import pygame
from pygame.math import Vector2

from core.entity_sprite import EntitySprite


class GameObject(ABC):
    _render_layer: int = 0
    pos: Vector2
    active: bool
    relative_hitboxes: list[pygame.Rect]
    _sprite: EntitySprite
    _fixed_layer: bool
    _fixed_opacity: bool

    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        self.pos = Vector2(*initial_position)
        self.active = True
        self.hitbox = pygame.Rect(self.pos.x, self.pos.y, 32, 32)
        self.rect: pygame.Rect | None = self.hitbox
        self.image: pygame.Surface | None = None
        self.relative_hitboxes = []
        self._fixed_layer = False
        self._fixed_opacity = False
        self._sprite = EntitySprite(self, *groups)

    @property
    def hitboxes(self) -> list[pygame.Rect]:
        if self.hitbox is None:
            return []

        absolute_hitboxes = []
        for rel_box in self.relative_hitboxes:
            abs_box = rel_box.move(self.hitbox.topleft)
            absolute_hitboxes.append(abs_box)
        return absolute_hitboxes

    @property
    def render_layer(self):
        return self._render_layer

    @render_layer.setter
    def render_layer(self, value):
        if self._fixed_layer:
            return
        self._render_layer = value

    def sync_colliders(self):
        if self.hitbox is not None:
            self.hitbox.center = (round(self.pos.x), round(self.pos.y))
            self.rect.center = self.hitbox.center

    @abstractmethod
    def update(self, dt: float):
        """Processamento da lógica e física do objeto."""

    def process_event(self, event: pygame.event.Event):
        """Processamento de eventos específicos (override se necessário)."""

    def kill(self):
        """Desativa o objeto e remove seu sprite do grupo."""
        self.active = False
        self._sprite.kill()

    def alive(self):
        """Verifica se o objeto ainda está ativo."""
        return self._sprite.alive()

    def on_collision(self, other: "GameObject"):
        """Método chamado quando ocorre uma colisão com outro GameObject (override se necessário)."""


class StaticObject(GameObject):
    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        super().__init__(initial_position, *groups)
        self.render_layer = 2

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
        self.render_layer = 1

    def update(self, dt: float):
        self.prev_pos = self.pos.copy()
        self.velocity += self.acceleration * dt
        self.velocity *= self.friction

        if self.velocity.length() < 0.01:
            self.velocity = Vector2(0, 0)

        self.pos += self.velocity * dt
        if self.rect:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
