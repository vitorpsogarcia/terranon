from abc import ABC
from typing import TYPE_CHECKING

import pygame

from core.component import Component, T
from core.components.transform_component import TransformComponent
from core.entity_sprite import EntitySprite

if TYPE_CHECKING:
    from core.components.collider_component import ColliderComponent
    from entities.structures.towers.generic_tower import GenericTower


class GameObject(ABC):
    active: bool
    _sprite: EntitySprite
    _fixed_layer: bool
    _fixed_opacity: bool
    collider: "ColliderComponent | None"

    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        self.active = True
        self._fixed_layer = False
        self._fixed_opacity = False
        self.collider: ColliderComponent | None = None
        self.components: list[Component] = []

        self.transform = self.add_component(TransformComponent(self, initial_position))
        self._sprite = EntitySprite(self, *groups)

        self._is_turret_target = False
        self._turret = None

    def update(self, dt: float):
        """Processamento da lógica e física do objeto."""
        for comp in self.components:
            if getattr(comp, "active", True):
                comp.update(dt)

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

    def add_component(self, component: T) -> T:
        self.components.append(component)
        return component

    def get_component(self, comp_type: type[T]) -> T | None:
        """Retorna o primeiro componente que é instância do tipo especificado, ou None."""
        for comp in self.components:
            if isinstance(comp, comp_type):
                return comp
        return None

    def set_turret_target(self, turret: "GenericTower"):
        self._is_turret_target = True
        self._turret = turret

    def clear_turret_target(self):
        self._is_turret_target = False
        self._turret = None
