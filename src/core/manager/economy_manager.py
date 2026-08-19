import logging

from core.enums.game_event_enum import GameEventEnum
from core.manager.event_manager import EventManager


class EconomyManager:
    _logger = logging.getLogger("EconomyManager")

    _instance: "EconomyManager"
    _current_points: int
    _total_points: int

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._current_points = 0
        self._total_points = 0

        EventManager.get_instance().subscribe(
            GameEventEnum.SPEND_POINTS, self.spend_points
        )

        EventManager.get_instance().subscribe(
            GameEventEnum.ENEMY_KILLED, self.add_points
        )

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls()

    @property
    def current_points(self):
        return self._current_points

    @current_points.setter
    def current_points(self, value):
        self._current_points = value

    @property
    def total_points(self):
        return self._total_points

    @total_points.setter
    def total_points(self, value):
        self._total_points = value

    def add_points(self, points):
        self._current_points += points
        self._total_points += points

    def remove_points(self, points):
        self._current_points -= points
        self._current_points = max(self._current_points, 0)

    def reset_points(self):
        self._current_points = 0
        self._total_points = 0

    def spend_points(self, points):
        if self._current_points >= points:
            self._current_points -= points
            return True
        else:
            return False
