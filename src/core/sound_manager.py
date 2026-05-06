import pygame

from core.exceptions.asset_not_found_exception import AssetNotFoundException
from core.settings.settings import ASSETS_FOLDER

class SoundManager:
    _instance = None

    @classmethod
    def play_background_music(cls, path: str, volume: float, loops: int = -1):
        try:
            music_path = ASSETS_FOLDER / "sounds/music" / path
            
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=loops)
        except (pygame.error, FileNotFoundError) as e:
            raise AssetNotFoundException(path, message=f"Erro ao carregar música: {e}")
        
    @classmethod
    def stop_background_music(cls):
        pygame.mixer.music.stop()