import pygame

from core.components.animator_component import AnimatorComponent
from core.components.collider_component import ColliderComponent
from core.components.health_component import HealthComponent
from core.components.movement_component import MovementComponent
from core.entity import Entity
from core.enums.collider_tag_enum import ColliderTagEnum
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
from utils.image import load_image


class Player(Entity):
    def __init__(self, position: pygame.Vector2, *groups: pygame.sprite.Group):
        super().__init__(position, *groups)

        self.health = self.add_component(
            HealthComponent(
                max_hp=100.0,
                on_death_callback=self.on_death,
                iframes_duration=0.5,
                allow_invulnerability=True,
            )
        )

        self.movement = self.add_component(
            MovementComponent(self, speed=PLAYER_BASE_SPEED)
        )
        self.animator = self.add_component(AnimatorComponent(self))
        self.render_component = self.animator
        self.direction = pygame.math.Vector2(0, 0)
        self.scale = SCALE_PLAYER
        self._last_direction = DirectionsEnum.SOUTH
        self._is_running = False
        self._shooting = False
        self._time_between_shots = 0.3
        self._shot_timer = 0.0
        self.aim_target: pygame.math.Vector2 | None = None

        self.collider = self.add_component(ColliderComponent(self))
        self.body_box = self.collider.add_box(
            -7.5, -15, 15, 30, tag=ColliderTagEnum.BODY
        )
        self.feet_box = self.collider.add_box(-7.5, 5, 15, 10, tag=ColliderTagEnum.FEET)

        self._setup_animations()
        self.animator.play(f"idle_{self._last_direction.text}")
        self.animator.update(0.0)

    @property
    def hitbox(self) -> pygame.Rect:
        return self.body_box.get_world_rect(self.transform.pos)

    @hitbox.setter
    def hitbox(self, value: pygame.Rect):
        pass

    @property
    def feet_hitbox(self) -> pygame.Rect:
        return self.feet_box.get_world_rect(self.transform.pos)

    @feet_hitbox.setter
    def feet_hitbox(self, value: pygame.Rect):
        pass

    @property
    def rect(self) -> pygame.Rect:
        return self.hitbox

    @rect.setter
    def rect(self, value: pygame.Rect):
        pass

    def on_death(self):
        self.active = False
        self.kill()
        EventManager().emit(GameEventEnum.GAME_OVER)

    @property
    def speed(self):
        return self.movement.speed

    @speed.setter
    def speed(self, value):
        self.movement.speed = value

    def apply_knockback(self, source_pos: pygame.math.Vector2, force: float):
        self.movement.apply_knockback(source_pos, force)

    @property
    def frame_width(self) -> int:
        return (
            self.animator.current_frame.get_width()
            if self.animator.current_frame
            else 0
        )

    @property
    def frame_height(self) -> int:
        return (
            self.animator.current_frame.get_height()
            if self.animator.current_frame
            else 0
        )

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

    def shoot_at(self, target_pos: pygame.math.Vector2):
        if self.rect is None:
            return

        start_pos = pygame.math.Vector2(self.rect.center)
        direction = target_pos - start_pos

        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.math.Vector2(0, 1)

        EventManager().emit(
            GameEventEnum.SPAWN_PROJECTILE,
            position=start_pos,
            direction=direction,
            type=ProjectileTypesEnum.NORMAL,
            variant=ProjectileVariantEnum.DEFAULT,
            friendly=True,
        )

        EventManager().emit(GameEventEnum.PLAY_SFX, "effects/shoot.wav")

    def shoot(self):
        if self.aim_target is not None:
            self.shoot_at(self.aim_target)
        elif self.rect is not None:
            facing = (
                self.direction
                if self.direction.length_squared() > 0
                else pygame.math.Vector2(0, 1)
            )
            self.shoot_at(pygame.math.Vector2(self.rect.center) + facing * 100)

    def update(self, dt: float):
        if not self.movement.is_knockedback:
            self.handle_input()
        self._shot_timer += dt

        if self.rect is not None:
            self.prev_rect = self.rect.copy()
        else:
            self.prev_rect = None

        super().update(dt)

        if not self.movement.is_knockedback:
            state = "idle"
            if self.direction.x != 0 or self.direction.y != 0:
                state = "running" if self._is_running else "walking"

            self.animator.play(f"{state}_{self._last_direction.text}")

        if self._shooting and self._shot_timer >= self._time_between_shots:
            self.shoot()
            self._shot_timer = 0.0
