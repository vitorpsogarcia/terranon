import pygame

from core.game_object import GameObject
from core.settings.colors import Colors
from entities.obstacle import Obstacle
from utils.position import calculate_distance

TURRET_SIZE = 50
HALF_SIZE = TURRET_SIZE / 2


class GenericTower(Obstacle):
    def __init__(
        self,
        position: pygame.Vector2,
        *groups: pygame.sprite.Group,
        range=100,
        damage=10,
        fire_rate=1.0,
    ):
        position = pygame.Vector2(
            round(position.x - HALF_SIZE), round(position.y - HALF_SIZE)
        )
        super().__init__(position, *groups)

        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate

        self.image = pygame.Surface((TURRET_SIZE, TURRET_SIZE)).convert_alpha()
        self.image.fill(Colors.debug.turret)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self._fixed_opacity = True
        self.target: GameObject | None = None
        self.cooldown = 0.0

        self.relative_hitboxes = [pygame.Rect(0, 0, TURRET_SIZE, TURRET_SIZE)]

    def update(self, dt: float):
        super().update(dt)

        if self.target and (
            not self.target.active
            or calculate_distance(self.target.pos, self.pos) > self.range
        ):
            self.target = None
