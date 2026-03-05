import pygame

from core.game_object import GameObject

SCREEN_SIZE = (1280, 720)

class GameManager:
    def __init__(self):
        self._running = True
        self._display_surface = None
        self.size = self.width, self.height = SCREEN_SIZE
    
    
    def on_init(self):
        pygame.init()
        self._display_surface = pygame.display.set_mode(self.size, pygame.DOUBLEBUF)
        self._running = True

    
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    
    
    def on_loop(self):
        pass

    
    def on_render(self):
        pass

    
    def on_cleanup(self):
        pygame.quit()
    

    def on_execute(self):
        if self.on_init() == False:
            self._running = False        
        
        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)
            
            self.on_loop()
            self.on_render()
        self.on_cleanup()
