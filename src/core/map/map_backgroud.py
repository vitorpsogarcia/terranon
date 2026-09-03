import pygame

from core.components.static_render_component import StaticRenderComponent  # NOVO IMPORT
from core.game_object import GameObject


class MapBackground(GameObject):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface):
        super().__init__(position)
        self.render_component = StaticRenderComponent(self, image)
        self.render_component.render_layer = -1

        self._fixed_layer = True

    def update(self, dt: float):
        pass
