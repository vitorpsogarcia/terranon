import random
from typing import TYPE_CHECKING

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.event_manager import EventManager
from core.factories.factories_loader import FactoriesLoader
from core.game_world import GameWorld
from core.sound_manager import SoundManager
from core.states.base_state import BaseState
from entities.base_structure import BaseStructure
from entities.enemy import Enemy

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
        try:
            SoundManager.play_background_music("Crashsite-Defense.wav", volume=0.7)
        except Exception as e:
            print(f"{e}")
        
        EventManager.get_instance().subscribe(GameEventEnum.GAME_OVER, self._game_over)

        self.world = GameWorld(self.screen_size)

        FactoriesLoader(self.world)
        
        player = Player(0, 0)
        w_player, h_player = player.frame_width, player.frame_height
        
        player.pos = pygame.math.Vector2(self.screen_size[0] // 2 - w_player // 2, self.screen_size[1] // 2 - h_player // 2)
        if player.rect is not None:
            player.rect.topleft = player.pos
        
        self.world.add_object(player)
        self.world.set_target(player)
        
        self.base = BaseStructure(500, 300)
        self.world.add_object(self.base)

        inimigo1 = Enemy(100, -200, target=self.base)
        inimigo2 = Enemy(900, 800, target=self.base)
        inimigo3 = Enemy(-300, 500, target=self.base)

        self.world.add_object(inimigo1)
        self.world.add_object(inimigo2)
        self.world.add_object(inimigo3)

        for _ in range(50):
            random_x = random.randint(-1000, 2000)
            random_y = random.randint(-1000, 2000)
            
            obs = Obstacle(random_x, random_y)
            self.world.add_object(obs)
        
        self.initialized = True
    

    def exit(self):
        self.initialized = False
        SoundManager.stop_background_music()
        EventManager.get_instance().unsubscribe(GameEventEnum.GAME_OVER, self._game_over)


    def update(self, delta_time):
        if self.world is not None:
            self.world.update(delta_time)
    

    def _change_state(self, new_state: GameStateEnum):
        self.state_manager.change_to(new_state)
    
    def _game_over(self):
        self.initialized = False
        self._change_state(GameStateEnum.GAME_OVER)


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
    

