import pygame


class EntitySprite(pygame.sprite.Sprite):
    def __init__(self, owner, *groups: pygame.sprite.Group):
        super().__init__(*groups)
        self.owner = owner

        # [Temporário] Imagem fantasma apenas para o CameraGroup (LayeredUpdates)
        # não dar AttributeError no blit nativo antes da HU #93.
        self.image = pygame.Surface((0, 0))
        self.image.set_alpha(0)
        self.rect = pygame.Rect(0, 0, 10, 10)

    def update(self, dt: float):
        if not self.owner.active:
            return
        
        self.owner.update(dt)
        fonte_fisica = getattr(self.owner, 'hitbox',
                               getattr(self.owner, 'rect', None))

        if fonte_fisica is not None:
            self.rect.size = fonte_fisica.size
            self.rect.center = fonte_fisica.center

    def process_event(self, event: pygame.event.Event):
        self.owner.process_event(event)

    def __getattr__(self, name):
        return getattr(self.owner, name)
