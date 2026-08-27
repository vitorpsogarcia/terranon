import pygame


class MovementComponent:
    def __init__(self, owner: "Entity", speed: float = 100.0):
        self.owner = owner
        self.speed = speed
        self.is_knockedback = False
        self.knockback_timer = 0.0

    def apply_knockback(self, source_pos: pygame.math.Vector2, force: float):
        direction = self.owner.pos - source_pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.math.Vector2(0, -1)

        self.owner.velocity += direction * force
        self.is_knockedback = True
        self.knockback_timer = 0.2

    def update(self, dt: float):
        if self.is_knockedback:
            self.knockback_timer -= dt
            if self.knockback_timer <= 0:
                self.is_knockedback = False
                self.owner.velocity = pygame.math.Vector2(0, 0)
            return

        direction = getattr(self.owner, "direction", pygame.math.Vector2(0, 0))
        if direction.length() > 0:
            direction = direction.normalize()

        self.owner.velocity = direction * self.speed
