import pygame
class EntitySprite(pygame.sprite.Sprite):
    def __init__(self, owner, *groups: pygame.sprite.Group):
        super().__init__(*groups)
        self.owner = owner

    def update(self, dt: float):
        if not self.owner.active:
            return
        self.owner.update(dt)
        
    def process_event(self, event: pygame.event.Event):
        self.owner.process_event(event)
        
    def __getattr__(self, name):
        return getattr(self.owner, name)
        