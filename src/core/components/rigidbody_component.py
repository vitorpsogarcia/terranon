import pygame

from core.component import Component


class RigidbodyComponent(Component):
    def __init__(self, owner):
        super().__init__(owner)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.friction = 0.85
        self.prev_pos = (
            self.owner.transform.pos.copy()
            if hasattr(self.owner, "transform")
            else pygame.math.Vector2(0, 0)
        )

    def update(self, dt: float):
        if not self.active or not hasattr(self.owner, "transform"):
            return

        self.prev_pos = self.owner.transform.pos.copy()

        self.velocity += self.acceleration * dt
        self.velocity *= self.friction

        if self.velocity.length() < 0.01:
            self.velocity = pygame.math.Vector2(0, 0)

        self.owner.transform.pos += self.velocity * dt
