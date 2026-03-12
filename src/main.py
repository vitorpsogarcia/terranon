import pygame
from settings import *
from game import GameManager

def main():
    pygame .init()
    
    tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_NAME)
    game = GameManager(tela)
    game.on_execute()
    
    pygame.quit()
    
if __name__ == "__main__":
    main()