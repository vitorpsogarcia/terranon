import logging

import pygame

from core.debug_manager import DebugManager
from core.game_object import GameObject


class CameraGroup(pygame.sprite.LayeredUpdates):
    _logger = logging.getLogger("CameraGroup")
    _target: GameObject | None

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

        self.zoom = 0.75
        self.zoom_speed = 0.1
        self.zoom_min = 0.5
        self.zoom_max = 2.0
        self._target = None

    @property
    def target(self):
        if self._target is None:
            raise AttributeError("Target is not set for CameraGroup.")

        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    def handle_zoom(self, scroll_amount):
        self.zoom -= scroll_amount * self.zoom_speed
        self.zoom = max(self.zoom_min, min(self.zoom_max, self.zoom))

    def custom_draw(self, surface: pygame.Surface, player=None):
        if player is None:
            player = self._target

        if player is None or player.rect is None:
            self.draw(surface)
            return

        dummy_width = int(self.display_surface.get_width() * self.zoom)
        dummy_height = int(self.display_surface.get_height() * self.zoom)

        self.offset.x = player.rect.centerx - (dummy_width // 2)
        self.offset.y = player.rect.centery - (dummy_height // 2)

        dummy_surface = pygame.Surface((dummy_width, dummy_height))
        dummy_surface.fill((20, 20, 20))

        for sprite in sorted(self.sprites(), key= lambda spr: spr.render_layer):
            offset_pos = sprite.rect.topleft - self.offset
            dummy_surface.blit(sprite.image, offset_pos)

        scaled_surface = pygame.transform.scale(dummy_surface, self.display_surface.get_size())

        self.display_surface.blit(scaled_surface, (0, 0))
        DebugManager.draw_world_debug(surface, self)
