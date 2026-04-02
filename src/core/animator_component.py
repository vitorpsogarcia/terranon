from typing import List, Dict, Optional
import pygame


class AnimatorComponent:

    def __init__(self, owner: pygame.sprite.Sprite):
        self.owner = owner
        self.animations: Dict[str, Dict[str, object]] = {}
        self.current: Optional[str] = None
        self._frame_index: int = 0
        self._time_acc: float = 0.0

    def add_animation(self, state_name: str, frames_list: List[pygame.Surface], frame_duration: float):
        if not frames_list:
            raise ValueError("frames_list must contain at least one Surface")
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
        frames: List[pygame.Surface] = anim["frames"]
        duration: float = anim["duration"]

        if len(frames) <= 1:
            self._apply_frame()
            return

        self._time_acc += dt
        while self._time_acc >= duration:
            self._time_acc -= duration
            self._frame_index = (self._frame_index + 1) % len(frames)
        self._apply_frame()

    def _apply_frame(self):
        anim = self.animations.get(self.current)
        if not anim:
            return
        frames: List[pygame.Surface] = anim["frames"]
        frame = frames[self._frame_index % len(frames)]
        prev_rect = getattr(self.owner, "rect", None)
        prev_center = prev_rect.center if prev_rect else None

        self.owner.image = frame
        if prev_center:
            self.owner.rect = self.owner.image.get_rect(center=prev_center)
        else:
            self.owner.rect = self.owner.image.get_rect()