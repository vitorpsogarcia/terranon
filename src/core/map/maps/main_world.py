import logging

import pygame

from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.enums.map_enums import WaypointsEnum
from core.enums.map_enums.map_layers_enum import MapLayersEnum
from core.map.map import Map
from core.map.waypoints.polyline import Polyline
from core.map.waypoints.waypoint import Waypoint
from core.settings.settings import ASSETS_FOLDER
from entities.enemy_spawner import EnemySpawner
from entities.nature.tree import Tree

main_world_path = (ASSETS_FOLDER / "maps" / "tmx" / "main_world.tmx").as_posix()


class MainWorldMap(Map):
    _logger = logging.getLogger("MainWorldMap")

    def __init__(self):
        super().__init__(main_world_path)

        self._logger.info(f"Processing map: {main_world_path}")
        self._process_map()
        self._logger.info("Map processed successfully.")

    def _process_map(self):
        ground_layer = self.tiled_map.get_layer_by_name(MapLayersEnum.GROUND.value)
        waypoints_layer = self.tiled_map.get_layer_by_name(
            MapLayersEnum.WAYPOINTS.value
        )
        spawners_layer = self.tiled_map.get_layer_by_name(MapLayersEnum.SPAWNERS.value)
        enemy_routes_layer = self.tiled_map.get_layer_by_name(
            MapLayersEnum.ENEMY_ROUTES.value
        )

        if ground_layer:
            self._process_ground_layer(ground_layer)
        if waypoints_layer:
            self._process_waypoints_layer(waypoints_layer)
        if enemy_routes_layer:
            self._process_enemy_paths_layer(enemy_routes_layer)
        if spawners_layer:
            self._process_spawners_layer(spawners_layer)

        self._process_objects_layer()

    def _process_ground_layer(self, layer):
        self._logger.info("Processing ground layer...")
        surface = pygame.Surface((
            self.tiled_map.width * self.tiled_map.tilewidth,
            self.tiled_map.height * self.tiled_map.tileheight,
        )).convert()
        for x, y, image in layer.tiles():
            surface.blit(
                image, (x * self.tiled_map.tilewidth, y * self.tiled_map.tileheight)
            )
        self._ground_image = surface
        self._logger.info("Ground layer processed successfully.")

    def _process_waypoints_layer(self, layer):
        self._logger.info("Processing waypoints layer...")
        waypoints = {}
        for item in layer:
            waypoint_name = item.name
            if waypoint_name:
                waypoints[WaypointsEnum(waypoint_name)] = Waypoint(
                    waypoint_name, pygame.math.Vector2(item.x, item.y)
                )
        self._waypoints = waypoints
        self._logger.info("Waypoints layer processed successfully.")

    def _process_enemy_paths_layer(self, layer):
        self._logger.info("Processing enemy paths layer...")

        routes_by_id = {}

        for item in layer:
            route_id = item.id
            points = []

            path_points = [*item.points]
            path_points.reverse()
            for point in path_points:
                points.append(
                    Waypoint(item.id, pygame.math.Vector2(point[0], point[1]))
                )

            to_waypoint = None
            if item.properties.get("is_last"):
                to_waypoint = self._waypoints.get(WaypointsEnum.BASE)

            polyline = Polyline(route_id, points, to_waypoint=to_waypoint)
            routes_by_id[route_id] = polyline

        self._enemy_paths = routes_by_id
        self._logger.info("Enemy paths layer processed successfully.")

    def _process_spawners_layer(self, layer):
        self._logger.info("Processing spawners layer...")

        spawners = {}

        for item in layer:
            spawner_name = item.name
            if spawner_name:
                if spawner_name not in EnemySpawnerEnum.to_list():
                    self._logger.warning(
                        f"Spawner name '{spawner_name}' in map does not match any defined EnemySpawnerEnum. Skipping."
                    )
                    continue

                start_path = item.properties.get("start_path")
                if start_path is None:
                    self._logger.error(
                        f"Spawner '{spawner_name}' is missing a start_path. Skipping."
                    )
                    continue

                path = self.get_enemy_path_by_id(start_path)
                if path is None:
                    self._logger.error(
                        f"Spawner '{spawner_name}' references non-existent enemy path ID {start_path}. Skipping."
                    )
                    continue

                enemy_spawner = EnemySpawner(
                    spawner_name, item.x, item.y, path
                )
                spawners[EnemySpawnerEnum(spawner_name)] = enemy_spawner

                self._logger.info(f"Spawner '{spawner_name}' processed successfully.")
        self._enemy_spawners = spawners
        self._logger.info("Spawners layer processed successfully.")

    def _process_objects_layer(self):
        trees_layer = self.tiled_map.get_layer_by_name(MapLayersEnum.TREES.value)
        collision_layer = self.tiled_map.get_layer_by_name(
            MapLayersEnum.COLLISION.value
        )

        if trees_layer:
            self._process_trees_layer(trees_layer)

        if collision_layer:
            self._process_collision_layer(collision_layer)

    def _process_trees_layer(self, layer):
        self._logger.info("Planting trees...")
        trees = []

        sorted_by_y = sorted(layer, key=lambda item: item.y)

        for item in sorted_by_y:
            tree_type = item.properties.get("type")
            colliders = item.properties.get("colliders", False)

            relative_hitboxes = []
            if colliders:
                for col in colliders:
                    # Cria o hitbox com coordenadas relativas à origem da árvore (definido no Tiled)
                    relative_hitbox = pygame.Rect(col.x, col.y, col.width, col.height)
                    relative_hitboxes.append(relative_hitbox)

                    # O sistema de colisor do mapa ainda precisa das coordenadas absolutas
                    absolute_hitbox = relative_hitbox.move(item.x, item.y)
                    self.add_collider(absolute_hitbox)

            if tree_type is None:
                continue

            # Passa a lista de hitboxes RELATIVOS para a árvore
            tree = Tree(
                pygame.math.Vector2(item.x, item.y), tree_type, relative_hitboxes
            )
            trees.append(tree)
        self._trees = trees

        self.add_list_render_object(trees)
        self._logger.info("Trees planted successfully.")

    def _process_collision_layer(self, layer):
        self._logger.info("Processing collision layer...")
        colliders = []
        for item in layer:
            collider = pygame.Rect(item.x, item.y, item.width, item.height)
            colliders.append(collider)
            self.add_collider(collider)
        self._logger.info("Collision layer processed successfully.")
