import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x: float, y:float, spritesheet_path: str):
        """

        Inicializa o jogador:
            parametro x (float): Posição inicial no eixo x.
            parametro y (float): Posição inicial no eixo y.
            parametro spritesheet_path (str): Caminho para o arquivo de spritesheet do jogador.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.speed = SPEED_PLAYER
        self.frame_width = FRAME_WIDTH_PLAYER
        self.frame_height = FRAME_HEIGHT_PLAYER
        self.frame = pygame.image.load(spritesheet_path).convert_alpha()
        self.image = self.frame
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    def draw(self, tela):
        """
        Renderiza os elemtnos do jogador na tela:
            parametro tela: A superfície onde o jogador será desenhado.
        """
        tela.blit(self.image, self.rect)
        tela.all.sprites.draw(tela)
        