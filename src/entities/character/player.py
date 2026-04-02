import pygame
from core.enums.character_state_enum import CharacterStateEnum
from core.settings.settings import PLAYER_KEYS, SCALE_PLAYER, PLAYER_BASE_SPEED
from entities.character.character_animator import CharacterAnimator
from entities.character.characters import Character
from utils.direction import get_direction_str_by_vector

class Player(Character):
    def __init__(self, axle_x: float, axle_y: float, *groups: pygame.sprite.Group):
        super().__init__(axle_x, axle_y, speed=PLAYER_BASE_SPEED, *groups)
        self.scale = SCALE_PLAYER
        self._last_direction = "S"
        self.render_layer = 1

        self._animator = CharacterAnimator("player", scale=self.scale)
        
        self._animator.update(0.0, CharacterStateEnum.IDLE, self._last_direction)
        self.image = self._animator.get_frame()
        self.rect = self.image.get_rect(topleft=(round(axle_x), round(axle_y)))
    
    @property
    def frame_width(self) -> int:
        return self.image.get_width() if self.image else 0
    
    @property
    def frame_height(self) -> int:
        return self.image.get_height() if self.image else 0

    def process_event(self, event: pygame.event.Event):
        pass

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0

        if keys[PLAYER_KEYS["UP"]]:
            self.direction.y -= 1
        if keys[PLAYER_KEYS["DOWN"]]:
            self.direction.y += 1
        if keys[PLAYER_KEYS["LEFT"]]:
            self.direction.x -= 1
        if keys[PLAYER_KEYS["RIGHT"]]:
            self.direction.x += 1

        if keys[PLAYER_KEYS["RUN"]]:
            self.speed = PLAYER_BASE_SPEED * 2
        else:
            self.speed = PLAYER_BASE_SPEED

        direction = get_direction_str_by_vector(self.direction)
        if direction is not None:
            self._last_direction = direction

    def update(self, dt: float):
        self.handle_input()

        state = CharacterStateEnum.IDLE
        if self.direction.x != 0 or self.direction.y != 0:
            state = CharacterStateEnum.MOVING


        self._animator.update(dt, state, self._last_direction)
        self.image = self._animator.get_frame()
        

        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        
        super().update(dt)
