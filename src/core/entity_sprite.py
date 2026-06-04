import pygame

class EntitySprite(pygame.sprite.Sprite):
    def __init__(self, owner, *groups: pygame.sprite.Group):
        super().__init__(*groups)
        self.owner = owner

    def update(self, dt: float):
        if hasattr(self.owner, 'active') and not self.owner.active:
            return
        if hasattr(self.owner, 'update'):
            return self.owner.update(dt)
        
    def process_event(self, event: pygame.event.Event):
        if hasattr(self.owner, 'process_event'):
            return self.owner.process_event(event)
        
    def __getattr__(self, name):
        return getattr(self.owner, name)