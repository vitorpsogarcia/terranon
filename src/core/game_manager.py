import pygame
from .settings import COLORS_GAME, FPS, AXLE_X_PLAYER, AXLE_Y_PLAYER
from entities.player import Player

class GameManager:
    def __init__(self, tela):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self._running = True
        self.player = Player(AXLE_X_PLAYER, AXLE_Y_PLAYER)
    
    def on_execute(self):
        while (self._running):
            self.clock.tick(FPS)
            self.on_events()
            self.update()
            self.on_render()
            
            DELTA_TIME = self.clock.tick(60) / 1000
            DELTA_TIME = max(0.001, min(0.01, DELTA_TIME)) 
    
        self.on_cleanup()
    
    def on_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                
            elif event.type == pygame.KEYUP:
                self.on_key_up()
                
            elif event.type == pygame.KEYDOWN:
                self.on_key_down()
                
    def update(self):
        pass
    
    def on_render(self):
        self.tela.fill(COLORS_GAME['BLACK'])
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
    
    def on_loop(self):
        pass

    def on_key_up(self):
        pass
    
    def on_key_down(self):
        pass