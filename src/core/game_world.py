import pygame
from core.camera_group import CameraGroup
from abc import ABC, abstractmethod
from typing import List, Tuple
from core.game_object import GameObject, StaticObject, DynamicObject
from core.camera_group import CameraGroup

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
        self.all_sprites = CameraGroup()
        self.obstacles = pygame.sprite.Group()
        self.dynamic_group = pygame.sprite.Group()


    def set_target(self, target: GameObject):
        self.target = target
        try:
            self.all_sprites.set_target(target)
        except Exception:
            pass

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
        self.all_sprites.add(obj, layer=layer)

    def remove_object(self, obj: GameObject):
        self.all_sprites.remove(obj)

    def update(self, dt: float):
        for obj in self.camera_group.sprites():
            if obj.active:
                obj.update(dt)

            if isinstance(obj, DynamicObject):
                try:
                    new_layer = 2 + int(round(obj.pos.y))
                    if new_layer != getattr(obj, "render_layer", None):
                        self.all_sprites.change_layer(obj, new_layer)
                        obj.render_layer = new_layer
                except Exception:
                    pass

    def handle_events(self, events: List[pygame.event.Event]):
        for obj in self.camera_group.sprites():
            if obj.active:
                for event in events:
                    obj.process_event(event)

    def draw(self, surface: pygame.Surface):

        try:
            self.all_sprites.custom_draw(surface)
        except Exception:
            self.all_sprites.draw(surface)

    def _iterate_objects(self):
        for obj in self.all_sprites:
            yield obj

    def _iterate_active_objects(self):
        for obj in self._iterate_objects():
            if obj.active:
                yield obj
