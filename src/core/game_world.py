import pygame
from abc import ABC, abstractmethod
from typing import List
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
    def __init__(self):
        self.objects: List[GameObject] = []

    def add_object(self, obj: GameObject):
        self.objects.append(obj)

    def remove_object(self, obj: GameObject):
        if obj in self.objects:
            self.objects.remove(obj)

    def update(self, dt: float):
        for obj in self.objects:
            if obj.active:
                obj.update(dt)

    def handle_events(self, events: List[pygame.event.Event]):
        for obj in self.objects:
            if obj.active:
                for event in events:
                    obj.process_event(event)

    def draw(self, surface: pygame.Surface):
        for obj in self.objects:
            if obj.active:
                obj.draw(surface)
