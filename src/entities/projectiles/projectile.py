from math import atan2, degrees
from pathlib import Path

import pygame
from pygame import Vector2

from core.components.animator_component import AnimatorComponent
from core.enums.projectile.projectile_types_enum import ProjectileTypesEnum
from core.enums.projectile.projectile_variant_enum import ProjectileVariantEnum
from core.game_object import DynamicObject, GameObject
from core.manager.asset_manager import AssetManager
from entities.enemy import Enemy


class Projectile(DynamicObject):
    def __init__(
        self,
        position: Vector2,
        direction: Vector2,
        speed: float = 100.0,
        damage: int = 10,
        lifetime: float = 2.0,
        type: ProjectileTypesEnum = ProjectileTypesEnum.NORMAL,
        variant: ProjectileVariantEnum = ProjectileVariantEnum.DEFAULT,
        friendly: bool = False,
        *groups: pygame.sprite.Group,
    ):
        super().__init__((position.x, position.y), *groups)
        self.animator = AnimatorComponent(self)
        self.friendly = friendly
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime
        self._type = type
        self._variant = variant
        self._name = f"projectile.{self._type.value}.{self._variant.variant_name}"

        self.rect = pygame.Rect(0, 0, 4, 4)
        self.rect.center = (round(position.x), round(position.y))

        self._setup_animations()

        self.animator.play(self._name)
        self.animator.update(0.0)

        angle_deg = degrees(atan2(-self.direction.y, self.direction.x))
        self.animator.set_angle(angle_deg)

    def _setup_animations(self):
        projectile_path = (
            Path("projectile") / self._type.value / self._variant.variant_name
        )

        frames: list[pygame.Surface] = []
        for i in range(self._variant.frames):
            frame_path = projectile_path / f"{i}.png"
            frame_name = f"{self._name}.{i}"
            frame = AssetManager.load_image(frame_name, str(frame_path), size=(20, 20))

            if frame is not None:
                frames.append(frame)

        self.animator.add_animation(self._name, frames, 1 / len(frames))

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

        self.pos += self.direction * self.speed * dt
        if self.rect:
            self.rect.center = (round(self.pos.x), round(self.pos.y))

        super().update(dt)
        self.animator.update(dt)

    def on_collision(self, other: GameObject):
        if other is None:
            return

        if isinstance(other, Enemy) and self.friendly:
            other.health.take_damage(self.damage)
            self.kill()
