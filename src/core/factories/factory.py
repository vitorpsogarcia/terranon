from core.game_world import GameWorld


class Factory:
    _instance = None

    def __init__(self, world: GameWorld):
        self.world = world


    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError(f"{cls.__name__} has not been initialized.")
        return cls._instance
    
    @classmethod
    def initialize(cls, world: GameWorld):
        if getattr(cls, "_instance", None) is not None:
            raise ValueError(f"{cls.__name__} has already been initialized.")
        cls._instance = cls(world)