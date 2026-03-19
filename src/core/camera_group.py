import pygame

class CameraGroup(pygame.sprite.Group):
    super().__init__()
    self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        
        self.half_w = screen_width // 2
        self.half_h = screen_height // 2

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_w
        self.offset.y = player.rect.centery - self.half_h

        for sprite in self.sprites():
            offset_rect = sprite.rect.copy()
            offset_rect.centerx -= self.offset.x
            offset_rect.centery -= self.offset.y
            self.display_surface.blit(sprite.image, offset_rect)