import pygame
from core.map.waypoints.polyline import Polyline
from core.map.waypoints.waypoint import Waypoint
from entities.character.characters import Character
from utils.direction import get_direction_str_by_vector

class Enemy(Character):
    current_waypoint: Waypoint
    def __init__(self, x: float, y: float, path: Polyline, speed: float = 50.0, *groups: pygame.sprite.Group):
        super().__init__(x, y, speed, *groups)

        self.path = path
        self.current_waypoint = self.path.get_start_waypoint()
        
        if self.image is None:
            self.image = pygame.Surface((20, 48)).convert_alpha()
            self.image.fill((111, 0, 0))
            self.rect = self.image.get_rect(topleft=(round(x), round(y)))

    def update(self, dt: float):
        next_waypoint = self.path.get_next_waypoint(self.current_waypoint)

        if next_waypoint is not None and self.rect is not None:
            target_pos = next_waypoint.position
            self_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)

            direction_vector = target_pos - self_pos
            distance = direction_vector.length()

            if distance > 5.0:
                self.direction = direction_vector.normalize()
                estado_animacao = "walking"
            else:
                self.current_waypoint = next_waypoint
                self.direction = pygame.math.Vector2(0, 0)
                estado_animacao = "walking"

        else:
            self.direction = pygame.math.Vector2(0, 0)
            estado_animacao = "idle"
            
            # TODO: Disparar evento de Dano à Base (vitor: Depende, e se o inimigo não estiver sobre a base? Seria melhor deixar para o colisor da base lidar com isso)
            # EventManager.get_instance().emit(GameEventEnum.BASE_DAMAGED, dano=10)
            
            self.health.take_damage(9999)

        self.current_state = estado_animacao
        dir_str = get_direction_str_by_vector(self.direction)
        if dir_str is not None:
            self.last_direction = dir_str

        super().update(dt)
