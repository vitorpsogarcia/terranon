import random
import pygame

from core.singleton_meta import SingletonMeta


class FloatingText:
    def __init__(
        self,
        pos: pygame.Vector2,
        text: str,
        color: tuple,
        font: pygame.font.Font,
        duration: float = 0.7,
    ):
        self.pos = pygame.Vector2(pos.x + random.uniform(-10, 10), pos.y - 10)
        self.text = text
        self.color = color
        self.font = font
        self.duration = duration
        self.timer = duration
        self.velocity = pygame.Vector2(0, -35)

    def update(self, dt: float) -> bool:
        self.timer -= dt
        self.pos.y += self.velocity.y * dt
        self.velocity.y *= 0.95
        return self.timer > 0

    def draw(self, surface: pygame.Surface, camera_offset: pygame.Vector2):
        if self.duration <= 0:
            return
        alpha = max(0, min(255, int(255 * (self.timer / self.duration))))
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)
        draw_pos = self.pos - camera_offset
        surface.blit(text_surface, draw_pos)


class Particles:
    def __init__(
        self,
        pos: pygame.Vector2,
        velocity: pygame.Vector2,
        color: tuple,
        size: float,
        duration: float,
    ):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.color = color
        self.size = size
        self.duration = duration
        self.timer = duration

    def update(self, dt: float) -> bool:
        self.timer -= dt
        self.pos += self.velocity * dt
        self.velocity *= 0.95
        return self.timer > 0

    def draw(self, surface: pygame.Surface, camera_offset: pygame.Vector2):
        if self.duration <= 0:
            return
        scale = max(0.0, self.timer / self.duration)
        current_size = max(1, int(self.size * scale))
        draw_pos = (
            int(self.pos.x - camera_offset.x),
            int(self.pos.y - camera_offset.y),
        )
        pygame.draw.circle(surface, self.color, draw_pos, current_size)


class EffectManager(metaclass=SingletonMeta):
    def __init__(self):
        self.texts: list[FloatingText] = []
        self.particles: list[Particles] = []
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

    def add_floating_text(
        self,
        pos: pygame.Vector2,
        text: str,
        color: tuple = (255, 220, 50),
    ):
        self.texts.append(FloatingText(pos, text, color, self.font))

    def add_particle(
        self,
        pos: pygame.Vector2,
        count: int = 8,
        color: tuple = (255, 200, 50),
        speed: float = 120.0,
    ):
        for _ in range(count):
            angle = random.uniform(0, 360)
            spd = random.uniform(speed * 0.4, speed)
            velocity = pygame.Vector2(spd, 0).rotate(angle)
            size = random.uniform(2, 4.5)
            duration = random.uniform(0.3, 0.6)
            self.particles.append(Particles(pos, velocity, color, size, duration))

    def update(self, dt: float):
        self.texts = [t for t in self.texts if t.update(dt)]
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2):
        for p in self.particles:
            p.draw(surface, camera_offset)
        for t in self.texts:
            t.draw(surface, camera_offset)

    def clear(self):
        self.texts.clear()
        self.particles.clear()