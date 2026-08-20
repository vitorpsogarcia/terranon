from core.enums.game_event_enum import GameEventEnum
from core.exceptions.event_not_valid_exception import EventNotValidException
from core.singleton_meta import SingletonMeta


class EventManager(metaclass=SingletonMeta):
    _events_listeners: dict[GameEventEnum, list]

    def __init__(self):
        self._events_listeners = {}
        for event in GameEventEnum:
            self._events_listeners[event] = []

    def _validate_event(self, event: GameEventEnum):
        if event not in self._events_listeners:
            raise EventNotValidException(event.value)

    def subscribe(self, event: GameEventEnum, listener):
        self._validate_event(event)
        self._events_listeners[event].append(listener)

    def unsubscribe(self, event: GameEventEnum, listener):
        self._validate_event(event)
        if listener in self._events_listeners[event]:
            self._events_listeners[event].remove(listener)

    def emit(self, event: GameEventEnum, *args, **kwargs):
        self._validate_event(event)
        for listener in self._events_listeners[event]:
            listener(*args, **kwargs)
