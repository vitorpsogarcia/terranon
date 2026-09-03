from logging import getLogger

from pygame import Vector2

from core.enums.game_event_enum import GameEventEnum
from core.enums.projectile.projectile_types_enum import ProjectileTypesEnum
from core.enums.projectile.projectile_variant_enum import ProjectileVariantEnum
from core.factories.factory import Factory
from core.manager.event_manager import EventManager
from entities.projectiles.projectile import Projectile


class ProjectileFactory(Factory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        EventManager().subscribe(GameEventEnum.SPAWN_PROJECTILE, self.create_projectile)

    def destroy(self):
        EventManager().unsubscribe(
            GameEventEnum.SPAWN_PROJECTILE, self.create_projectile
        )

    def create_projectile(
        self,
        position: Vector2,
        direction: Vector2,
        type: ProjectileTypesEnum,
        variant: ProjectileVariantEnum,
        speed=400.0,
        damage=10,
        lifetime=1.5,
        friendly=False,
    ):
        projectile = Projectile(
            position, direction, speed, damage, lifetime, type, variant, friendly
        )
        self.world.add_object(projectile)
        return projectile
