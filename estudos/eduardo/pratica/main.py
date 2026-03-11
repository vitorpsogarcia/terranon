import pygame
from settings import *
from game import Game

def main():
    pygame.init()
    
    tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_NAME)
    game = Game(tela)
    game.run()
    
    pygame.quit()
    
if __name__ == "__main__":
    main()