import pygame

from core.components.static_render_component import StaticRenderComponent
from core.game_object import StaticObject
from core.manager.asset_manager import AssetManager


class Obstacle(StaticObject):
    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        width: float = 64,
        height: float = 64,
        image: pygame.Surface | None = None,
    ):
        super().__init__(position, *groups)
        self.hitbox = pygame.Rect(
            round(self.pos.x), round(self.pos.y), int(width), int(height)
        )
        self.rect = self.hitbox
        self.relative_hitboxes = [pygame.Rect(0, 0, int(width), int(height))]

        if image is not None:
            self.image = image
        else:
            self.image = AssetManager().load_image(
                name=f"obstacle_fallback_{int(width)}_{int(height)}",
                path="Tower_gun.png",
                size=(int(width), int(height)),
            )

        self.render_component = StaticRenderComponent(self, self.image)

