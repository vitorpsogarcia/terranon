from core.factories.enemy_factory import EnemyFactory
from core.factories.projectile_factory import ProjectileFactory
from core.game_world import GameWorld


class FactoriesLoader:
    def __init__(self, world: GameWorld):
        ProjectileFactory.initialize(world)
        EnemyFactory()