from typing import TYPE_CHECKING

import pygame

from core.component import Component
from core.enums.collider_tag_enum import ColliderTagEnum

if TYPE_CHECKING:
    from core.game_object import GameObject


class BoxCollider:
    def __init__(
        self,
        offset_x: float,
        offset_y: float,
        width: float,
        height: float,
        tag: ColliderTagEnum = ColliderTagEnum.SOLID,
        is_trigger: bool = False,
    ):
        self.offset = pygame.math.Vector2(offset_x, offset_y)
        self.width = float(width)
        self.height = float(height)
        self.tag = tag
        self.is_trigger = is_trigger

    def get_world_rect(self, owner_pos: pygame.math.Vector2) -> pygame.Rect:
        return pygame.Rect(
            round(owner_pos.x + self.offset.x),
            round(owner_pos.y + self.offset.y),
            round(self.width),
            round(self.height),
        )


class ColliderComponent(Component):
    def __init__(self, owner: "GameObject"):
        super().__init__(owner)
        self.owner = owner
        self.colliders: list[BoxCollider] = []
        self.active = True

    def add_box(
        self,
        offset_x: float,
        offset_y: float,
        width: float,
        height: float,
        tag: ColliderTagEnum = ColliderTagEnum.SOLID,
        is_trigger: bool = False,
    ) -> BoxCollider:
        box = BoxCollider(
            offset_x=offset_x,
            offset_y=offset_y,
            width=width,
            height=height,
            tag=tag,
            is_trigger=is_trigger,
        )
        self.colliders.append(box)
        return box

    def add_collider(self, collider: BoxCollider):
        self.colliders.append(collider)

    def remove_collider(self, collider: BoxCollider):
        if collider in self.colliders:
            self.colliders.remove(collider)

    def get_world_rects(
        self, tag: ColliderTagEnum | None = None
    ) -> list[tuple[pygame.Rect, ColliderTagEnum]]:
        """Retorna uma lista de tuplas (pygame.Rect em coordenadas do mundo, tag)."""
        owner_pos = self.owner.transform.pos
        result = []
        for col in self.colliders:
            if tag is None or col.tag == tag:
                result.append((col.get_world_rect(owner_pos), col.tag))
        return result

    def get_world_rects_by_tag(self, tag: ColliderTagEnum) -> list[pygame.Rect]:
        """Retorna apenas os Rects que possuem a tag especificada."""
        owner_pos = self.owner.transform.pos
        return [
            col.get_world_rect(owner_pos) for col in self.colliders if col.tag == tag
        ]

    def collides_with(
        self,
        other: "ColliderComponent",
        my_tag: ColliderTagEnum | None = None,
        other_tag: ColliderTagEnum | None = None,
    ) -> bool:
        if not self.active or not other.active:
            return False

        my_rects = (
            self.get_world_rects_by_tag(my_tag)
            if my_tag is not None
            else [
                col.get_world_rect(self.owner.transform.pos) for col in self.colliders
            ]
        )
        if not my_rects:
            return False

        other_rects = (
            other.get_world_rects_by_tag(other_tag)
            if other_tag is not None
            else [
                col.get_world_rect(other.owner.transform.pos) for col in other.colliders
            ]
        )
        if not other_rects:
            return False

        for r1 in my_rects:
            for r2 in other_rects:
                if r1.colliderect(r2):
                    return True
        return False

    def collides_with_rect(
        self, rect: pygame.Rect, my_tag: ColliderTagEnum | None = None
    ) -> bool:
        if not self.active:
            return False
        my_rects = (
            self.get_world_rects_by_tag(my_tag)
            if my_tag is not None
            else [
                col.get_world_rect(self.owner.transform.pos) for col in self.colliders
            ]
        )
        for r in my_rects:
            if r.colliderect(rect):
                return True
        return False

    def get_bounding_rect(self) -> pygame.Rect | None:
        """Retorna o retângulo envolvente de todos os colisores no mundo."""
        if not self.colliders:
            return None
        owner_pos = self.owner.transform.pos
        rects = [col.get_world_rect(owner_pos) for col in self.colliders]
        bounding = rects[0].copy()
        for r in rects[1:]:
            bounding.union_ip(r)
        return bounding

    def update(self, dt: float):
        pass
