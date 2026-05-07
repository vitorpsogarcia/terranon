import pygame
from typing import List
from entities.character.characters import Character
from utils.direction import get_direction_str_by_vector
from core.event_manager import EventManager
from core.enums.game_event_enum import GameEventEnum

class Enemy(Character):
    def __init__(self, x: float, y: float, path: List[pygame.math.Vector2], speed: float = 50.0, *groups: pygame.sprite.Group):
        super().__init__(x, y, speed, *groups)

        self.path = path
        self.current_waypoint_index = 0
        
        if self.image is None:
            self.image = pygame.Surface((20, 48)).convert_alpha()
            self.image.fill((111, 0, 0))
            self.rect = self.image.get_rect(topleft=(round(x), round(y)))

    def update(self, dt: float):
        if self.current_waypoint_index < len(self.path):
            
            target_pos = self.path[self.current_waypoint_index]
            self_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)

            direction_vector = target_pos - self_pos
            distance = direction_vector.length()

            if distance > 5.0:
                self.direction = direction_vector.normalize()
                estado_animacao = "walking"
            else:
                self.current_waypoint_index += 1
                self.direction = pygame.math.Vector2(0, 0)
                estado_animacao = "walking"
                
        else:
            self.direction = pygame.math.Vector2(0, 0)
            estado_animacao = "idle"
            
            # TODO: Disparar evento de Dano à Base
            # EventManager.get_instance().emit(GameEventEnum.BASE_DAMAGED, dano=10)
            
            self.health.take_damage(9999)

        self.current_state = estado_animacao
        dir_str = get_direction_str_by_vector(self.direction)
        if dir_str is not None:
            self.last_direction = dir_str

        super().update(dt)
