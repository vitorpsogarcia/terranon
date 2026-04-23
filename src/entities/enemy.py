import pygame
from entities.character.characters import Character
from utils.direction import get_direction_str_by_vector


class Enemy(Character):
    def __init__(self, x: float, y: float, target: any, speed: float = 50.0, *groups: pygame.sprite.Group):
        super().__init__(x, y, speed, *groups)

        self.target = target
        
        if self.image is None:
            self.image = pygame.Surface((48, 48)).convert_alpha()
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect(topleft=(round(x), round(y)))

    def update(self, dt: float):
        if self.target and getattr(self.target, 'active', True) and self.target.rect:
            
            target_pos = pygame.math.Vector2(
                self.target.rect.centerx, self.target.rect.centery)
            self_pos = pygame.math.Vector2(
                self.rect.centerx, self.rect.centery)

            direction_vector = target_pos - self_pos
            distance = direction_vector.length()

            if distance > 2.0:
                self.direction = direction_vector.normalize()
                estado_animacao = "walking"
            else:
                self.direction = pygame.math.Vector2(0, 0)
                estado_animacao = "idle"

        else:
            self.direction = pygame.math.Vector2(0, 0)
            estado_animacao = "idle"

        self.current_state = estado_animacao
        dir_str = get_direction_str_by_vector(self.direction)
        if dir_str is not None:
            self.last_direction = dir_str

        super().update(dt)
