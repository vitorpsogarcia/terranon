import logging
from typing import TYPE_CHECKING

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.event_manager import EventManager
from core.factories.factories_loader import FactoriesLoader
from core.game_world import GameWorld
from core.map.map_backgroud import MapBackground
from core.sound_manager import SoundManager
from core.states.base_state import BaseState
from entities.base_structure import BaseStructure

if TYPE_CHECKING:
    from core.state_manager import StateManager
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

        EventManager.get_instance().subscribe(GameEventEnum.GAME_OVER, self._game_over)
        EventManager.get_instance().subscribe(
            GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned
        )

        self.world = GameWorld(self.screen_size)

        FactoriesLoader(self.world)

        MapManager.change_map(MapsEnum.MAIN_WORLD, self.world)
        current_map = MapManager.get_map(MapsEnum.MAIN_WORLD)

        if current_map and current_map._ground_image:
            bg = MapBackground(pygame.math.Vector2(0, 0), current_map._ground_image)
            self.world.add_object(bg)

        player_x, player_y = 415, 478
        if current_map and WaypointsEnum.PLAYER_SPAWNPOINT in current_map._waypoints:
            spawnpoint = current_map._waypoints[WaypointsEnum.PLAYER_SPAWNPOINT]
            player_x, player_y = spawnpoint.position.x, spawnpoint.position.y

        player = Player(pygame.Vector2(player_x, player_y))

        player.pos = pygame.math.Vector2(player_x, player_y)
        if player.rect is not None:
            player.rect.topleft = player.pos

        for objects_list in current_map.render_objects:
            for obj in objects_list:
                self.world.add_object(obj)

        self.world.add_object(player)
        self.world.set_target(player)

        self.base = BaseStructure(500, 300)
        self.world.add_object(self.base)

        self.initialized = True

    def exit(self):
        self.initialized = False
        SoundManager().stop_music()
        EventManager.get_instance().unsubscribe(
            GameEventEnum.GAME_OVER, self._game_over
        )
        EventManager.get_instance().unsubscribe(
            GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned
        )

    def update(self, delta_time):
        if self.world is not None:
            self.world.update(delta_time)

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
