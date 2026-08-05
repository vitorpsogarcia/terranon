import pygame

from core.game_object import StaticObject


class MapBackground(StaticObject):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface):
        super().__init__(position)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (position.x, position.y)
        self.render_layer = -1
        self._fixed_layer = True

    def update(self, dt: float):
        pass
