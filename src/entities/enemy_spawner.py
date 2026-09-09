import pygame

from core.components.static_render_component import StaticRenderComponent
from core.enums.enemy_enum import EnemyEnum
from core.enums.game_event_enum import GameEventEnum
from core.factories.enemy_factory import EnemyFactory
from core.game_object import GameObject
from core.manager.asset_manager import AssetManager
from core.manager.event_manager import EventManager
from core.map.waypoints.polyline import Polyline
from core.settings.settings import MAIN_BASE_SIZE


class EnemySpawner(GameObject):
    def __init__(
        self,
        spawner_id: str,
        position: pygame.Vector2,
        path: Polyline,
        spawn_interval: float = 5.0,
        *groups: pygame.sprite.Group,
    ):
        position.x = round(position.x - MAIN_BASE_SIZE / 2)
        position.y = round(position.y - MAIN_BASE_SIZE / 2)
        super().__init__(position, *groups)

        self.spawner_id = spawner_id
        self.path = path
        self.image = AssetManager().load_image(
            name="goblin_base",
            path="goblin_base.png",
            size=(MAIN_BASE_SIZE, MAIN_BASE_SIZE),
        )
        self.render_component = StaticRenderComponent(self, self.image)
        self.render_component.render_layer = 2

    def update(self, dt: float):
        super().update(dt)

    def spawn_enemy(self, enemy_type: EnemyEnum = EnemyEnum.GOBLIN):
        spawn_pos = self.render_component.center()
        new_enemy = EnemyFactory.create_enemy(enemy_type, spawn_pos, self.path)
        EventManager().emit(GameEventEnum.ENEMY_SPAWNED, new_enemy)
