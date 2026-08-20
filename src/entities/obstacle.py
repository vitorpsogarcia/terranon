import pygame

from core.game_object import StaticObject


class Obstacle(StaticObject):
    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        width: float = 64,
        height: float = 64,
    ):
        super().__init__(position, *groups)
        self.image = pygame.Surface((width, height)).convert_alpha()
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(round(self.pos.x), round(self.pos.y)))

        self.relative_hitboxes = [pygame.Rect(0, 0, width, height)]
