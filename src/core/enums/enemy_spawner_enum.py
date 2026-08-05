from enum import Enum


class EnemySpawnerEnum(Enum):
    SPWN_ALPHA = "SPWN_ALPHA"
    SPWN_BETA = "SPWN_BETA"
    SPWN_GAMA = "SPWN_GAMA"
    SPWN_DELTA = "SPWN_DELTA"

    @classmethod
    def to_list(cls) -> list[str]:
        return [member.value for member in cls]
