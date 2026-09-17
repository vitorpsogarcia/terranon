from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.enums.upgrade_type_enum import UpgradeTypeEnum


if TYPE_CHECKING:
    from entities.character.player import Player
    from core.wave_manager import WaveManager
    from core.manager.economy_manager import EconomyManager

@dataclass
class GameContext:
    wave_manager: "WaveManager | None" = None
    economy_manager: "EconomyManager | None" = None

class Upgrade:
    def __init__(self, upgrade_type: UpgradeTypeEnum, title: str, description: str, is_unique: bool = False, max_stacks: int | None = None):
        self.type = upgrade_type
        self.title = title
        self.description = description
        self.is_unique = is_unique
        self.max_stacks = max_stacks
        self.current_stacks: int = 0

    def can_appear(self, player: "Player", context: GameContext) -> bool:
        if self.is_unique and self.current_stacks > 0:
            return False
        if self.max_stacks is not None and self.current_stacks > self.max_stacks:
            return False


        if self.type == UpgradeTypeEnum.UNLOCK_SHIELD:
            return not player.has_shield
        elif self.type == UpgradeTypeEnum.SHIELD_CAPACITY_UP:
            return player.has_shield
        elif self.type == UpgradeTypeEnum.DAMAGE_REDUCTION:
            return player.health.damage_reduction < player.health.max_damage_reduction

        return True


    def apply(self, player: "Player", context: GameContext) -> None:
        if self.type == UpgradeTypeEnum.MAX_HP_UP:
            player.health.max_hp += 5.0
            player.health.heal(5.0)
        elif self.type == UpgradeTypeEnum.UNLOCK_SHIELD:
            player.shield.unlock(initial_shield=10.0, max_shield=10.0)
        elif self.type == UpgradeTypeEnum.SHIELD_CAPACITY_UP:
            player.shield.max_shield += 5.0
            player.shield.current_shield += 5.0
        elif self.type == UpgradeTypeEnum.BULLET_DAMAGE_UP:
            player.bullet_damage += 5.0
        elif self.type == UpgradeTypeEnum.DAMAGE_REDUCTION:
            player.health.damage_reduction = min(player.health.max_damage_reduction, player.health.damage_reduction + 0.05)
        elif self.type == UpgradeTypeEnum.COIN_GAIN_UP:
            if context.economy_manager:
                context.economy_manager.bonus_multiplier += 0.05
        elif self.type == UpgradeTypeEnum.ENEMY_SPEED_DOWN:
            from core.factories.enemy_factory import EnemyFactory
            EnemyFactory.speed_multiplier = max(0.2, EnemyFactory.speed_multiplier - 0.05)
        elif self.type == UpgradeTypeEnum.SPAWN_INTERVAL_UP:
            if context.wave_manager:
                context.wave_manager.spawn_delay +=2.0