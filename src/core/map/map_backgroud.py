import pygame
from core.game_object import StaticObject
from core.components.static_render_component import StaticRenderComponent  # NOVO IMPORT


class MapBackground(StaticObject):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface):
        super().__init__(position)
        self.render_component = StaticRenderComponent(self, image)

        self.render_layer = -1
        self._fixed_layer = True

    def update(self, dt: float):
        pass
