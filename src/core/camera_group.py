import logging

import pygame

from core.debug_manager import DebugManager


class CameraGroup(pygame.sprite.LayeredUpdates):
    _logger = logging.getLogger("CameraGroup")

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        if self.display_surface is not None:
            self.half_w = self.display_surface.get_size()[0] // 2
            self.half_h = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.target = None

    def set_target(self, target):
        self.target = target

    def custom_draw(self, surface: pygame.Surface):
        if self.target and hasattr(self.target, "rect"):
            self.offset.x = self.target.rect.centerx - self.half_w
            self.offset.y = self.target.rect.centery - self.half_h

        for sprite in self.sprites():
            owner = getattr(sprite, "owner", None)
            if getattr(owner, "active", True):
                offset_pos = sprite.rect.topleft - self.offset
                surface.blit(sprite.image, offset_pos)

        DebugManager.draw_world_debug(surface, self)
