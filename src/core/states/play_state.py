import random
from typing import TYPE_CHECKING

import pygame

from core.enums.game_state_enum import GameStateEnum
from core.game_world import GameWorld
from core.states.base_state import BaseState

if TYPE_CHECKING:
    from core.state_manager import StateManager
from entities.character.player import Player
from entities.obstacle import Obstacle


class PlayState(BaseState):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.world: GameWorld | None = None
        self.initialized = False
        self.screen_size = screen_size
    

    def enter(self):
        if (self.initialized):
            return

        self.world = GameWorld()
        
        player = Player(0, 0)
        w_player, h_player = player.frame_width, player.frame_height
        
        player.pos = pygame.math.Vector2(self.screen_size[0] // 2 - w_player // 2, self.screen_size[1] // 2 - h_player // 2)
        player.rect.topleft = player.pos
        
        self.world.add_object(player)
        self.world.set_target(player)

        for _ in range(50):
            random_x = random.randint(-1000, 2000)
            random_y = random.randint(-1000, 2000)
            
            obs = Obstacle(random_x, random_y)
            self.world.add_object(obs)
        
        self.initialized = True
    

    def exit(self):
        # self.world = None
        pass


    def update(self, delta_time):
        if self.world is not None:
            self.world.update(delta_time)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.state_manager.change_to(GameStateEnum.INVENTORY)
                elif event.key == pygame.K_k:
                    self.state_manager.change_to(GameStateEnum.GAME_OVER)
                elif event.key == pygame.K_ESCAPE:
                    self.state_manager.change_to(GameStateEnum.MENU)

        if self.world is not None:
            self.world.handle_events(events)


    def draw(self, surface):
        if self.world is not None:
            self.world.draw(surface)