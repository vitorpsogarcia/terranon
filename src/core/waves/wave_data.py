from dataclasses import dataclass, field

from core.enums.enemy_spawner_enum import EnemySpawnerEnum


@dataclass(frozen=True)
class WaveData:
    """Estrutura de dados contendo os parâmetros de configuração de uma onda."""

    wave_number: int
    total_enemies: int
    enemy_points: int
    active_spawners: list[EnemySpawnerEnum] = field(default_factory=list)
    duration: float = 60.0
    interval_duration: float = 30.0

