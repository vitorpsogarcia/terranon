import pygame

from core.components.animator_component import AnimatorComponent
from core.components.health_component import HealthComponent
from core.components.movement_component import MovementComponent
from core.components.path_follower_component import PathFollowerComponent
from core.entity import Entity
from core.enums.game_event_enum import GameEventEnum
from core.manager.event_manager import EventManager
from core.map.waypoints.polyline import Polyline
from core.map.waypoints.waypoint import Waypoint
from utils.direction import get_direction_str_by_vector


class Enemy(Entity):
    current_waypoint: Waypoint
    _points: int

    def __init__(
        self,
        position: pygame.Vector2,
        path: Polyline,
        *groups: pygame.sprite.Group,
        speed: float = 50.0,
        points: int = 5,
        max_hp: float = 100.0,
    ):
        super().__init__(position, *groups)

        self.health = self.add_component(
            HealthComponent(
                max_hp=max_hp,
                on_death_callback=self.on_death,
                iframes_duration=0.5,
                allow_invulnerability=False,
            )
        )

        self.movement = self.add_component(MovementComponent(self, speed=speed))
        self.path_follower = self.add_component(PathFollowerComponent(self, path))
        self.animator = self.add_component(AnimatorComponent(self))
        self.render_component = self.animator
        self.direction = pygame.math.Vector2(0, 0)

        self.scale = 0.3
        self.hitbox = pygame.Rect(self.pos.x, self.pos.y, 30, 60)
        self.rect = self.hitbox
        self._points = points
        self.current_state = "idle"
        self.last_direction = "south"

    def update(self, dt: float):
        super().update(dt)

        if self.current_state == "idle":
            self.health.die()

        dir_str = get_direction_str_by_vector(self.direction)
        if dir_str is not None:
            self.last_direction = dir_str

        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        if self.rect is not None:
            self.rect.center = self.hitbox.center

    def on_death(self, by_player: bool = False):
        self.active = False
        self.kill()

        if by_player:
            EventManager().emit(GameEventEnum.ENEMY_KILLED, self._points)

    def take_damage(self, amount: float, by_player: bool = False):
        self.health.take_damage(amount)
        if self.health.is_dead:
            self.on_death(by_player=by_player)
