
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state_manager import StateManager


class BaseState (ABC):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        self.state_manager = state_manager
        self.screen_size = screen_size

    @abstractmethod
    def enter(self):
        pass


    @abstractmethod
    def exit(self):
        pass


    @abstractmethod
    def update(self, delta_time):
        pass


    @abstractmethod
    def handle_events(self, events):
        pass


    @abstractmethod
    def draw(self, surface):
        pass