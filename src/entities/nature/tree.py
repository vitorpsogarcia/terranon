import pygame

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
        self.relative_hitboxes = hitboxes

        self.image = AssetManager.get_image(self._type)
        self.rect = self.image.get_rect(topleft=initial_position)
