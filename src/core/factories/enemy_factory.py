from typing import ClassVar
import pygame
from core.enums.enemy_enum import EnemyEnum
from core.exceptions.enemy_type_not_found_exception import EnemyTypeNotFoundException
from core.map.waypoints.polyline import Polyline
from entities.character.goblin import Goblin


class EnemyFactory:
    _registry: dict[EnemyEnum, object] = {
        EnemyEnum.GOBLIN: Goblin,
    }

    @classmethod
    def preload_all_enemies(cls):
        """Varre as classes registradas e faz o cache das imagens via AssetManager."""
        for enemy_class in cls._registry.values():
            if hasattr(enemy_class, "preload_assets"):
                enemy_class.preload_assets()
    @classmethod
    def get_enemy_by_type(cls, enemy_type: EnemyEnum):
        if enemy_type not in cls._registry:
            raise EnemyTypeNotFoundException(enemy_type)
        return cls._registry.get(enemy_type)


    @classmethod
    def create_enemy(
        cls, enemy_type: EnemyEnum, position: pygame.Vector2, path: Polyline
    ):
        enemy_class = cls.get_enemy_by_type(enemy_type)

        if enemy_class is None:
            raise EnemyTypeNotFoundException(enemy_type)

        return enemy_class(position, path=path)
