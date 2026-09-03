import pygame

from core.components.base_render_component import BaseRenderComponent


class StaticRenderComponent(BaseRenderComponent):
    def __init__(self, owner, image: pygame.Surface):
        super().__init__(owner)
        self.image = image

    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        if not self.image:
            return

        draw_pos = self.owner.transform.pos - offset

        if self._opacity < 255:
            self.image.set_alpha(self._opacity)
            surface.blit(self.image, draw_pos)
            self.image.set_alpha(255)
        else:
            surface.blit(self.image, draw_pos)

    def center(self) -> pygame.Vector2:
        rect = self.image.get_rect(
            topleft=(
                round(self.owner.transform.pos.x),
                round(self.owner.transform.pos.y),
            )
        )
        return pygame.Vector2(rect.center)
