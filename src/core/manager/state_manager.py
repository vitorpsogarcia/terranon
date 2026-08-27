from typing import TYPE_CHECKING

from core.enums.game_state_enum import GameStateEnum
from core.singleton_meta import SingletonMeta

if TYPE_CHECKING:
    from core.manager.game_manager import GameManager
    from core.states.base_state import BaseState


class StateManager(metaclass=SingletonMeta):
    def __init__(self, game_manager: "GameManager | None" = None):
        self.game_manager: GameManager | None = game_manager
        self.state_factories = {}

    def register_state(self, state_name: GameStateEnum, factory_func):
        self.state_factories[state_name.value] = factory_func

    def _create_state(self, state_name: GameStateEnum):
        if state_name.value not in self.state_factories:
            raise ValueError(f"State '{state_name.value}' not registered.")
        return self.state_factories[state_name.value]()

    def change_to(self, state_name: GameStateEnum):
        if self.game_manager is None:
            raise ValueError("GameManager not set for StateManager.")

        new_state = self._create_state(state_name)
        self.game_manager.change_state(new_state)

    def push(self, state_name: GameStateEnum):
        if self.game_manager is None:
            raise ValueError("GameManager not set for StateManager.")

        new_state = self._create_state(state_name)
        self.game_manager.push_state(new_state)

    def pop(self):
        if self.game_manager is None:
            raise ValueError("GameManager not set for StateManager.")

        self.game_manager.pop_state()

    @property
    def current_state(self):
        return self.game_manager.current_state if self.game_manager else None
