import pygame
class EntitySprite(pygame.sprite.Sprite):
    _opacity = 255


    def __init__(self, owner, *groups: pygame.sprite.Group):
        super().__init__(*groups)
        self.owner = owner


    @property
    def opacity(self):
        return self._opacity


    @opacity.setter
    def opacity(self, value):
        value = max(0, min(255, value))
        self._opacity = value

        if self.image is not None:
            self.image.set_alpha(self._opacity)

    @property
    def image(self):
        return self.__image


    @image.setter
    def image(self, value):
        self.__image = value
        if value is not None:
            self.__image.set_alpha(self._opacity)
            self.rect = self.__image.get_rect()
        else:
            self.rect = None


    def update(self, dt: float):
        if not self.owner.active:
            return
        self.owner.update(dt)
        

    def process_event(self, event: pygame.event.Event):
        self.owner.process_event(event)
        

    def __getattr__(self, name):
        return getattr(self.owner, name)
        