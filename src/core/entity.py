from typing import TypeVar

import pygame

from core.game_object import DynamicObject

T = TypeVar("T", bound="Component")


class Component:
    def __init__(self, owner: "Entity"):
        self.owner = owner
        self.active = True

    def update(self, dt: float):
        pass


class Entity(DynamicObject):
    def __init__(self, initial_position: pygame.Vector2, *groups: pygame.sprite.Group):
        super().__init__(initial_position, *groups)
        self.components: list[Component] = []

    def add_component(self, component: T) -> T:
        self.components.append(component)
        return component

    def update(self, dt: float):
        if not self.active:
            return

        for comp in self.components:
            # Component may not inherit from the Component base class yet (e.g. HealthComponent)
            if getattr(comp, "active", True):
                comp.update(dt)

        super().update(dt)
