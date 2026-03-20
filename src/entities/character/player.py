import pygame
from core.settings import SCALE_PLAYER, SPEED_PLAYER, FRAME_WIDTH_PLAYER, FRAME_HEIGHT_PLAYER
from entities.character.character_animator import CharacterAnimator
from entities.character.characters import Character
from utils.direction import get_direction_str_by_vector
class Player(Character):
    _animator: CharacterAnimator | None = None
    
    def __init__(
        self,
        axle_x: float,
        axle_y: float,
    ):
        super().__init__(axle_x, axle_y, speed=SPEED_PLAYER)
        self.frame_width = FRAME_WIDTH_PLAYER
        self.frame_height = FRAME_HEIGHT_PLAYER
        self.scale = SCALE_PLAYER
        self._last_direction = "S"
        self._layer = 1


        try:
            self._animator = CharacterAnimator("player", self.frame_width, self.frame_height, self.scale)
        except FileNotFoundError:
            self.frame = pygame.Surface(
                (self.frame_width, self.frame_height)
            ).convert_alpha()
            self.frame.fill((0, 255, 0))

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
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_w]:
            self.direction.y -= 1

        if keys[pygame.K_s]:
            self.direction.y += 1

        if keys[pygame.K_a]:
            self.direction.x -= 1

        if keys[pygame.K_d]:
            self.direction.x += 1
    
        direction = get_direction_str_by_vector(self.direction)

        if direction is not None:
            self._last_direction = direction

    def update(self, dt: float):
        self.handle_input()
        
        state = "idle"
        if self.direction.x != 0 or self.direction.y != 0:
            state = "running"

        if self._animator:
            self._animator.update(dt, state, self._last_direction)
            self.image = self._animator.get_frame()
            
        super().update(dt)
