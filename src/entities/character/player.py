import pygame
from core.settings.settings import PLAYER_KEYS, SCALE_PLAYER, PLAYER_BASE_SPEED, FRAME_WIDTH_PLAYER, FRAME_HEIGHT_PLAYER
from entities.character.character_animator import CharacterAnimator
from entities.character.characters import Character
from core.animator_component import AnimatorComponent
from utils.direction import get_direction_str_by_vector

class Player(Character):
    def __init__(self, axle_x: float, axle_y: float, *groups: pygame.sprite.Group):
        super().__init__(axle_x, axle_y, speed=PLAYER_BASE_SPEED, *groups)
        self.frame_width = FRAME_WIDTH_PLAYER
        self.frame_height = FRAME_HEIGHT_PLAYER
        self.scale = SCALE_PLAYER
        self._last_direction = "S"
        self.render_layer = 1

        self.animator = AnimatorComponent(self)

        legacy = CharacterAnimator("player", self.frame_width, self.frame_height, self.scale)

        if not getattr(legacy, "sprites", None):
            self.image = pygame.Surface((self.frame_width, self.frame_height)).convert_alpha()
            self.image.fill((0, 255, 0))
            self.rect = self.image.get_rect(topleft=(round(axle_x), round(axle_y)))
        else:
            for direction, frames in legacy.sprites.items():
                if isinstance(frames, pygame.Surface):
                    self.animator.add_animation(f"idle_{direction}", [frames], frame_duration=1.0)
                    self.animator.add_animation(f"walking_{direction}", [frames], frame_duration=1.0)
                    self.animator.add_animation(f"running_{direction}", [frames], frame_duration=1.0)
                else:
                    idle = frames[0]
                    run_frames = frames[1:] if len(frames) > 1 else [idle]
                    self.animator.add_animation(f"idle_{direction}", [idle], frame_duration=1.0)
                    self.animator.add_animation(f"walking_{direction}", run_frames, frame_duration=1/5.0)
                    self.animator.add_animation(f"running_{direction}", run_frames, frame_duration=1/10.0)

            self.animator.play(f"idle_{self._last_direction}")
            self.animator.update(0.0)
            self.rect.topleft = (round(axle_x), round(axle_y))

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

        state = "idle"
        if self.direction.x != 0 or self.direction.y != 0:
            state = "walking"
            if (abs(self.direction.x) > 1 or abs(self.direction.y) > 1):
                state = "running"

        anim_name = f"{state}_{self._last_direction}"
        self.animator.play(anim_name)
        self.animator.update(dt)

        super().update(dt)
