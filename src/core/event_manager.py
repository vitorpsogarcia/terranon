from typing import Dict, List

from core.enums.game_event_enum import GameEventEnum
from core.exceptions.event_not_valid_exception import EventNotValidException


class EventManager:
    _instance = None
    _events_listeners: Dict[GameEventEnum, list] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls()

    @classmethod
    def initialize(cls):
        if getattr(cls, "_initialized", False):
            raise ValueError(f"{cls.__name__} has already been initialized.")
        
        instance = cls()
        for event in GameEventEnum:
            instance._events_listeners[event] = []
            
        cls._initialized = True

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
