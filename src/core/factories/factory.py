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
            cls._instance.world = world
            return cls._instance
        cls._instance = cls(world)
    
    @classmethod
    def reset(cls):
        cls._instance = None