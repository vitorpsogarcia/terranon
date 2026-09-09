from math import atan2, degrees
from pathlib import Path

import pygame
from pygame import Vector2

from core.components.animator_component import AnimatorComponent
from core.components.collider_component import ColliderComponent
from core.enums.collider_tag_enum import ColliderTagEnum
from core.enums.projectile.projectile_types_enum import ProjectileTypesEnum
from core.enums.projectile.projectile_variant_enum import ProjectileVariantEnum
from core.game_object import GameObject
from core.manager.asset_manager import AssetManager
from entities.enemy import Enemy


class Projectile(GameObject):
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
        super().__init__(position, *groups)
        self.animator = AnimatorComponent(self)
        self.render_component = self.animator
        self.friendly = friendly
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime
        self._type = type
        self._variant = variant
        self._name = f"projectile.{self._type.value}.{self._variant.variant_name}"

        self.collider = ColliderComponent(self)
        self.collider.add_box(
            -2, -2, 4, 4, tag=ColliderTagEnum.PROJECTILE, is_trigger=True
        )

        self._setup_animations()

        self.animator.play(self._name)
        self.animator.update(0.0)

        angle_deg = degrees(atan2(-self.direction.y, self.direction.x))
        self.animator.set_angle(angle_deg)

    @property
    def hitbox(self) -> pygame.Rect:
        return self.collider.get_bounding_rect() or pygame.Rect(
            round(self.transform.pos.x), round(self.transform.pos.y), 4, 4
        )

    @hitbox.setter
    def hitbox(self, value: pygame.Rect):
        pass

    @property
    def rect(self) -> pygame.Rect:
        return self.hitbox

    @rect.setter
    def rect(self, value: pygame.Rect):
        pass

    def _setup_animations(self):
        projectile_path = (
            Path("projectile") / self._type.value / self._variant.variant_name
        )

        frames: list[pygame.Surface] = []
        for i in range(self._variant.frames):
            frame_path = projectile_path / f"{i}.png"
            frame_name = f"{self._name}.{i}"
            frame = AssetManager().load_image(
                frame_name, str(frame_path), size=(20, 20)
            )

            if frame is not None:
                frames.append(frame)

        self.animator.add_animation(self._name, frames, 1 / len(frames))

    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

        self.transform.pos += self.direction * self.speed * dt
        super().update(dt)
        self.animator.update(dt)

    def on_collision(self, other: GameObject):
        if other is None:
            return

        if isinstance(other, Enemy) and self.friendly:
            other.take_damage(self.damage, True)
            self.kill()
