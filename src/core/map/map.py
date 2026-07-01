from abc import ABC, abstractmethod
import logging
from typing import Dict

from pytmx.util_pygame import load_pygame

from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.enums.map_enums.waypoints_enum import WaypointsEnum
from core.game_world import GameWorld
from core.map.waypoints.polyline import Polyline
from core.map.waypoints.waypoint import Waypoint
from entities.enemy_spawner import EnemySpawner


class Map(ABC):
    _logger = logging.getLogger("Map")

    _ground_image = None
    _waypoints: Dict[WaypointsEnum, Waypoint] = {}
    _enemy_spawners: Dict[EnemySpawnerEnum, EnemySpawner] = {}
    _enemy_paths: Dict[int, Polyline] = {}

    def __init__(self, map_path: str):
        self.tiled_map = load_pygame(map_path)


    @abstractmethod
    def _process_map(self):
        ...
    

    def instantiate(self, world: GameWorld):
        for spawner in self._enemy_spawners.values():
            world.add_object(spawner)
    
    
    def get_enemy_path_by_id(self, route_id: int) -> Polyline | None:
        try:
            return self._enemy_paths[route_id]
        except KeyError:
            self._logger.error(f"Enemy path not found for route ID: {route_id}")
            return None
