import pygame

from core.components.collider_component import ColliderComponent
from core.components.static_render_component import StaticRenderComponent
from core.enums.collider_tag_enum import ColliderTagEnum
from core.game_object import GameObject
from core.manager.asset_manager import AssetManager


class Obstacle(GameObject):
    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        width: float = 64,
        height: float = 64,
        image: pygame.Surface | None = None,
        default_hitbox: bool = True,
    ):
        super().__init__(position, *groups)

        if image is not None:
            self.image = image
        else:
            self.image = AssetManager().load_image(
                name=f"obstacle_fallback_{int(width)}_{int(height)}",
                path="Tower_gun.png",
                size=(int(width), int(height)),
            )

        self.render_component = StaticRenderComponent(self, self.image)
        self.render_component.render_layer = 2

        self.collider = ColliderComponent(self)
        if default_hitbox and width > 0 and height > 0:
            self.collider.add_box(0, 0, width, height, tag=ColliderTagEnum.SOLID)
