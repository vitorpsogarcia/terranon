from enum import Enum


class WaypointsEnum(Enum):
    PLAYER_SPAWNPOINT = 'player_spawnpoint'
    BASE = 'base'


    @staticmethod
    def get_by_text(text: str):
        for enum in WaypointsEnum:
            if enum.value == text:
                return enum
        return None