import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.projectile.projectile_types_enum import ProjectileTypesEnum
from core.enums.projectile.projectile_variant_enum import ProjectileVariantEnum
from core.game_object import GameObject
from core.manager.event_manager import EventManager
from core.manager.spatial_manager import SpatialManager
from core.settings.colors import Colors
from entities.obstacle import Obstacle
from utils.position import calculate_distance

TURRET_SIZE = 50


class GenericTower(Obstacle):
    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        range=200,
        damage=10,
        fire_rate=10.0,
        turret_size=TURRET_SIZE,
    ):
        super().__init__(position, *groups, width=turret_size, height=turret_size)
        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate
        self.target: GameObject | None = None
        self.cooldown = 0.0

        self._fixed_opacity = True

        self.render_component.image.fill(Colors.debug.turret)
        self._center = self.render_component.center()

        # Hitbox legado removido

    def update(self, dt: float):
        super().update(dt)

        if self.target is None:
            enemy = SpatialManager().get_nearest_enemy(self._center, self.range)

            if enemy is not None:
                self.target = enemy
        else:
            if (
                not self.target.active
                or calculate_distance(self.target.transform.pos, self._center)
                > self.range
            ):
                self.target = None
            else:
                self.cooldown -= dt
                if self.cooldown <= 0:
                    self.fire()
                    self.cooldown = 1.0 / self.fire_rate

    def fire(self):
        if self.target:
            direction = self.target.transform.pos - self._center
            EventManager().emit(
                GameEventEnum.SPAWN_PROJECTILE,
                self._center,
                direction,
                ProjectileTypesEnum.NORMAL,
                ProjectileVariantEnum.DEFAULT,
                speed=3.0,
                damage=self.damage,
                lifetime=1.5,
                friendly=True,
            )
