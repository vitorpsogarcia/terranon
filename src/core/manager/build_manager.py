import logging

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.game_object import GameObject
from core.manager.event_manager import EventManager
from core.settings.colors import Colors
from core.settings.settings import GRID_SIZE
from core.singleton_meta import SingletonMeta


class Grid:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size

    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2 | None = None):
        if offset is None:
            offset = pygame.math.Vector2(0, 0)

        width, height = surface.get_size()

        start_x = int(offset.x // self.grid_size) * self.grid_size
        end_x = int(offset.x + width) + self.grid_size

        for x in range(start_x, end_x, self.grid_size):
            screen_x = round(x - offset.x)
            pygame.draw.line(
                surface, Colors.ui.building_grid, (screen_x, 0), (screen_x, height)
            )

        start_y = int(offset.y // self.grid_size) * self.grid_size
        end_y = int(offset.y + height) + self.grid_size

        for y in range(start_y, end_y, self.grid_size):
            screen_y = round(y - offset.y)
            pygame.draw.line(
                surface, Colors.ui.building_grid, (0, screen_y), (width, screen_y)
            )


class BuildManager(metaclass=SingletonMeta):
    _logger = logging.getLogger("BuildManager")

    is_building = False
    grid_size = GRID_SIZE

    def __init__(self):
        self.building_mode = False
        self.current_building: GameObject | None = None
        self.grid = Grid(self.grid_size)

        EventManager().subscribe(
            GameEventEnum.BUILD_TOGGLED, self._toggle_building_mode
        )

    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2 | None = None):
        if self.is_building:
            self.grid.draw(surface, offset)

    def _toggle_building_mode(self):
        self.is_building = not self.is_building
        if self.is_building:
            self._logger.info("Entered building mode.")
            EventManager().emit(GameEventEnum.BUILD_MODE_ENTERED)
        else:
            self._logger.info("Exited building mode.")
            EventManager().emit(GameEventEnum.BUILD_MODE_EXITED)
