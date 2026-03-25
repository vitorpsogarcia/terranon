import pygame
from core.game_object import StaticObject

class Obstacle(StaticObject):
    def __init__(self, x: float, y: float, width: int = 64, height: int = 64, *groups: pygame.sprite.Group  ):
        super().__init__(x, y, *groups)
        self.image = pygame.Surface((width, height)).convert_alpha()
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(round(x), round(y)))
