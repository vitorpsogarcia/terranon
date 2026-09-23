from enum import Enum


class WaveStateEnum(Enum):
    """Estados do ciclo de vida do sistema de ondas."""

    WARMUP = "WARMUP"  # Contagem regressiva antes da primeira onda (30s)
    ACTIVE = "ACTIVE"  # Onda em combate (até 60s)
    INTERVAL = "INTERVAL"  # Intervalo de preparação entre ondas (30s)

