import pygame

from core.component import Component
from core.game_object import GameObject


class MovementComponent(Component):
    def __init__(self, owner: "GameObject", speed: float = 100.0):
        self.owner = owner
        self.speed = speed
        self.is_knockedback = False
        self.knockback_timer = 0.0

    def apply_knockback(self, source_pos: pygame.math.Vector2, force: float):
        direction = self.owner.transform.pos - source_pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.math.Vector2(0, -1)

        if hasattr(self.owner, "rigidbody"):
            self.owner.rigidbody.velocity += direction * force
        self.is_knockedback = True
        self.knockback_timer = 0.2

    def update(self, dt: float):
        if self.is_knockedback:
            self.knockback_timer -= dt
            if self.knockback_timer <= 0:
                self.is_knockedback = False
                if hasattr(self.owner, "rigidbody"):
                    self.owner.rigidbody.velocity = pygame.math.Vector2(0, 0)
            return

        direction = getattr(self.owner, "direction", pygame.math.Vector2(0, 0))
        if direction.length() > 0:
            direction = direction.normalize()

        if hasattr(self.owner, "rigidbody"):
            self.owner.rigidbody.velocity = direction * self.speed
