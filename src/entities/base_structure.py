import pygame
from core.enums.game_event_enum import GameEventEnum
from core.event_manager import EventManager
from core.game_object import StaticObject
from core.health_component import HealthComponent


class BaseStructure(StaticObject):
    def __init__(self, x: float, y: float):
        self.pos = pygame.math.Vector2(x, y)
        super().__init__(self.pos.x, self.pos.y)

        self.image = pygame.Surface((64, 64)).convert_alpha()
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(topleft=(round(self.pos.x), round(self.pos.y)))

        self.health = HealthComponent(
            max_hp=500.0, on_death_callback=self.on_death)

    def update(self, dt: float):
        self.health.update(dt)
        super().update(dt)

    def on_death(self):
        self.active = False
        self.kill()
        print("A BASE CAIU! GAME OVER!")
        EventManager.get_instance().emit(GameEventEnum.GAME_OVER)
        
