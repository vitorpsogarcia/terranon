import pygame
from .settings import COLORS_GAME, FPS

class GameManager:
    def __init__(self, tela):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self._running = True

    
    def on_execute(self):
        while (self._running):
            self.clock.tick(FPS)
            self.on_events()
            self.update()
            self.on_render()
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