
import pygame

from core.game_object import GameObject


class AnimatorComponent:

    def __init__(self, owner: GameObject):
        self.owner = owner
        self.animations: dict[str, dict[str, object]] = {}
        self.current: str | None = None
        self._frame_index: int = 0
        self._time_acc: float = 0.0
        self._angle = 0

    def add_animation(self, state_name: str, frames_list: list[pygame.Surface], frame_duration: float):
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
        prev_rect = getattr(self.owner, "rect", None)
        prev_center = prev_rect.center if prev_rect else None

        frame = pygame.transform.rotate(frame, self._angle)

        self.owner.image = frame
        if prev_center:
            self.owner.rect = self.owner.image.get_rect(center=prev_center)
        else:
            self.owner.rect = self.owner.image.get_rect()
    
    def set_angle(self, angle: float):
        self._angle = angle
        if self.current is not None:
            self._apply_frame()