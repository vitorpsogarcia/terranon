import pygame
import random
from core.settings import COLORS_GAME, FPS, SCREEN_WIDTH, SCREEN_HEIGHT 
from core.game_world import GameScene, GameWorld
from entities.character.player import Player
from entities.obstacle import Obstacle


class GameManager:
    def __init__(self, tela: pygame.Surface):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self._running = True

        self.active_scene: GameScene | None = None

        self._init_game()

    def _init_game(self):
        world = GameWorld(SCREEN_WIDTH, SCREEN_HEIGHT)
        screen_width, screen_height = self.tela.get_size()
        player = Player(0, 0)
        w_player, h_player = player.frame_width, player.frame_height
        player.pos = pygame.math.Vector2(screen_width // 2 - w_player // 2, screen_height // 2 - h_player // 2)
        player.rect.topleft = player.pos
        world.add_object(player)
        world.set_target(player)
        
        for _ in range(50):
            random_x = random.randint(-1000, 2000)
            random_y = random.randint(-1000, 2000)
            
            obs = Obstacle(random_x, random_y)
            world.add_object(obs)
            
        self.active_scene = world

    def on_execute(self):
        dt = self.clock.tick(FPS) / 1000.0

        while self._running:
            self.on_events()
            dt = max(0.001, min(0.05, dt))
            self.update(dt)
            self.on_render()
            dt = self.clock.tick(FPS) / 1000.0

        self.on_cleanup()

    def on_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._running = False

        if self.active_scene:
            self.active_scene.handle_events(events)

    def update(self, dt: float):
        if self.active_scene:
            self.active_scene.update(dt)

    def on_render(self):
        self.tela.fill(COLORS_GAME.get("BLACK", (0, 0, 0)))

        if self.active_scene:
            self.active_scene.draw(self.tela)

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
