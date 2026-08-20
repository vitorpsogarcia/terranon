from core.game_world import GameWorld
from core.singleton_meta import SingletonMeta


class Factory(metaclass=SingletonMeta):
    def __init__(self, world: GameWorld):
        self.world = world
