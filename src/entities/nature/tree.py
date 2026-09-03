import pygame

from core.components.collider_component import ColliderComponent
from core.components.static_render_component import StaticRenderComponent
from core.enums.collider_tag_enum import ColliderTagEnum
from core.manager.asset_manager import AssetManager
from entities.obstacle import Obstacle


class Tree(Obstacle):
    def __init__(
        self,
        initial_position: pygame.Vector2,
        type: str,
        hitboxes: list[pygame.Rect],
        *groups: pygame.sprite.Group,
    ):
        super().__init__(initial_position, *groups)
        self._type = type
        image = AssetManager().get_image(self._type)
        self.render_component = StaticRenderComponent(self, image)
        self.relative_hitboxes = hitboxes
        self.collider = ColliderComponent(self)
        for r in hitboxes:
            self.collider.add_box(
                r.x, r.y, r.width, r.height, tag=ColliderTagEnum.SOLID
            )
