import pygame

from core.enums.map_enums import MapsEnum, WaypointsEnum
from core.game_world import GameWorld
from core.map.map_manager import MapManager
from core.map.map_backgroud import MapBackground
from core.wave_manager import WaveManager
from entities.character.player import Player
from entities.structures.main_base import MainBase


class LevelLoader:
    def __init__(self, screen_size: tuple[int, int]):
        self.screen_size = screen_size

    def load_level(self, map_enum: MapsEnum) -> tuple[GameWorld, Player, WaveManager]:
        world = GameWorld(self.screen_size)

        MapManager().change_map(map_enum, world)
        current_map = MapManager().get_map(map_enum)

        if current_map and current_map._ground_image:
            bg = MapBackground(pygame.math.Vector2(0, 0), current_map._ground_image)
            world.add_object(bg)

        player_x, player_y = 0, 0
        if current_map:
            if WaypointsEnum.PLAYER_SPAWNPOINT in current_map._waypoints:
                spawnpoint = current_map._waypoints[WaypointsEnum.PLAYER_SPAWNPOINT]
                player_x, player_y = spawnpoint.position.x, spawnpoint.position.y
            if WaypointsEnum.BASE in current_map._waypoints:
                basepoint = current_map._waypoints[WaypointsEnum.BASE]
                base_x, base_y = basepoint.position.x, basepoint.position.y

                base = MainBase(pygame.Vector2(base_x, base_y))
                world.add_object(base)

        player = Player(pygame.Vector2(player_x, player_y))
        player.pos = pygame.math.Vector2(player_x, player_y)
        if player.rect is not None:
            player.rect.topleft = player.pos

        world.add_object(player)
        world.set_target(player)

        wave_manager = WaveManager(world.spatial_manager.spawners)

        return world, player, wave_manager
