import pygame

from core.component import Component
from core.map.waypoints.polyline import Polyline
from core.map.waypoints.waypoint import Waypoint


class PathFollowerComponent(Component):
    def __init__(self, owner, path: Polyline, stop_distance: float = 5.0):
        self.owner = owner
        self.path = path
        self.stop_distance = stop_distance
        self.current_waypoint: Waypoint = self.path.get_start_waypoint()

    def update(self, dt: float):
        """
        Updates the path follower logic and modifies owner direction and state directly.
        """
        next_waypoint = self.path.get_next_waypoint(self.current_waypoint)

        if next_waypoint is not None and hasattr(self.owner, "transform"):
            target_pos = next_waypoint.position
            self_pos = pygame.math.Vector2(
                self.owner.transform.pos.x, self.owner.transform.pos.y
            )

            direction_vector = target_pos - self_pos
            distance = direction_vector.length()

            if distance > self.stop_distance:
                self.owner.direction = direction_vector.normalize()
                self.owner.current_state = "walking"
            else:
                self.current_waypoint = next_waypoint
                self.owner.direction = pygame.math.Vector2(0, 0)
                self.owner.current_state = "walking"

        else:
            self.owner.direction = pygame.math.Vector2(0, 0)
            self.owner.current_state = "idle"
