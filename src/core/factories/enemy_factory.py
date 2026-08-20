from typing import ClassVar
import pygame
from core.enums.enemy_enum import EnemyEnum
from core.exceptions.enemy_type_not_found_exception import EnemyTypeNotFoundException
from entities.character.goblin import Goblin
from entities.enemy import Enemy


class EnemyFactory:
    _instance = None
    _registry: ClassVar[dict[EnemyEnum, Enemy]] = {
        EnemyEnum.GOBLIN: Goblin
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Aciona o pré-carregamento dos assets na memória
            cls._instance._preload_all_enemies()
        return cls._instance

    def _preload_all_enemies(self):
        """Varre as classes registradas e faz o cache das imagens via AssetManager."""
        for enemy_class in self._registry.values():
            if hasattr(enemy_class, "preload_assets"):
                enemy_class.preload_assets()

    @classmethod
    def get_enemy_by_type(cls, enemy_type: EnemyEnum):
        if enemy_type not in cls._registry:
            raise EnemyTypeNotFoundException(enemy_type)
        return cls._registry.get(enemy_type)

    @classmethod
    def create_enemy(cls, enemy_type: EnemyEnum, position: pygame.Vector2, path: list):
        enemy_class = cls.get_enemy_by_type(enemy_type)
        return enemy_class(position, path=path)
