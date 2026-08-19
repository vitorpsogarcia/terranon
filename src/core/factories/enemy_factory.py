from typing import ClassVar

import pygame

from core.enums.enemy_enum import EnemyEnum
from core.exceptions.enemy_type_not_found_exception import EnemyTypeNotFoundException
from core.map.waypoints.polyline import Polyline
from entities.character.goblin import Goblin
from entities.enemy import Enemy


class EnemyFactory:
    _instance = None
    _registry: ClassVar[dict[EnemyEnum, object]] = {
        EnemyEnum.GOBLIN: Goblin,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_enemy_by_type(cls, enemy_type: EnemyEnum):
        if enemy_type not in cls._registry:
            raise EnemyTypeNotFoundException(enemy_type)
        return cls._registry.get(enemy_type)

    @classmethod
    def create_enemy(
        cls, enemy_type: EnemyEnum, position: pygame.Vector2, path: Polyline
    ):
        enemy_class = EnemyFactory.get_enemy_by_type(enemy_type)

        if enemy_class is None:
            raise EnemyTypeNotFoundException(enemy_type)

        return enemy_class(position, path=path)
