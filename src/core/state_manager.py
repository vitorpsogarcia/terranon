from typing import TYPE_CHECKING, Dict

from core.enums.game_state_enum import GameStateEnum


if TYPE_CHECKING:
    from core.states.base_state import BaseState
    from core.game_manager import GameManager


class StateManager:
    def __init__(self, game_manager: "GameManager | None" = None):
        self.game_manager: "GameManager | None" = game_manager
        self.states: Dict[str, "BaseState"] = {}
    
    def register_state(self, state_name: GameStateEnum, state):
        self.states[state_name.value] = state

    def change_to(self, state_name: str):
        if self.game_manager is None:
            raise ValueError("GameManager not set for StateManager.")
        
        if state_name not in self.states:
            raise ValueError(f"State '{state_name}' not registered in StateManager.")
        
        new_state = self.states[state_name]
        self.game_manager.change_state(new_state)
