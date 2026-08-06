import pygame

from core.enums.game_event_enum import GameEventEnum
from core.manager.event_manager import EventManager
from core.map.waypoints.polyline import Polyline
from core.map.waypoints.waypoint import Waypoint
from entities.character.characters import Character
from utils.direction import get_direction_str_by_vector


class Enemy(Character):
    current_waypoint: Waypoint
    _points: int

    def __init__(
        self,
        position: pygame.Vector2,
        path: Polyline,
        *groups: pygame.sprite.Group,
        speed: float = 50.0,
        points: int = 5,
        max_hp: int = 100,
    ):
        super().__init__(position, speed, *groups, max_hp=max_hp)
        self.scale = 0.3

        self.path = path
        self.current_waypoint = self.path.get_start_waypoint()
        self.hitbox = pygame.Rect(self.pos.x, self.pos.y, 30, 60)

        if self.image is None:
            self.image = pygame.Surface((20, 48)).convert_alpha()
            self.image.fill((111, 0, 0))
            self.rect = self.image.get_rect(
                topleft=(round(self.pos.x), round(self.pos.y))
            )

        self._points = points

    def update(self, dt: float):
        next_waypoint = self.path.get_next_waypoint(self.current_waypoint)

        if next_waypoint is not None and self.rect is not None:
            target_pos = next_waypoint.position
            self_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)

            direction_vector = target_pos - self_pos
            distance = direction_vector.length()

            if distance > 5.0:
                self.direction = direction_vector.normalize()
                estado_animacao = "walking"
            else:
                self.current_waypoint = next_waypoint
                self.direction = pygame.math.Vector2(0, 0)
                estado_animacao = "walking"

        else:
            self.direction = pygame.math.Vector2(0, 0)
            estado_animacao = "idle"

            self.health.die()

        self.current_state = estado_animacao
        dir_str = get_direction_str_by_vector(self.direction)
        if dir_str is not None:
            self.last_direction = dir_str

        super().update(dt)
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))

    def on_death(self):
        super().on_death()
        EventManager().emit(GameEventEnum.ENEMY_KILLED, self._points)
