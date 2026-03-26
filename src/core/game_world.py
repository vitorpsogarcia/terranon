import pygame
from core.camera_group import CameraGroup
from typing import List, Tuple
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
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
    def __init__(self, screen_size: Tuple[int, int]):
        self.camera_group = CameraGroup()

    def set_target(self, target: GameObject):
        self.camera_group.set_target(target)

    def add_object(self, obj: GameObject):
        self.camera_group.add(obj, layer=obj.render_layer)

    def remove_object(self, obj: GameObject):
        self.camera_group.remove(obj)

    def update(self, dt: float):
        for obj in self.camera_group.sprites():
            if obj.active:
                obj.update(dt)

    def handle_events(self, events: List[pygame.event.Event]):
        for obj in self.camera_group.sprites():
            if obj.active:
                for event in events:
                    obj.process_event(event)

    def draw(self, surface: pygame.Surface):
        self.camera_group.custom_draw(surface)
