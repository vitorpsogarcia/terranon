import logging
from abc import ABC, abstractmethod

import pygame
from pytmx.util_pygame import load_pygame

from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.enums.map_enums.waypoints_enum import WaypointsEnum
from core.game_object import GameObject
from core.game_world import GameWorld
from core.map.waypoints.polyline import Polyline
from core.map.waypoints.waypoint import Waypoint
from entities.enemy_spawner import EnemySpawner


class Map(ABC):
    _logger = logging.getLogger("Map")

    _ground_image = None
    _waypoints: dict[WaypointsEnum, Waypoint] = {}
    _enemy_spawners: dict[EnemySpawnerEnum, EnemySpawner] = {}
    _enemy_paths: dict[int, Polyline] = {}
    _world_colliders: list[pygame.Rect] = []
    _render_objects: list[list[GameObject]] = []

    def __init__(self, map_path: str):
        self.tiled_map = load_pygame(map_path)


    @abstractmethod
    def _process_map(self):
        ...


    @property
    def world_colliders(self) -> list[pygame.Rect]:
        return self._world_colliders


    @property
    def render_objects(self) -> list[list[GameObject]]:
        return self._render_objects


    def add_list_render_object(self, list_objects: list[GameObject]):
        self._render_objects.append(list_objects)

    def remove_list_render_object(self, list_objects: list[GameObject]):
        if list_objects in self._render_objects:
            self._render_objects.remove(list_objects)


    def instantiate(self, world: GameWorld):
        for spawner in self._enemy_spawners.values():
            world.add_object(spawner)

        for list_objects in self.render_objects:
            for obj in list_objects:
                world.add_object(obj)

        world.world_colliders.extend(self.world_colliders)
    
    
    def get_enemy_path_by_id(self, route_id: int) -> Polyline | None:
        try:
            return self._enemy_paths[route_id]
        except KeyError:
            self._logger.error(f"Enemy path not found for route ID: {route_id}")
            return None


    def add_collider(self, collider: pygame.Rect):
        self._world_colliders.append(collider)


