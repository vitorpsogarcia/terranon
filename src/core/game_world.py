import pygame
from abc import ABC, abstractmethod
from typing import List, Tuple
from core.game_object import GameObject, StaticObject, DynamicObject


class GameScene(ABC):
    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def handle_events(self, events: List[pygame.event.Event]):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass


class GameWorld(GameScene):
    def __init__(self, screen_size: Tuple[int, int]):
        self.objects = pygame.sprite.LayeredUpdates()
        self.obstacles = pygame.sprite.Group()
        self.dynamic_group = pygame.sprite.Group()

        self.target = None
        self.screen_size = screen_size
        self.middle = (screen_size[0] // 2, screen_size[1] // 2)
        self.offset = pygame.math.Vector2()

    def set_target(self, target: GameObject):
        self.target = target

    def add_object(self, obj: GameObject):

        if isinstance(obj, DynamicObject):
            layer = 2 + int(obj.pos.y)
            self.dynamic_group.add(obj)
        elif isinstance(obj, StaticObject):
            if obj.__class__.__name__ == "Obstacle":
                layer = 1
                self.obstacles.add(obj)
            else:
                layer = 0
        else:
            layer = getattr(obj, "render_layer", 0)

        obj.render_layer = layer
        self.objects.add(obj, layer=layer)

    def remove_object(self, obj: GameObject):
        self.objects.remove(obj)

    def update(self, dt: float):
        for obj in self._iterate_active_objects():
            obj.update(dt)

            if isinstance(obj, DynamicObject):
                try:
                    new_layer = 2 + int(round(obj.pos.y))
                    if new_layer != getattr(obj, "render_layer", None):
                        self.objects.change_layer(obj, new_layer)
                        obj.render_layer = new_layer
                except Exception:
                    pass

    def handle_events(self, events: List[pygame.event.Event]):
        for obj in self._iterate_active_objects():
            for event in events:
                obj.process_event(event)

    def draw(self, surface: pygame.Surface):
        if self.target and hasattr(self.target, "rect"):
            self.offset.x = self.target.rect.centerx - self.middle[0]
            self.offset.y = self.target.rect.centery - self.middle[1]

        for obj in self.objects:
            obj.draw(surface, self.offset)

    def _iterate_objects(self):
        for obj in self.objects:
            yield obj

    def _iterate_active_objects(self):
        for obj in self._iterate_objects():
            if obj.active:
                yield obj
