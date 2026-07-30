from __future__ import annotations
from pygame import Vector2

class Waypoint:
    def __init__(self, id: str | int, position: Vector2):
        self.id = id
        self.position = position
