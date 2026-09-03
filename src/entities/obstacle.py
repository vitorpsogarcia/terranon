import pygame

from core.components.collider_component import ColliderComponent
from core.components.static_render_component import StaticRenderComponent
from core.enums.collider_tag_enum import ColliderTagEnum
from core.game_object import GameObject


class Obstacle(GameObject):
    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        width: float = 0,
        height: float = 0,
    ):
        super().__init__(position, *groups)

        surface = pygame.Surface((width, height)).convert_alpha()
        surface.fill((255, 0, 0))
        self.render_component = StaticRenderComponent(self, surface)
        self.render_component.render_layer = 2  # Substitui o layer 2 do StaticObject

        self.collider = ColliderComponent(self)
        if width > 0 and height > 0:
            self.collider.add_box(0, 0, width, height, tag=ColliderTagEnum.SOLID)
