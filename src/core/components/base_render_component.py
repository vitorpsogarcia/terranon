from abc import ABC, abstractmethod

import pygame


class BaseRenderComponent(ABC):
    def __init__(self, owner):
        self.owner = owner
        self._opacity: int = 255

    @property
    def opacity(self) -> int:
        return self._opacity

    @opacity.setter
    def opacity(self, value: int):
        if getattr(self.owner, "_fixed_opacity", False):
            return
        self._opacity = max(0, min(255, int(value)))

    @abstractmethod
    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        """
        Método obrigatório para desenhar o componente na tela.
        :param surface: A tela principal (ou surface da câmera)
        :param offset: O deslocamento da câmera para simular o movimento do mundo
        """
