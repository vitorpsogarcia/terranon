import logging

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.exceptions.asset_not_found_exception import AssetNotFoundException
from core.manager.asset_manager import AssetManager
from core.manager.event_manager import EventManager
from core.settings.settings import ASSETS_FOLDER
from core.singleton_meta import SingletonMeta


class SoundManager(metaclass=SingletonMeta):
    _instance = None
    _logger = logging.getLogger("SoundManager")

    def __init__(self):
        pygame.mixer.init()

        self.volumes: dict[str, float] = {"master": 1.0, "music": 1.0, "sfx": 0.8}

        self._sfx_counts: dict[str, int] = {}

        EventManager().subscribe(GameEventEnum.PLAY_SFX, self._on_play_sfx)
        EventManager().subscribe(GameEventEnum.PLAY_MUSIC, self._on_play_music)
        EventManager().subscribe(GameEventEnum.STOP_MUSIC, self._on_stop_music)

    def _on_play_sfx(self, filename: str):
        self.play_sfx(filename)

    def _on_play_music(self, filename: str, loops: int = -1, fade_ms: int = 1000):
        self.play_music(filename, loops, fade_ms)

    def _on_stop_music(self, fade_ms: int = 500):
        self.stop_music(fade_ms)

    def play_music(self, filename: str, loops: int = -1, fade_ms: int = 1000):
        try:
            music_path = ASSETS_FOLDER / "sounds" / "music" / filename

            if not music_path.exists():
                self._logger.warning(f"Musica '{filename}' não foi encontrada. Verifique o caminho: {music_path}")
                return
            
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(
                self.volumes["music"] * self.volumes["master"]
            )
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            
        except Exception as e:
            self._logger.error(f"Erro ao tocar música '{filename}': {e}")

    def play_sfx(self, filename: str):
        sound = AssetManager().get_sound(filename)

        if filename not in self._sfx_counts:
            self._sfx_counts[filename] = 0

        if self._sfx_counts[filename] < 3:
            sound.set_volume(self.volumes["sfx"] * self.volumes["master"])
            self._sfx_counts[filename] += 1
        elif self._sfx_counts[filename] >= 3:
            self._sfx_counts[filename] = 0
        else:
            return

        channel = sound.play()
        if channel:
            channel.set_endevent(pygame.event.custom_type())

    def stop_music(self, fade_ms: int = 500):
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except Exception as e:
            self._logger.error(f"Erro ao parar música: {e}")

    def set_volume(self, category: str, volume: float):
        if category in self.volumes:
            self.volumes[category] = max(0.0, min(1.0, volume))
            if category in ["music", "master"]:
                pygame.mixer.music.set_volume(
                    self.volumes["music"] * self.volumes["master"]
                )
        else:
            raise ValueError(f"Categoria de volume '{category}' não é válida.")
