import pygame

from core.enums.directions_enum import DirectionsEnum
from core.map.waypoints.polyline import Polyline
from core.settings.settings import ASSETS_FOLDER
from entities.enemy import Enemy
from utils.image import load_image


class Goblin(Enemy):
    def __init__(self, pos: pygame.Vector2, path: Polyline, *groups):
        super().__init__(pos, path, *groups, speed=80, max_hp=20)

        self.damage = 5.0
        self.scale = 0.1

        self._last_direction = DirectionsEnum.NORTH
        self.last_direction = self._last_direction.text
        self.current_state = "walking"
        self._current_anim = f"walking_{self._last_direction.text}"
        self._setup_animations()
        self.animator.play(self._current_anim)
        self.animator.update(0.0)

    def update(self, dt: float):
        super().update(dt)
        new_anim_name = f"{self.current_state}_{self.last_direction}"

        if self._current_anim != new_anim_name:
            self._current_anim = new_anim_name
            self.animator.play(self._current_anim)

    def _setup_animations(self):
        goblin_root = ASSETS_FOLDER / "images" / "goblin-pack" / "frames"

        for direction in DirectionsEnum.four_direction_list():
            direction_value = direction.text
            running_dir = goblin_root / direction_value

            idle_frame = None
            running_frames = []

            for i in range(6):
                image_path = running_dir / f"{i}.png"
                try:
                    image = load_image(image_path, scale=self.scale)
                    if i == 0:
                        idle_frame = image
                    else:
                        running_frames.append(image)
                except FileNotFoundError:
                    break

            move_frames = running_frames if running_frames else [idle_frame]

            self.animator.add_animation(
                f"idle_{direction_value}", [idle_frame], frame_duration=1.0
            )
            self.animator.add_animation(
                f"walking_{direction_value}", move_frames, frame_duration=1 / 7.0
            )
