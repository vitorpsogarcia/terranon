import logging

import pygame

from core.enums.directions_enum import DirectionsEnum
from core.manager.asset_manager import AssetManager
from core.map.waypoints.polyline import Polyline
from core.settings.settings import GOBLIN_SCALE
from entities.enemy import Enemy

logger = logging.getLogger("Goblin")


class Goblin(Enemy):
    def __init__(self, pos: pygame.Vector2, path: Polyline, *groups):
        super().__init__(pos, path, *groups, speed=80, max_hp=20)
        self.damage = 5.0
        self.scale = GOBLIN_SCALE
        self._last_direction = DirectionsEnum.NORTH
        self.last_direction = self._last_direction.text
        self.current_state = "walking"
        self._current_anim = f"walking_{self._last_direction.text}"
        self._setup_animations()
        self.animator.play(self._current_anim)
        self.animator.update(0.0)

    @classmethod
    def preload_assets(cls):
        """Carrega e salva os frames do Goblin no AssetManager"""
        escala_goblin = GOBLIN_SCALE

        for direction in DirectionsEnum.four_direction_list():
            dir_val = direction.text

            for i in range(6):
                image_path = f"goblin-pack/frames/{dir_val}/{i}.png"
                asset_name = f"goblin_{dir_val}_{i}"

                try:
                    AssetManager().load_image(
                        name=asset_name, path=image_path, scale=escala_goblin
                    )
                except Exception:
                    logger.warning(f"Falha ao carregar a imagem: {image_path}")

    def update(self, dt: float):
        super().update(dt)
        new_anim_name = f"{self.current_state}_{self.last_direction}"

        if self._current_anim != new_anim_name:
            self._current_anim = new_anim_name
            self.animator.play(self._current_anim)

    def _setup_animations(self):
        """Busca as imagens prontas na RAM (AssetManager) para criar as animações"""
        for direction in DirectionsEnum.four_direction_list():
            dir_val = direction.text

            idle_frame = None
            running_frames = []

            for i in range(6):
                asset_name = f"goblin_{dir_val}_{i}"
                try:
                    image = AssetManager().get_image(asset_name)
                    if i == 0:
                        idle_frame = image
                    else:
                        running_frames.append(image)
                except Exception:
                    break

            move_frames = running_frames if len(running_frames) > 0 else None

            if idle_frame is not None:
                self.animator.add_animation(
                    f"idle_{dir_val}", [idle_frame], frame_duration=1.0
                )
            if move_frames is not None:
                self.animator.add_animation(
                    f"walking_{dir_val}", move_frames, frame_duration=1 / 7.0
                )
