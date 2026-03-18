import pygame
from core.settings import SPEED_PLAYER, FRAME_WIDTH_PLAYER, FRAME_HEIGHT_PLAYER
from entities.characters import Character


class Player(Character):
    def __init__(
        self,
        axle_x: float,
        axle_y: float,
        spritesheet_path: str = "assets/player_spritesheet.png",
    ):

        super().__init__(axle_x, axle_y, speed=SPEED_PLAYER)
        self.frame_width = FRAME_WIDTH_PLAYER
        self.frame_height = FRAME_HEIGHT_PLAYER

        try:
            self.frame = pygame.image.load(spritesheet_path).convert_alpha()

        except FileNotFoundError:
            self.frame = pygame.Surface(
                (self.frame_width, self.frame_height)
            ).convert_alpha()
            self.frame.fill((0, 255, 0))

        self.image = pygame.Surface(
            (self.frame_width, self.frame_height)
        ).convert_alpha()

        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(round(axle_x), round(axle_y)))

    def process_event(self, event: pygame.event.Event):
        pass

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_UP]:
            self.direction.y -= 1

        if keys[pygame.K_DOWN]:
            self.direction.y += 1

        if keys[pygame.K_LEFT]:
            self.direction.x -= 1

        if keys[pygame.K_RIGHT]:
            self.direction.x += 1

    def update(self, dt: float):
        self.handle_input()
        super().update(dt)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
