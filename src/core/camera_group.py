import pygame

class CameraGroup(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.target = None

    def set_target(self, target):
        self.target = target

    def custom_draw(self, surface: pygame.Surface):
        if self.target and hasattr(self.target, 'rect'):
            self.offset.x = self.target.rect.centerx - self.half_w
            self.offset.y = self.target.rect.centery - self.half_h

        for sprite in self.sprites():
            if sprite.active and sprite.image and sprite.rect:
                offset_pos = sprite.rect.topleft - self.offset
                surface.blit(sprite.image, offset_pos)
