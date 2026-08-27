import pygame

from core.enums.enemy_enum import EnemyEnum
from core.enums.game_event_enum import GameEventEnum
from core.factories.enemy_factory import EnemyFactory
from core.game_object import StaticObject
from core.manager.event_manager import EventManager
from core.map.waypoints.polyline import Polyline
from core.components.null_render_component import NullRenderComponent


class EnemySpawner(StaticObject):
    def __init__(
        self,
        spawner_id: str,
        position: pygame.Vector2,
        path: Polyline,
        spawn_interval: float = 5.0,
        *groups: pygame.sprite.Group,
    ):
        super().__init__(position, *groups)
        self.spawner_id = spawner_id
        self.path = path
        self.render_component = NullRenderComponent(self)

    def update(self, dt: float):
        super().update(dt)

    def spawn_enemy(self, enemy_type: EnemyEnum = EnemyEnum.GOBLIN):
        new_enemy = EnemyFactory.create_enemy(enemy_type, self.pos, self.path)
        EventManager.get_instance().emit(GameEventEnum.ENEMY_SPAWNED, new_enemy)
