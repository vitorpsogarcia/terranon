import logging
from typing import TYPE_CHECKING

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.manager.economy_manager import EconomyManager
from core.manager.event_manager import EventManager
from core.manager.spatial_manager import SpatialManager
from core.settings.colors import Colors
from core.settings.settings import GRID_SIZE
from core.singleton_meta import SingletonMeta
from entities.structures.structure import Structure

if TYPE_CHECKING:
    from core.game_world import GameWorld


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
    grid_size = GRID_SIZE

    def __init__(self):
        self.is_building = False
        self.current_ghost: Structure | None = None
        self.current_structure_class: type[Structure] | None = None
        self.world_reference: GameWorld | None = None
        self.grid = Grid(self.grid_size)

        EventManager().subscribe(GameEventEnum.BUILD_TOGGLED, self._toggle_build_menu)

    def _toggle_build_menu(self):
        EventManager().emit(GameEventEnum.PLAY_SFX, filename="ui/click.wav")

    def set_ghost(self, structure_class: type[Structure], world: "GameWorld"):
        if self.is_building:
            self.cancel_build()

        self.current_structure_class = structure_class
        self.world_reference = world
        self.is_building = True

        # Instantiate ghost at 0,0 initially
        self.current_ghost = structure_class(pygame.Vector2(0, 0), is_ghost=True)
        assert self.current_ghost is not None, "Failed to create ghost structure."
        self.world_reference.add_object(self.current_ghost)

        self._logger.info("Entered building mode with ghost.")
        EventManager().emit(GameEventEnum.BUILD_MODE_ENTERED)

    def update(self, mouse_world_pos: pygame.Vector2):
        if not self.is_building or not self.current_ghost:
            return

        # Snap to grid
        snapped_x = int(mouse_world_pos.x // self.grid_size) * self.grid_size
        snapped_y = int(mouse_world_pos.y // self.grid_size) * self.grid_size

        self.current_ghost.transform.pos.x = snapped_x
        self.current_ghost.transform.pos.y = snapped_y

        # Validate placement
        can_place = SpatialManager().can_place_structure(self.current_ghost)
        can_afford = EconomyManager().current_points >= self.current_ghost.build_cost

        if can_place and can_afford:
            self.current_ghost.render_component.color_tint = (
                Colors.building.greenish
            )  # Greenish
        else:
            self.current_ghost.render_component.color_tint = (
                Colors.building.reddish
            )  # Reddish

    def attempt_build(self):
        if not self.is_building or not self.current_ghost or not self.world_reference:
            return

        can_place = SpatialManager().can_place_structure(self.current_ghost)
        can_afford = EconomyManager().current_points >= self.current_ghost.build_cost

        if can_place and can_afford:
            EconomyManager().spend_points(self.current_ghost.build_cost)

            assert self.current_structure_class is not None, (
                "Structure class is None during build."
            )
            # Create real structure
            real_structure = self.current_structure_class(
                self.current_ghost.transform.pos.copy()
            )
            self.world_reference.add_object(real_structure)

            try:
                EventManager().emit(
                    GameEventEnum.PLAY_SFX, filename="effects/build.wav"
                )
            except Exception as e:
                self._logger.error(f"Error playing build sfx: {e}")

            # Usually we keep building mode active to build more, or we cancel
            # Let's cancel for now, or keep ghost. If we keep, we just don't cancel.
            # But we must clear the current ghost and recreate to avoid sharing references? No, it's just a position update.
            # We'll cancel to require re-selecting, or user can keep placing. We'll cancel for simplicity.
            self.cancel_build()

    def cancel_build(self):
        if self.current_ghost and self.world_reference:
            self.world_reference.remove_object(self.current_ghost)
            self.current_ghost.kill()

        self.current_ghost = None
        self.current_structure_class = None
        self.is_building = False
        self._logger.info("Exited building mode.")
        EventManager().emit(GameEventEnum.BUILD_MODE_EXITED)

    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2 | None = None):
        if offset is None:
            offset = pygame.math.Vector2(0, 0)

        if self.is_building:
            self.grid.draw(surface, offset)
            self._draw_ranges(surface, offset)

    def _toggle_building_mode(self):
        self.is_building = not self.is_building
        if self.is_building:
            self._logger.info("Entered building mode.")
            EventManager().emit(GameEventEnum.BUILD_MODE_ENTERED)
        else:
            self._logger.info("Exited building mode.")
            EventManager().emit(GameEventEnum.BUILD_MODE_EXITED)

    def _draw_ranges(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        # Draw ranges for all existing towers
        for struct_sprite in SpatialManager().structures_group:
            struct = getattr(struct_sprite, "owner", None)
            if struct and hasattr(struct, "range"):
                center = struct.render_component.center()
                self._draw_circle_alpha(
                    surface,
                    color=(255, 255, 255, 50),
                    center=(int(center.x - offset.x), int(center.y - offset.y)),
                    radius=struct.range,
                )

        # Draw range for the ghost
        assert self.current_ghost is not None, "Ghost is None during range drawing."
        if self.current_ghost and hasattr(self.current_ghost, "range"):
            center = self.current_ghost.render_component.center()
            self._draw_circle_alpha(
                surface,
                color=(255, 255, 255, 100),  # slightly more visible
                center=(int(center.x - offset.x), int(center.y - offset.y)),
                radius=self.current_ghost.range,
            )

    def _draw_circle_alpha(
        self,
        surface: pygame.Surface,
        color: tuple,
        center: tuple[int, int],
        radius: float,
    ):
        target_rect = pygame.Rect(
            center[0] - radius, center[1] - radius, radius * 2, radius * 2
        )
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(shape_surf, color, (radius, radius), radius)
        surface.blit(shape_surf, target_rect)
