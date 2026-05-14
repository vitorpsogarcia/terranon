import pygame
from typing import List
from core.game_object import StaticObject
from entities.enemy import Enemy
from core.event_manager import EventManager
from core.enums.game_event_enum import GameEventEnum

class EnemySpawner(StaticObject):
    def __init__(self, spawner_id: str, x: float, y: float, path: List[pygame.math.Vector2], spawn_interval: float = 5.0):
        super().__init__(x, y)
        self.spawner_id = spawner_id
        self.path = path
        self.spawn_interval = spawn_interval
        self.spawn_timer = spawn_interval 
        self.image = pygame.Surface((32, 32)).convert_alpha()
        self.image.fill((100, 0, 100)) 
        self.rect = self.image.get_rect(center=(round(x), round(y)))

    def update(self, dt: float):
        super().update(dt)

        self.spawn_timer += dt

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0.0

    def spawn_enemy(self, enemy_type: str = "default"):
        new_enemy = Enemy(self.pos.x, self.pos.y, path=self.path)
        EventManager.get_instance().emit(GameEventEnum.ENEMY_SPAWNED, new_enemy)