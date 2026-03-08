import pygame
from settings import *
from player import Player

class Game:
    def __init__(self, tela):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(x=AXLE_X_PLAYER, y=AXLE_Y_PLAYER, spritesheet_path=SPRITESHEET_PLAYER)
        
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
    def update(self):
        pass
    
    def draw(self):
        self.tela.fill(COLORS['WHITE'])
        pygame.display.flip()