from enum import Enum


class GameEventEnum(Enum):
    SPAWN_PROJECTILE = "SPAWN_PROJECTILE"
    PLAY_SFX = "PLAY_SFX"
    ENEMY_DIED = "ENEMY_DIED"
    GAME_OVER = "GAME_OVER"
    WAVE_STARTED = "WAVE_STARTED"
    WAVE_ENDED = "WAVE_ENDED"

    def __str__(self):
        return self.value
    
    @staticmethod
    def to_list():
        return list(GameEventEnum)
    