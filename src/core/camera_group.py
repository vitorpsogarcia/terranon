import logging

import pygame

from core.game_object import GameObject, StaticObject
from core.manager.debug_manager import DebugManager


class CameraGroup(pygame.sprite.LayeredUpdates):
    _logger = logging.getLogger("CameraGroup")
    _target: GameObject | None

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        if self.display_surface is not None:
            self.half_w = self.display_surface.get_size()[0] // 2
            self.half_h = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self._target = None

    @property
    def target(self):
        if self._target is None:
            raise AttributeError("Target is not set for CameraGroup.")

        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    def custom_draw(self, surface: pygame.Surface):
        if self.target.rect is None:
            return

        self.offset.x = self.target.rect.centerx - self.half_w
        self.offset.y = self.target.rect.centery - self.half_h

        target_pos, target_layer = self.target.pos, self.target.render_layer

        for sprite in self.sprites():
            owner = getattr(sprite, "owner", None)
            if owner is not None:
                offset_pos = sprite.rect.topleft - self.offset

                if isinstance(owner, StaticObject):
                    distance = target_pos.distance_to(owner.pos)
                    if distance < 200 and (
                        target_layer - 75 < owner.render_layer < target_layer + 75
                    ):
                        owner._sprite.opacity = 128
                    else:
                        owner._sprite.opacity = 255

                surface.blit(sprite.image, offset_pos)

        DebugManager().draw_world_debug(surface, self)
