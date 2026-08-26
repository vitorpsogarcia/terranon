from abc import ABC, abstractmethod
import pygame


class BaseRenderComponent(ABC):
    def __init__(self, owner):
        self.owner = owner

    @abstractmethod
    def draw(self, surface: pygame.Surface, offset: pygame.math.Vector2):
        """
        Método obrigatório para desenhar o componente na tela.
        :param surface: A tela principal (ou surface da câmera)
        :param offset: O deslocamento da câmera para simular o movimento do mundo
        """
        pass
