import pygame
from core.game_object import StaticObject
from core.health_component import HealthComponent


class BaseStructure(StaticObject):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        self.image = pygame.Surface((64, 64)).convert_alpha()
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=(round(x), round(y)))

        self.health = HealthComponent(
            max_hp=500.0, on_death_callback=self.on_death)

    def update(self, dt: float):
        self.health.update(dt)
        super().update(dt)

    def on_death(self):
        self.active = False
        self.kill()
        print("A BASE CAIU! GAME OVER!")
        
