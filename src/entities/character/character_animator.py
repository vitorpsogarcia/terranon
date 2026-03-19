from pathlib import Path

import pygame

from core.settings import ASSETS_FOLDER, DIRECTIONS
from utils.image import load_image

class CharacterAnimator:
    def __init__(self, char_name: str, frame_width: int, frame_height: int):
        self._last_direction = "S"
        self._state = "idle"
        self._frame_index = 0.0
        self.animation_speed = 10.0
        self._sprites_path = ASSETS_FOLDER / "images" / char_name
        self.sprites = self._get_sprites(self._sprites_path, frame_width, frame_height)
        
    def update(self, dt: float, state: str, direction: str):
        if self._state != state or self._last_direction != direction:
            self._frame_index = 0.0
            
        self._state = state
        self._last_direction = direction
        
        if self._state == "running":
            self._frame_index += self.animation_speed * dt
            if self._frame_index >= 8:
                self._frame_index = 0.0
        else:
            self._frame_index = 0.0

    def get_frame(self) -> pygame.Surface:
        direction = self._last_direction
        if direction not in self.sprites:
            direction = "S"
            
        anim_list = self.sprites[direction]
        if isinstance(anim_list, pygame.Surface):
            return anim_list
            
        if self._state == "idle":
            return anim_list[0]
        else:
            frame = int(self._frame_index) + 1
            if frame > 8: 
                frame = 1
            return anim_list[frame]

    @staticmethod
    def _get_sprites(_sprites_path: Path, frame_width: int, frame_height: int):
        sprites = {}
        for direction in DIRECTIONS:
            try:
                sprites_dir = []
                sprites_dir.append(load_image(_sprites_path / "idle" / f"{direction}.png").convert_alpha())
                for i in range(0, 8):
                    sprites_dir.append(load_image(_sprites_path / "animations" / "running" / direction / f"{i}.png").convert_alpha())
                sprites[direction] = sprites_dir
            except FileNotFoundError:
                placeholder = pygame.Surface((frame_width, frame_height)).convert_alpha()
                placeholder.fill((255, 0, 0))
                sprites[direction] = placeholder
        
        return sprites