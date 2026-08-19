from enum import Enum


class GameEventEnum(Enum):
    PLAY_SFX = "PLAY_SFX"
    PLAY_MUSIC = "PLAY_MUSIC"
    GAME_OVER = "GAME_OVER"

    WAVE_STARTED = "WAVE_STARTED"
    WAVE_ENDED = "WAVE_ENDED"

    ENEMY_SPAWNED = "ENEMY_SPAWNED"
    ENEMY_KILLED = "ENEMY_KILLED"
    SPAWN_PROJECTILE = "SPAWN_PROJECTILE"
    SPEND_POINTS = "SPEND_POINTS"
    RESET_WAVES = "RESET_WAVES"

    def __str__(self):
        return self.value

    @staticmethod
    def to_list():
        return list(GameEventEnum)
