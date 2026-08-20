import pygame

from core.enums.game_event_enum import GameEventEnum
from core.game_object import GameObject
from core.health_component import HealthComponent
from core.manager.event_manager import EventManager
from core.settings.colors import Colors
from core.settings.settings import MAIN_BASE_SIZE
from entities.enemy import Enemy
from entities.obstacle import Obstacle


class MainBase(Obstacle):
    def __init__(self, position: pygame.Vector2, *groups: pygame.sprite.Group):

        # Ajusta a posição para o centro da base
        position.x = round(position.x - MAIN_BASE_SIZE / 2)
        position.y = round(position.y - MAIN_BASE_SIZE / 2)
        super().__init__(position, *groups, width=MAIN_BASE_SIZE, height=MAIN_BASE_SIZE)
        self._fixed_opacity = True

        self.image = pygame.Surface((MAIN_BASE_SIZE, MAIN_BASE_SIZE)).convert_alpha()
        self.image.fill(Colors.debug.base)

        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self.relative_hitboxes = [pygame.Rect(0, 0, MAIN_BASE_SIZE, MAIN_BASE_SIZE)]

        self.health = HealthComponent(max_hp=500.0, on_death_callback=self.on_death)

    def update(self, dt: float):
        self.health.update(dt)
        super().update(dt)

    def on_death(self):
        self.active = False
        self.kill()
        print("A BASE CAIU! GAME OVER!")
        EventManager.get_instance().emit(GameEventEnum.GAME_OVER)

    def on_collision(self, other: GameObject):
        if isinstance(other, Enemy):
            self.health.take_damage(other.health.current_hp)
            other.health.die()
