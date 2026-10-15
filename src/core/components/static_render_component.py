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

        img_to_draw = self.image

        if self.color_tint is not None:
            img_to_draw = self.image.copy()
            img_to_draw.fill(self.color_tint, special_flags=pygame.BLEND_RGB_MULT)

        if self._opacity < 255:
            img_to_draw.set_alpha(self._opacity)
            surface.blit(img_to_draw, draw_pos)
            if img_to_draw is self.image:
                img_to_draw.set_alpha(255)
        else:
            surface.blit(img_to_draw, draw_pos)

    def center(self) -> pygame.Vector2:
        rect = self.image.get_rect(
            topleft=(
                round(self.owner.transform.pos.x),
                round(self.owner.transform.pos.y),
            )
        )
        return pygame.Vector2(rect.center)
