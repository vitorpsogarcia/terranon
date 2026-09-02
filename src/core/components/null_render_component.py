import pygame

from core.components.base_render_component import BaseRenderComponent


class NullRenderComponent(BaseRenderComponent):
    def __init__(self, owner):
        super().__init__(owner)

    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        pass
