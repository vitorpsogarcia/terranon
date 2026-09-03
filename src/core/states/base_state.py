from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager


class GameScene(ABC):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        self.state_manager = state_manager
        self.screen_size = screen_size
        self.is_transparent: bool = False
        self.blocks_update: bool = True

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass


BaseState = GameScene
