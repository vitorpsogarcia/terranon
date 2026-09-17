import random
from typing import TYPE_CHECKING

from core.enums.game_event_enum import GameEventEnum
from core.enums.upgrade_type_enum import UpgradeTypeEnum
from core.manager.event_manager import EventManager
from core.singleton_meta import SingletonMeta
from core.upgrades.upgrades import GameContext, Upgrade

if TYPE_CHECKING:
    from entities.character.player import Player

class UpgradeManager(metaclass=SingletonMeta):
    def __init__(self):
        self.catalog: list[Upgrade] = []
        self.reset_catalog()

    def reset_catalog(self):
        self.catalog = [
            Upgrade(UpgradeTypeEnum.MAX_HP_UP, "Vida Máxima +5", "Aumenta a vida máxima em +5 PV e cura 5 PV.", is_unique=False),
            Upgrade(UpgradeTypeEnum.UNLOCK_SHIELD, "Escudo de Energia", "Desbloqueia e ativa um escudo protetor de 10 PE.", is_unique=True, max_stacks=1),
            Upgrade(UpgradeTypeEnum.SHIELD_CAPACITY_UP, "Capacidade do Escudo +5", "Aumenta a capacidade máxima do escudo em +5 PE.", is_unique=False),
            Upgrade(UpgradeTypeEnum.BULLET_DAMAGE_UP, "Projétil Poderoso +5", "Aumenta o dano base dos disparos em +5 PD.", is_unique=False),
            Upgrade(UpgradeTypeEnum.DAMAGE_REDUCTION, "Blindagem Corporal", "Reduz o dano recebido em 5% (Máx: 75%).", is_unique=False, max_stacks=15),
            Upgrade(UpgradeTypeEnum.COIN_GAIN_UP, "Bônus Econômico", "Aumenta o ganho de pontos por abate em +5%.", is_unique=False),
            Upgrade(UpgradeTypeEnum.ENEMY_SPEED_DOWN, "Lentidão nos Inimigos", "Reduz a velocidade de movimento dos novos inimigos em 5%.", is_unique=False),
            Upgrade(UpgradeTypeEnum.SPAWN_INTERVAL_UP, "Cadência de Invasão", "Reduz o intervalo de spawn dos inimigos em +2.0s.", is_unique=False),
        ]

    def get_random_upgrades(self, count: int, player: "Player", context: GameContext) -> list[Upgrade]:
        eligible = [u for u in self.catalog if u.can_appear(player, context)]
        if len(eligible) <= count:
            selected = eligible.copy()
        else:
            selected = random.sample(eligible, count)

        EventManager().emit(GameEventEnum.UPGRADE_OFFERED, upgrades=selected)
        return selected

    def select_upgrade(self, upgrade: Upgrade, player: "Player", context: GameContext) -> None:
        EventManager().emit(GameEventEnum.UPGRADE_SELECTED, upgrade=upgrade)
        upgrade.apply(player, context)
        upgrade.current_stacks += 1
        EventManager().emit(GameEventEnum.UPGRADE_APPLIED, upgrade=upgrade)