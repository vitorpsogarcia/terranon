from typing import TYPE_CHECKING

import pygame

from core.components.static_render_component import StaticRenderComponent
from core.enums.collider_tag_enum import ColliderTagEnum
from core.enums.game_event_enum import GameEventEnum
from core.enums.projectile.projectile_types_enum import ProjectileTypesEnum
from core.enums.projectile.projectile_variant_enum import ProjectileVariantEnum
from core.manager.asset_manager import AssetManager
from core.manager.event_manager import EventManager
from core.manager.spatial_manager import SpatialManager
from entities.obstacle import Obstacle
from utils.math_helpers import calculate_intercept_position
from utils.position import calculate_distance

if TYPE_CHECKING:
    from entities.enemy import Enemy

TURRET_SIZE = 64
TURRET_ID_PREFIX = "S_GT_"


class GenericTower(Obstacle):
    id_ct = 0

    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        range=100,
        damage=10,
        fire_rate=10.0,
        turret_size=TURRET_SIZE,
    ):
        half_size = turret_size / 2
        position = pygame.Vector2(
            round(position.x - half_size), round(position.y - half_size)
        )
        super().__init__(
            position,
            *groups,
            width=turret_size,
            height=turret_size,
            default_hitbox=False,
        )

        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate

        self.id = f"{TURRET_ID_PREFIX}{GenericTower.id_ct}"
        GenericTower.id_ct += 1

        self.image = AssetManager().load_image(
            name=f"generic_tower_{turret_size}",
            path="Tower_gun.png",
            size=(turret_size, turret_size),
        )
        self.render_component = StaticRenderComponent(self, self.image)
        self.render_component.render_layer = 2
        self._fixed_opacity = True

        self.target: Enemy | None = None
        self.cooldown = 0.0
        self._center = self.render_component.center()

        self.collider.add_box(
            0, 0, turret_size, turret_size, tag=ColliderTagEnum.TRIGGER
        )
        self.collider.add_box(
            turret_size // 4,
            turret_size // 2,
            turret_size // 2,
            turret_size // 2,
            tag=ColliderTagEnum.SOLID,
        )

    def update(self, dt: float):
        super().update(dt)

        if self.target is None:
            enemy = SpatialManager().get_nearest_enemy(self._center, self.range)

            if enemy is not None:
                self.target = enemy
                enemy.set_turret_target(self)
        else:
            if (
                not self.target.active
                or calculate_distance(self.target.transform.pos, self._center)
                > self.range
            ):
                self.target.clear_turret_target()
                self.target = None
            else:
                self.cooldown -= dt
                if self.cooldown <= 0:
                    self.fire()
                    self.cooldown = 1.0 / self.fire_rate

    def fire(self):
        if not self.target or not self.target.active:
            return
        bullet_speed = 300.0  # Em px/s

        # Obtém a velocidade atual do inimigo (direção * velocidade)
        enemy_vel = pygame.Vector2(0, 0)
        if hasattr(self.target, "movement") and hasattr(self.target, "direction"):
            enemy_vel = self.target.direction * self.target.movement.speed
        elif hasattr(self.target, "rigidbody"):
            enemy_vel = self.target.rigidbody.velocity
        aim_pos = calculate_intercept_position(
            shooter_pos=self._center,
            bullet_speed=bullet_speed,
            target_pos=self.target.transform.pos,
            target_velocity=enemy_vel,
        )
        direction = aim_pos - self._center
        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2(0, 1)

        EventManager().emit(
            GameEventEnum.SPAWN_PROJECTILE,
            position=self._center,
            direction=direction,
            type=ProjectileTypesEnum.NORMAL,
            variant=ProjectileVariantEnum.DEFAULT,
            speed=bullet_speed,
            damage=self.damage,
            lifetime=1.5,
            friendly=True,
        )
