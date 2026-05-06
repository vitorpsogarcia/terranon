from pygame import Vector2

from core.enums.projectile.projectile_types_enum import ProjectileTypesEnum
from core.enums.projectile.projectile_variant_enum import ProjectileVariantEnum
from core.factories.factory import Factory
from entities.projectiles.projectile import Projectile

class ProjectileFactory(Factory):

    def create_projectile(self, position: Vector2, direction: Vector2, type: ProjectileTypesEnum, variant: ProjectileVariantEnum, speed=400.0, damage=10, lifetime=1.5, friendly=False):

        projectile = Projectile(position, direction, speed, damage, lifetime, type, variant, friendly)
        self.world.add_object(projectile)
        return projectile