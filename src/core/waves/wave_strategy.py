from abc import ABC, abstractmethod

from core.waves.wave_data import WaveData


class IWaveStrategy(ABC):
    """Interface para algoritmos de geração de parâmetros de ondas."""

    @abstractmethod
    def generate_wave(self, wave_number: int) -> WaveData:
        """Gera os parâmetros da onda especificada."""
        pass

