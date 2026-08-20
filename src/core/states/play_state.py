import logging
from typing import TYPE_CHECKING

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.factories.factories_loader import FactoriesLoader
from core.game_world import GameWorld
from core.manager.economy_manager import EconomyManager
from core.manager.event_manager import EventManager
from core.manager.sound_manager import SoundManager
from core.map.map_backgroud import MapBackground
from core.states.base_state import BaseState
from core.wave_manager import WaveManager
from entities.structures.main_base import MainBase
from entities.structures.towers.generic_tower import GenericTower

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager
from core.enums.map_enums import MapsEnum, WaypointsEnum
from core.map.map_manager import MapManager
from entities.character.player import Player


class PlayState(BaseState):
    _logger = logging.getLogger("PlayState")
    _show_debug = False

    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.world: GameWorld | None = None
        self.initialized = False
        self.screen_size = screen_size

    def enter(self):
        if self.initialized:
            return
        try:
            SoundManager().play_music("Crashsite-Defense.wav")
        except Exception as e:
            self._logger.error(f"{e}")

        EconomyManager()

        EventManager().subscribe(GameEventEnum.GAME_OVER, self._game_over)
        EventManager().subscribe(GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned)

        self.world = GameWorld(self.screen_size)

        FactoriesLoader(self.world)

        MapManager().change_map(MapsEnum.MAIN_WORLD, self.world)
        current_map = MapManager().get_map(MapsEnum.MAIN_WORLD)

        if current_map and current_map._ground_image:
            bg = MapBackground(pygame.math.Vector2(0, 0), current_map._ground_image)
            self.world.add_object(bg)

        player_x, player_y = 0, 0
        if current_map:
            if WaypointsEnum.PLAYER_SPAWNPOINT in current_map._waypoints:
                spawnpoint = current_map._waypoints[WaypointsEnum.PLAYER_SPAWNPOINT]
                player_x, player_y = spawnpoint.position.x, spawnpoint.position.y
            if WaypointsEnum.BASE in current_map._waypoints:
                basepoint = current_map._waypoints[WaypointsEnum.BASE]
                base_x, base_y = basepoint.position.x, basepoint.position.y

                base = MainBase(pygame.Vector2(base_x, base_y))
                self.world.add_object(base)

        player = Player(pygame.Vector2(player_x, player_y))

        player.pos = pygame.math.Vector2(player_x, player_y)
        if player.rect is not None:
            player.rect.topleft = player.pos

        for objects_list in current_map.render_objects:
            for obj in objects_list:
                self.world.add_object(obj)

        self.world.add_object(player)
        self.world.set_target(player)

        self.wave_manager = WaveManager(self.world.spawners)

        self._load_debug_objects()

        self.initialized = True

    def exit(self):
        self.initialized = False
        SoundManager().stop_music()
        EventManager().unsubscribe(GameEventEnum.GAME_OVER, self._game_over)
        EventManager().unsubscribe(GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned)

    def update(self, delta_time):
        if self.world is not None:
            self.world.update(delta_time)

        if hasattr(self, "wave_manager"):
            self.wave_manager.update(delta_time)

    def _change_state(self, new_state: GameStateEnum):
        self.state_manager.change_to(new_state)

    def _game_over(self):
        self.initialized = False
        self._change_state(GameStateEnum.GAME_OVER)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.state_manager.change_to(GameStateEnum.INVENTORY)
                elif event.key == pygame.K_k:
                    self.state_manager.change_to(GameStateEnum.GAME_OVER)
                elif event.key == pygame.K_ESCAPE:
                    self.state_manager.change_to(GameStateEnum.MENU)

        if self.world is not None:
            self.world.handle_events(events)

    def draw(self, surface):
        if self.world is not None:
            self.world.draw(surface)

    def _on_enemy_spawned(self, enemy):
        """Callback acionado quando um ninho cria um inimigo."""
        if self.world:
            self.world.add_object(enemy)

    def _load_debug_objects(self):
        if self.world is None:
            return

        generic_turret = GenericTower(pygame.Vector2(8563, 5950))

        self.world.add_object(generic_turret)
