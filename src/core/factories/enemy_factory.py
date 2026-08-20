import pygame

from core.enums.enemy_enum import EnemyEnum
from core.exceptions.enemy_type_not_found_exception import EnemyTypeNotFoundException
from core.map.waypoints.polyline import Polyline
from core.singleton_meta import SingletonMeta
from entities.character.goblin import Goblin


class EnemyFactory(metaclass=SingletonMeta):
    def __init__(self):
        self._registry: dict[EnemyEnum, object] = {
            EnemyEnum.GOBLIN: Goblin,
        }

    def get_enemy_by_type(self, enemy_type: EnemyEnum):
        if enemy_type not in self._registry:
            raise EnemyTypeNotFoundException(enemy_type)
        return self._registry.get(enemy_type)

    def create_enemy(
        self, enemy_type: EnemyEnum, position: pygame.Vector2, path: Polyline
    ):
        enemy_class = EnemyFactory().get_enemy_by_type(enemy_type)

        if enemy_class is None:
            raise EnemyTypeNotFoundException(enemy_type)

        return enemy_class(position, path=path)
