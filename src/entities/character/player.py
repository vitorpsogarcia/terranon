import pygame
from core.settings.settings import SCALE_PLAYER, PLAYER_BASE_SPEED, FRAME_WIDTH_PLAYER, FRAME_HEIGHT_PLAYER
from entities.character.character_animator import CharacterAnimator
from entities.character.characters import Character
from utils.direction import get_direction_str_by_vector
from core.input_manager import InputManager

class Player(Character):
    def __init__(
        self,
        axle_x: float,
        axle_y: float,
        *groups: pygame.sprite.Group
    ):
        super().__init__(axle_x, axle_y, speed=PLAYER_BASE_SPEED, *groups)
        self.frame_width = FRAME_WIDTH_PLAYER
        self.frame_height = FRAME_HEIGHT_PLAYER
        self.scale = SCALE_PLAYER
        self._last_direction = "S"
        self.render_layer = 1
        self._animator = CharacterAnimator("player", self.frame_width, self.frame_height, self.scale)
        self.input_manager = InputManager()

        if not self._animator:

            self.image = pygame.Surface(
                (self.frame_width, self.frame_height)
            ).convert_alpha()

            self.image.fill((0, 255, 0))
            self.rect = self.image.get_rect(topleft=(round(axle_x), round(axle_y)))
        else:
            self._animator.update(0.0, "idle", self._last_direction)
            self.image = self._animator.get_frame()
            self.rect = self.image.get_rect(topleft=(round(axle_x), round(axle_y)))

    def process_event(self, event: pygame.event.Event):
        pass

    def handle_input(self):
        self.direction.x = 0
        self.direction.y = 0

        if self.input_manager.is_action_pressed("UP"):
            self.direction.y -= 1

        if self.input_manager.is_action_pressed("DOWN"):
            self.direction.y += 1

        if self.input_manager.is_action_pressed("LEFT"):
            self.direction.x -= 1

        if self.input_manager.is_action_pressed("RIGHT"):
            self.direction.x += 1

        if self.input_manager.is_action_pressed("RUN"):
            self.speed = PLAYER_BASE_SPEED * 2
        else:
            self.speed = PLAYER_BASE_SPEED

        direction = get_direction_str_by_vector(self.direction)

        if direction is not None:
            self._last_direction = direction

    def update(self, dt: float):
        self.handle_input()
        
        state = "idle"
        if (self.direction.x != 0 or self.direction.y != 0) and state == "idle":
            state = "walking"
            self._animator.animation_speed = 5.0

            if (abs(self.direction.x) > 1 or abs(self.direction.y) > 1):
                state = "running"
                self._animator.animation_speed = 10.0

        if self._animator:
            self._animator.update(dt, state, self._last_direction)
            self.image = self._animator.get_frame()
            
        super().update(dt)