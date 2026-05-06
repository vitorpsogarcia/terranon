from typing import Dict

from core.enums.game_event_enum import GameEventEnum
from core.exceptions.event_not_valid_exception import EventNotValidException


class EventManager:
    _instance = None
    _events_listeners: Dict[GameEventEnum, list] = {}

    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    
    @classmethod
    def initialize(cls):
        if cls._instance is not None:
            raise ValueError(f"{cls.__name__} has already been initialized.")
        cls._instance = cls()

        for event in GameEventEnum:
            cls._events_listeners[event] = []

    
    def _validate_event(self, event: GameEventEnum):
        if event not in self._events_listeners:
            raise EventNotValidException(event.value)
    

    def subscribe(self, event: GameEventEnum, listener):
        self._validate_event(event)
        self._events_listeners[event].append(listener)
    

    def unsubscribe(self, event: GameEventEnum, listener):
        self._validate_event(event)
        self._events_listeners[event].remove(listener)

    
    def emit(self, event: GameEventEnum, *args, **kwargs):
        self._validate_event(event)
        for listener in self._events_listeners[event]:
            listener(*args, **kwargs)