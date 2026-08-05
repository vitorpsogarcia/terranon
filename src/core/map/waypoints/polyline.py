
from core.map.waypoints.waypoint import Waypoint


class Polyline:
    def __init__(self, id: int, waypoints: list[Waypoint], to_waypoint: Waypoint | None = None):
        self._id = id
        self._waypoints = waypoints
        self._to_waypoint = to_waypoint

    
    @property
    def get_id(self) -> int:
        return self._id

    
    @property
    def waypoints(self) -> list[Waypoint]:
        return self._waypoints
    
    
    @property
    def length(self) -> int:
        return len(self._waypoints)
    
    
    def get_next_waypoint(self, current_waypoint: Waypoint) -> Waypoint | None:
        try:
            index = self._waypoints.index(current_waypoint)
            is_last_waypoint = index == len(self._waypoints) - 1
            if is_last_waypoint and self._to_waypoint:
                return self._to_waypoint
            elif index < len(self._waypoints) - 1:
                return self._waypoints[index + 1]
        except ValueError:
            pass
        return None
    
    
    def get_start_waypoint(self) -> Waypoint:
        return self._waypoints[0]
    
    
    def get_end_waypoint(self) -> Waypoint:
        return self._waypoints[-1]
