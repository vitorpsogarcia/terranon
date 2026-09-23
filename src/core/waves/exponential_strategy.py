from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.waves.wave_data import WaveData
from core.waves.wave_strategy import IWaveStrategy


class ExponentialWaveStrategy(IWaveStrategy):
    """Estratégia exponencial com base de 1.1x e ativação progressiva de ninhos.

    Baseado nas regras canônicas de estrutura_waves.csv:
    - Multiplicador de inimigos: 1.1 por onda (partindo de 3 na onda 1).
    - Pontos por inimigo: 5 pts (W1-W4), 6 pts (W5-W9), 7 pts (W10-W14), 8 pts (W15+).
    - Ativação de spawners: BETA (W1+), ALPHA (W5+), GAMA (W10+), DELTA (W15+).
    - Duração da onda: 60s.
    - Duração do intervalo: 30s.
    """

    def __init__(
        self,
        base_enemies: int = 3,
        multiplier: float = 1.1,
        wave_duration: float = 60.0,
        interval_duration: float = 30.0,
    ):
        self.base_enemies = base_enemies
        self.multiplier = multiplier
        self.wave_duration = wave_duration
        self.interval_duration = interval_duration

    def generate_wave(self, wave_number: int) -> WaveData:
        w = max(1, wave_number)

        # Cálculo da quantidade de inimigos (exponencial composta)
        total_enemies = max(1, round(self.base_enemies * (self.multiplier ** (w - 1))))

        # Cálculo da pontuação por inimigo (degraus nas waves 5, 10 e 15)
        points_bonus = (1 if w >= 5 else 0) + (1 if w >= 10 else 0) + (1 if w >= 15 else 0)
        enemy_points = min(8, 5 + points_bonus)

        # Spawners ativados progressivamente
        spawners: list[EnemySpawnerEnum] = [EnemySpawnerEnum.SPWN_BETA]
        if w >= 5:
            spawners.append(EnemySpawnerEnum.SPWN_ALPHA)
        if w >= 10:
            spawners.append(EnemySpawnerEnum.SPWN_GAMA)
        if w >= 15:
            spawners.append(EnemySpawnerEnum.SPWN_DELTA)

        return WaveData(
            wave_number=w,
            total_enemies=total_enemies,
            enemy_points=enemy_points,
            active_spawners=spawners,
            duration=self.wave_duration,
            interval_duration=self.interval_duration,
        )

