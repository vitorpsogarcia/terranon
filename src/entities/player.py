import pygame
from core.settings import SPEED_PLAYER, FRAME_WIDTH_PLAYER, FRAME_HEIGHT_PLAYER

class Player(pygame.sprite.Sprite):
    def __init__(self, axle_x: float, axle_y: float):
        super().__init__()
        self.x = axle_x
        self.y = axle_y
        self.speed = SPEED_PLAYER
        self.frame_width: FRAME_WIDTH_PLAYER
        self.frame_height: FRAME_HEIGHT_PLAYER
        self.frame = pygame.image.load(spritesheet_path).convert_alpha()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.direction.y = -1
            
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0
            
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0
            
    def draw(self, tela):
        tela.blit(self.image, self.rect)
        tela.all.sprites.draw(tela)