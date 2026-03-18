import pygame

from core.game_manager import GameManager
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_NAME

def main():
    pygame .init()
    
    tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_NAME)
    game_manager = GameManager(tela)

    game_manager.on_execute()
    
    pygame.quit()
    
if __name__ == "__main__":
    main()