from core.enums.enemy_enum import EnemyEnum


class EnemyTypeNotFoundException(Exception):
    def __init__(self, enemy_type: EnemyEnum):
        super().__init__(f"Enemy of type {enemy_type.value} not exists")