import pygame

from core.components.base_render_component import BaseRenderComponent
from core.component import Component
from core.game_object import GameObject


class AnimatorComponent(BaseRenderComponent, Component):  # 1. Herda do contrato base
    def __init__(self, owner: GameObject):
        super().__init__(owner)
        self.animations: dict[str, dict[str, object]] = {}
        self.current: str | None = None
        self._frame_index: int = 0
        self._time_acc: float = 0.0
        self._angle = 0
        self.current_frame: pygame.Surface | None = None

    def add_animation(
        self, state_name: str, frames_list: list[pygame.Surface], frame_duration: float
    ):
        if not frames_list:
            raise ValueError("frames_list deve conter pelo menos uma Surface")
        if frame_duration <= 0:
            raise ValueError("frame_duration deve ser maior que zero")
        self.animations[state_name] = {
            "frames": list(frames_list),
            "duration": float(frame_duration),
        }

    def play(self, state_name: str, reset: bool = True):
        if state_name == self.current:
            return
        if state_name not in self.animations:
            return
        self.current = state_name
        if reset:
            self._frame_index = 0
            self._time_acc = 0.0
        self._apply_frame()

    def update(self, dt: float):
        if self.current is None:
            return
        anim = self.animations.get(self.current)
        if not anim:
            return
        frames: list[pygame.Surface] = anim["frames"]
        duration: float = anim["duration"]

        if len(frames) <= 1:
            self._apply_frame()
            return

        self._time_acc += dt
        while self._time_acc >= duration:
            num_frames = int(self._time_acc // duration)
            self._time_acc %= duration
            self._frame_index = (self._frame_index + num_frames) % len(frames)
        self._apply_frame()

    def _apply_frame(self):
        if self.current is None:
            return
        anim = self.animations.get(self.current)
        if not anim:
            return
        frames: list[pygame.Surface] = anim["frames"]
        frame = frames[self._frame_index % len(frames)]

        if self._angle != 0:
            frame = pygame.transform.rotate(frame, self._angle)

        self.current_frame = frame

    def set_angle(self, angle: float):
        self._angle = angle
        if self.current is not None:
            self._apply_frame()

    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        if self.current_frame is None:
            return

        draw_rect = self.current_frame.get_rect(
            center=(
                round(self.owner.transform.pos.x),
                round(self.owner.transform.pos.y),
            )
        )

        draw_rect.topleft = (draw_rect.x - offset.x, draw_rect.y - offset.y)

        if self._opacity < 255:
            self.current_frame.set_alpha(self._opacity)
            surface.blit(self.current_frame, draw_rect)
            self.current_frame.set_alpha(255)
        else:
            surface.blit(self.current_frame, draw_rect)
