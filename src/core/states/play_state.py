import logging
from typing import TYPE_CHECKING

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.enums.map_enums import MapsEnum
from core.game_world import GameWorld
from core.manager.economy_manager import EconomyManager
from core.manager.event_manager import EventManager
from core.manager.game_manager import GameManager
from core.manager.highscore_manager import HighscoreManager
from core.manager.sound_manager import SoundManager
from core.states.base_state import BaseState
from entities.structures.towers.generic_tower import GenericTower

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager
    from entities.character.player import Player


class PlayState(BaseState):
    _logger = logging.getLogger("PlayState")
    _show_debug = False

    def __init__(
        self,
        state_manager: "StateManager",
        game_manager: "GameManager",
        screen_size: tuple[int, int],
    ):
        super().__init__(state_manager, screen_size)
        self.world: GameWorld | None = None
        self.player: Player | None = None
        self.screen_size = screen_size
        self.game_manager = game_manager
        self.player_name: str = "Player"

    def enter(self):
        try:
            SoundManager().play_music("Crashsite-Defense.wav")
        except Exception as e:
            self._logger.error(f"{e}")

        EconomyManager().reset_points()
        self.player_name = HighscoreManager().current_player_name

        EventManager().subscribe(GameEventEnum.GAME_OVER, self._game_over)
        EventManager().subscribe(GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned)

        from core.map.level_loader import LevelLoader

        level_loader = LevelLoader(self.screen_size)
        self.world, self.player, self.wave_manager = level_loader.load_level(
            MapsEnum.MAIN_WORLD
        )

        self._load_debug_objects()

    def exit(self):
        SoundManager().stop_music()
        if hasattr(self, "wave_manager"):
            self.wave_manager.destroy()
        if self.world:
            self.world.destroy()
            self.world = None
        self.player = None
        EventManager().unsubscribe(GameEventEnum.GAME_OVER, self._game_over)
        EventManager().unsubscribe(GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned)

    def update(self, delta_time):
        if self.world is not None and self.player is not None:
            mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
            self.player.aim_target = self.world.camera_group.screen_to_world(mouse_pos)

        if self.world is not None:
            self.world.update(delta_time)

        if hasattr(self, "wave_manager"):
            self.wave_manager.update(delta_time)

    def _change_state(self, new_state: GameStateEnum):
        self.state_manager.change_to(new_state)

    def _game_over(self):
        final_score = EconomyManager().total_points
        HighscoreManager().add_score(self.player_name, final_score)
        self.initialized = False
        self._change_state(GameStateEnum.GAME_OVER)

    def handle_events(self, events: list[pygame.event.Event]):

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.state_manager.push(GameStateEnum.INVENTORY)
                elif event.key == pygame.K_k:
                    self.state_manager.change_to(GameStateEnum.GAME_OVER)
                elif event.key == pygame.K_ESCAPE:
                    self.state_manager.push(GameStateEnum.PAUSE)

            if event.type == pygame.MOUSEWHEEL and self.world is not None:
                self.world.camera_group.handle_zoom(event.y)

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
