import pygame

from core.animator_component import AnimatorComponent
from core.game_object import DynamicObject
from core.health_component import HealthComponent


class Character(DynamicObject):
    def __init__(
        self,
        initial_position: pygame.Vector2,
        speed: float = 100.0,
        *groups: pygame.sprite.Group,
    ):
        super().__init__(initial_position, *groups)
        self.animator = AnimatorComponent(self)
        self.health = HealthComponent(
            max_hp=100.0, on_death_callback=self.on_death, iframes_duration=0.5
        )
        self.speed = speed
        self.direction = pygame.math.Vector2(0, 0)
        self.is_knockedback = False
        self.knockback_timer = 0.0

    def move(self, dt: float):
        if self.is_knockedback:
            self.prev_pos = self.pos.copy()
            self.pos += self.velocity * dt
            self.velocity *= self.friction
            self.knockback_timer = 0
            if self.knockback_timer <= 0:
                self.is_knockedback = False
                self.velocity = pygame.math.Vector2(0, 0)
            return

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        input_velocity = self.direction * self.speed

        self.velocity = input_velocity + getattr(
            self, "knockback_velocity", pygame.math.Vector2(0, 0)
        )

    def apply_knockback(self, source_pos: pygame.math.Vector2, force: float):
        direction = self.pos - source_pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.math.Vector2(0, -1)
        self.velocity += direction * force

        self.is_knockedback = True
        self.knockback_timer = 0.0

    def apply_knockback_from_direction(
        self, direction: pygame.math.Vector2, force: float
    ):
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.velocity += direction * force

    def update(self, dt: float):
        if not self.active:
            return

        self.health.update(dt)
        self.move(dt)
        self.animator.update(dt)
        super().update(dt)

    def on_death(self):
        self.active = False
        self.kill()
