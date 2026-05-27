import pygame
from core.game_object import DynamicObject
from core.animator_component import AnimatorComponent
from core.health_component import HealthComponent
from core.enums.game_event_enum import GameEventEnum
from core.event_manager import EventManager


class Character(DynamicObject):
    def __init__(self, x: float, y: float, speed: float = 100.0, *groups: pygame.sprite.Group):
        super().__init__(x, y, *groups)
        self.animator = AnimatorComponent(self)
        self.health = HealthComponent(max_hp=100.0, on_death_callback=self.on_death, iframes_duration=0.5)
        self.speed = speed
        self.direction = pygame.math.Vector2(0, 0)

    def move(self, dt: float):
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.velocity = self.direction * self.speed

    def update(self, dt: float):
        if not self.active:
            return
        
        self.health.update(dt)
        self.move(dt)
        self.animator.update(dt)
        super().update(dt)

    def on_death(self):
        EventManager.get_instance().emit(GameEventEnum.PLAY_SFX, "effects/death.mp3")
        self.active = False
        self.kill()
