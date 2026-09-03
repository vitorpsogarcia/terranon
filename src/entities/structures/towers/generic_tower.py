import pygame

from core.components.static_render_component import StaticRenderComponent
from core.game_object import GameObject
from core.manager.asset_manager import AssetManager
from entities.obstacle import Obstacle
from utils.position import calculate_distance

TURRET_SIZE = 64


class GenericTower(Obstacle):
    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        range=100,
        damage=10,
        fire_rate=1.0,
        turret_size=TURRET_SIZE,
    ):
        half_size = turret_size / 2
        position = pygame.Vector2(
            round(position.x - half_size), round(position.y - half_size)
        )
        super().__init__(position, *groups, width=turret_size, height=turret_size)

        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate

        self.image = AssetManager().load_image(
            name=f"generic_tower_{turret_size}",
            path="Tower_gun.png",
            size=(turret_size, turret_size),
        )
        self.render_component = StaticRenderComponent(self, self.image)
        self.hitbox = pygame.Rect(
            round(self.pos.x), round(self.pos.y), turret_size, turret_size
        )
        self.rect = self.hitbox
        self.relative_hitboxes = [pygame.Rect(0, 0, turret_size, turret_size)]
        self._fixed_opacity = True
        self.target: GameObject | None = None
        self.cooldown = 0.0

    def update(self, dt: float):
        super().update(dt)

        if self.target and (
            not self.target.active
            or calculate_distance(self.target.pos, self.pos) > self.range
        ):
            self.target = None
