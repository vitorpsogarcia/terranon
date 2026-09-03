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
        self._sync_rect()

    def _sync_rect(self):
        if hasattr(self.owner, "collider") and self.owner.collider:
            bounding = self.owner.collider.get_bounding_rect()
            if bounding:
                self.rect.size = bounding.size
                self.rect.center = bounding.center
                return
        
        if hasattr(self.owner, "transform"):
            self.rect.center = (round(self.owner.transform.pos.x), round(self.owner.transform.pos.y))


    def update(self, dt: float):
        if not getattr(self.owner, "active", False):
            return

        self.owner.update(dt)
        self._sync_rect()

    def process_event(self, event: pygame.event.Event):
        if hasattr(self.owner, "process_event"):
            self.owner.process_event(event)

    def __getattr__(self, name):
        return getattr(self.owner, name)
