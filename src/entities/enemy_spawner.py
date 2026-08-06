
import pygame

from core.enums.enemy_enum import EnemyEnum
from core.enums.game_event_enum import GameEventEnum
from core.event_manager import EventManager
from core.game_object import StaticObject
from core.map.waypoints.polyline import Polyline
from entities.enemy_factory import EnemyFactory


class EnemySpawner(StaticObject):
    def __init__(self, spawner_id: str, position: pygame.Vector2 , path: Polyline,  *groups: pygame.sprite.Group, spawn_interval: float = 5.0,):
        super().__init__(position, *groups)
        self.spawner_id = spawner_id
        self.path = path
        self.image = pygame.Surface((32, 32)).convert_alpha()
        self.image.fill((100, 0, 100)) 
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    def update(self, dt: float):
        super().update(dt)

    def spawn_enemy(self, enemy_type: str = "goblin"):
        if enemy_type == EnemyEnum.WEAK_BASIC:
            new_enemy_goblin = EnemyFactory.create_enemy(enemy_type, self.pos, self.path)
        else:
            new_enemy_goblin = Enemy(self.pos.x, self.pos.y, path=self.path)
            
        EventManager.get_instance().emit(GameEventEnum.ENEMY_SPAWNED, new_enemy_goblin)
