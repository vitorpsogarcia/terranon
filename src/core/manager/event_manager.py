import weakref
from inspect import ismethod

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

        for ref in self._events_listeners[event]:
            if ref() == listener:
                return

        if ismethod(listener):
            ref = weakref.WeakMethod(listener)
        else:
            ref = weakref.ref(listener)

        self._events_listeners[event].append(ref)

    def unsubscribe(self, event: GameEventEnum, listener):
        self._validate_event(event)
        for ref in self._events_listeners[event]:
            if ref() == listener:
                self._events_listeners[event].remove(ref)
                break

    def emit(self, event: GameEventEnum, *args, **kwargs):
        self._validate_event(event)

        listeners = list(self._events_listeners[event])
        for ref in listeners:
            if ref in self._events_listeners[event]:
                func = ref()
                if func is not None:
                    func(*args, **kwargs)

        self._events_listeners[event] = [
            ref for ref in self._events_listeners[event] if ref() is not None
        ]
