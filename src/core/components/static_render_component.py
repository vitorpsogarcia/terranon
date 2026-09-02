import pygame

from core.components.base_render_component import BaseRenderComponent


class StaticRenderComponent(BaseRenderComponent):
    def __init__(self, owner, image: pygame.Surface):
        super().__init__(owner)
        self.image = image

    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        if not self.image:
            return

        draw_pos = self.owner.pos - offset

        if self._opacity < 255:
            self.image.set_alpha(self._opacity)
            surface.blit(self.image, draw_pos)
            self.image.set_alpha(255)
        else:
            surface.blit(self.image, draw_pos)
