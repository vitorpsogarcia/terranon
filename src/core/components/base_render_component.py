from abc import ABC, abstractmethod

import pygame


class BaseRenderComponent(ABC):
    def __init__(self, owner, render_layer: int = 0):
        self.owner = owner
        self._opacity: int = 255
        self._color_tint: pygame.Color | None = None
        self._render_layer = render_layer

    @property
    def render_layer(self) -> int:
        return self._render_layer

    @render_layer.setter
    def render_layer(self, value: int):
        self._render_layer = value

    @property
    def opacity(self) -> int:
        return self._opacity

    @opacity.setter
    def opacity(self, value: int):
        if getattr(self.owner, "_fixed_opacity", False):
            return
        self._opacity = max(0, min(255, int(value)))

    @property
    def color_tint(self) -> pygame.Color | None:
        return self._color_tint

    @color_tint.setter
    def color_tint(self, value: pygame.Color | None):
        self._color_tint = value

    @abstractmethod
    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        """
        Método obrigatório para desenhar o componente na tela.
        :param surface: A tela principal (ou surface da câmera)
        :param offset: O deslocamento da câmera para simular o movimento do mundo
        """
