from pathlib import Path

import pygame

from core.asset_manager import AssetManager
from core.enums.character_state_enum import CharacterStateEnum
from core.settings.settings import DIRECTIONS

class CharacterAnimator:
    _state: CharacterStateEnum
    
    def __init__(self, char_name: str, scale: float = 1.0, default_speed: float = 5.0):
        self._last_direction = "S"
        self._state = CharacterStateEnum.IDLE
        self._frame_index = 0.0
        self._relative_path = Path(char_name)
        
        self.char_name = char_name
        self.animation_speed = default_speed

        self._get_sprites(self._relative_path, char_name, scale=scale)

    def set_speed(self, speed: float):
        self.animation_speed = speed
    
        
    def update(self, dt: float, state: CharacterStateEnum, direction: str):
        if self._state != state or self._last_direction != direction:
            self._frame_index = 0.0
            
        self._state = state
        self._last_direction = direction
        
        if self._state == CharacterStateEnum.MOVING:
            self._frame_index += self.animation_speed * dt
            if self._frame_index >= 8:
                self._frame_index = 0.0
        else:
            self._frame_index = 0.0

    def get_frame(self) -> pygame.Surface:
        direction = self._last_direction
            
        if self._state == CharacterStateEnum.IDLE:
            return AssetManager().get_image(f"{self.char_name}.{CharacterStateEnum.IDLE.value}.{direction}")
        else:
            frame = int(self._frame_index)
            if frame > 7: 
                frame = 1
            return AssetManager().get_image(f"{self.char_name}.{CharacterStateEnum.MOVING.value}.{direction}.{frame}")


    @staticmethod
    def _get_sprites(_sprites_path: Path, char_name: str, scale: float = 1) -> None:
        for direction in DIRECTIONS:
            AssetManager().load_image(f"{char_name}.idle.{direction}", str(_sprites_path / CharacterStateEnum.IDLE.value / f"{direction}.png"), scale=scale)
            for i in range(0, 8):
                path = _sprites_path / "animations" / CharacterStateEnum.MOVING.value / direction / f"{i}.png"
                AssetManager().load_image(f"{char_name}.{CharacterStateEnum.MOVING.value}.{direction}.{i}", str(path), scale=scale)
                
        