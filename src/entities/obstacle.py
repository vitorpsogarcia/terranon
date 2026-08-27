import pygame

from core.game_object import StaticObject
from core.components.static_render_component import StaticRenderComponent


class Obstacle(StaticObject):
    def __init__(self, position: pygame.Vector2, *groups: pygame.sprite.Group, width: int = 64, height: int = 64,):
        super().__init__(position, *groups)
        fallback_image = pygame.Surface((width, height)).convert_alpha()
        fallback_image.fill((255, 0, 0))
        self.render_component = StaticRenderComponent(self, fallback_image)
