import pygame
from abc import ABC, abstractmethod
from typing import List, Dict
from core.game_object import GameObject


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
    def __init__(self, screen_width: int, screen_height: int):
        self.objects: Dict[int, List[GameObject]] = {}

        self.target = None
        self.half_w = screen_width // 2
        self.half_h = screen_height // 2
        self.offset = pygame.math.Vector2()
        self._sorted_layers_keys = []

    def set_target(self, target: GameObject):
        self.target = target

    def add_object(self,obj: GameObject):
        layer = obj.render_layer
        if not self.objects.get(layer):
            self.objects[layer] = []
        
        self.objects[layer].append(obj)
        if layer not in self._sorted_layers_keys:
            self._sorted_layers_keys.append(layer)
            self._sorted_layers_keys.sort()

    def remove_object(self, obj: GameObject):
        layer = obj.render_layer

        if obj in self.objects.get(layer, []):
            self.objects[layer].remove(obj)

    def update(self, dt: float):
        for layer in self.objects:
            for obj in self.objects[layer]:
                if obj.active:
                    obj.update(dt)

    def handle_events(self, events: List[pygame.event.Event]):
        for layer in self.objects:
            for obj in self.objects[layer]:
                if obj.active:
                    for event in events:
                        obj.process_event(event)

    def draw(self, surface: pygame.Surface):
        if self.target and hasattr(self.target, 'rect'):
            self.offset.x = self.target.rect.centerx - self.half_w
            self.offset.y = self.target.rect.centery - self.half_h

        for layer in self._sorted_layers_keys:
            for obj in self.objects[layer]:
                if obj.active:
                    obj.draw(surface, self.offset)
