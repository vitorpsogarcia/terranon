from abc import ABC, abstractmethod
import pygame


class UIElement(ABC):
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.visible: bool = True
        self.enabled: bool = True

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass
