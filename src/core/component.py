from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from core.game_object import GameObject

T = TypeVar("T", bound="Component")


class Component:
    def __init__(self, owner: "GameObject"):
        self.owner = owner
        self.active = True

    def update(self, dt: float):
        pass
