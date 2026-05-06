from core.factories.projectile_factory import ProjectileFactory
from core.game_world import GameWorld


class FactoriesLoader():
    def __init__(self, world: GameWorld):
        self.world = world
        ProjectileFactory.initialize(self.world)