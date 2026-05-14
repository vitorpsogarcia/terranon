from ast import Dict

import pygame

from core.asset_manager import AssetManager
from core.exceptions.asset_not_found_exception import AssetNotFoundException
from core.settings.settings import ASSETS_FOLDER
from typing import Dict

class SoundManager:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        pygame.mixer.init()

        self.volumes: Dict[str, float] = {
            "master": 1.0,
            "music": 1.0,
            "sfx": 0.8
        }

        self._sfx_counts: Dict [str, int] = {}
        self._initialized = True

    def play_music(self, filename: str, loops: int = -1, fade_ms: int = 1000):
        try:
            music_path = ASSETS_FOLDER / "sounds" / "music" / filename
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.volumes["music"] * self.volumes["master"])
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
        except Exception as e:
            raise AssetNotFoundException(f"Musica '{filename}' não foi encontrada.") from e
        
    def play_sfx(self, filename: str):
        sound = AssetManager.get_sound(filename)

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
        pygame.mixer.music.fadeout(fade_ms)

    def set_volume(self, category: str, volume: float):
        if category in self.volumes:
            self.volumes[category] = max(0.0, min(1.0, volume))
            if category in ["music", "master"]:
                pygame.mixer.music.set_volume(self.volumes["music"] * self.volumes["master"])
        else:
            raise ValueError(f"Categoria de volume '{category}' não é válida.")
        