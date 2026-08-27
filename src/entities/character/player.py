import pygame

from core.enums.directions_enum import DirectionsEnum
from core.enums.game_event_enum import GameEventEnum
from core.enums.projectile.projectile_types_enum import ProjectileTypesEnum
from core.enums.projectile.projectile_variant_enum import ProjectileVariantEnum
from core.manager.event_manager import EventManager
from core.settings.settings import (
    ASSETS_FOLDER,
    PLAYER_BASE_SPEED,
    PLAYER_KEYS,
    SCALE_PLAYER,
)
from entities.character.characters import Character
from utils.image import load_image


class Player(Character):
    def __init__(self, position: pygame.Vector2, *groups: pygame.sprite.Group):
        super().__init__(
            position, PLAYER_BASE_SPEED, *groups, allow_invulnerability=True
        )
        self.scale = SCALE_PLAYER
        self._last_direction = DirectionsEnum.SOUTH
        self._is_running = False
        self._shooting = False
        self._time_between_shots = 0.3
        self._shot_timer = 0.0

        self.hitbox = pygame.Rect(self.pos.x, self.pos.y, 15, 30)
        self.rect = self.hitbox
        self.feet_hitbox = pygame.Rect(self.pos.x, self.pos.y, 15, 10)

        self._setup_animations()
        self.animator.play(f"idle_{self._last_direction.text}")
        self.animator.update(0.0)
        if self.rect is not None:
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def on_death(self):
        on_death = super().on_death()
        EventManager.get_instance().emit(GameEventEnum.GAME_OVER)

        return on_death

    @property
    def frame_width(self) -> int:
        return self.animator.current_frame.get_width() if self.animator.current_frame else 0

    @property
    def frame_height(self) -> int:
        return self.animator.current_frame.get_height() if self.animator.current_frame else 0

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._shooting = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._shooting = False

    def _setup_animations(self):
        player_root = ASSETS_FOLDER / "images" / "player"

        for direction in DirectionsEnum.to_list():
            direction_value = direction.text
            idle_path = player_root / "idle" / f"{direction_value}.png"
            running_dir = player_root / "animations" / "moving" / direction_value

            try:
                idle_frame = load_image(idle_path, scale=self.scale)
            except FileNotFoundError:
                continue

            running_frames = []
            for i in range(8):
                run_path = running_dir / f"{i}.png"
                try:
                    running_frames.append(load_image(run_path, scale=self.scale))
                except FileNotFoundError:
                    break

            move_frames = running_frames if running_frames else [idle_frame]

            self.animator.add_animation(
                f"idle_{direction_value}", [idle_frame], frame_duration=1.0
            )
            self.animator.add_animation(
                f"walking_{direction_value}", move_frames, frame_duration=1 / 7.0
            )
            self.animator.add_animation(
                f"running_{direction_value}", move_frames, frame_duration=1 / 10.0
            )

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

        self._is_running = bool(keys[PLAYER_KEYS["RUN"]])
        if self._is_running:
            self.speed = PLAYER_BASE_SPEED * 2
        else:
            self.speed = PLAYER_BASE_SPEED

        direction = DirectionsEnum.get_by_vector(self.direction)
        if direction is not None:
            self._last_direction = direction

    def shoot(self):
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())

        if self.rect is not None:
            camera_offset = pygame.math.Vector2(0, 0)
            for group in self._sprite.groups():
                if hasattr(group, "offset"):
                    camera_offset = group.offset
                    break

            start_pos = pygame.math.Vector2(self.rect.center)
            world_mouse_pos = mouse_pos + camera_offset
            direction = world_mouse_pos - start_pos

            if direction.length() > 0:
                direction = direction.normalize()
            else:
                direction = pygame.math.Vector2(0, 1)

            EventManager.get_instance().emit(
                GameEventEnum.SPAWN_PROJECTILE,
                position=start_pos,
                direction=direction,
                type=ProjectileTypesEnum.NORMAL,
                variant=ProjectileVariantEnum.DEFAULT,
                friendly=True,
            )

            EventManager.get_instance().emit(
                GameEventEnum.PLAY_SFX, "effects/shoot.wav"
            )

    def update(self, dt: float):
        if not self.is_knockedback:
            self.handle_input()
        self._shot_timer += dt

        self.prev_pos = self.pos.copy()
        if self.rect is not None:
            self.prev_rect = self.rect.copy()
        else:
            self.prev_rect = None

        super().update(dt)

        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        self.feet_hitbox.midbottom = self.hitbox.midbottom

        if not self.is_knockedback:
            state = "idle"
            if self.direction.x != 0 or self.direction.y != 0:
                state = "running" if self._is_running else "walking"

            self.animator.play(f"{state}_{self._last_direction.text}")

        if self.rect is not None:
            self.rect.center = self.hitbox.center

        if self._shooting and self._shot_timer >= self._time_between_shots:
            self.shoot()
            self._shot_timer = 0.0
