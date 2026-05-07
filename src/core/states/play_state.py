import random
from typing import TYPE_CHECKING

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.event_manager import EventManager
from core.factories.factories_loader import FactoriesLoader
from core.game_world import GameWorld
from core.states.base_state import BaseState
from entities.base_structure import BaseStructure
from entities.enemy import Enemy
from entities.enemy_spawner import EnemySpawner

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
        EventManager.get_instance().subscribe(GameEventEnum.GAME_OVER, self._game_over)
        EventManager.get_instance().subscribe(
            GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned)

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

        for _ in range(50):
            random_x = random.randint(-1000, 2000)
            random_y = random.randint(-1000, 2000)
            
            obs = Obstacle(random_x, random_y)
            self.world.add_object(obs)
        
        
        rota_norte = [
            pygame.math.Vector2(500, -100), 
            pygame.math.Vector2(800, 50),
            pygame.math.Vector2(200, 200),
            pygame.math.Vector2(532, 336)
            ]
        rota_sul   = [
            pygame.math.Vector2(500, 800), 
            
            pygame.math.Vector2(532, 336)
            ]
        rota_leste = [
            pygame.math.Vector2(1100, 300),
            
            pygame.math.Vector2(532, 336)
            ]
        rota_oeste = [
            pygame.math.Vector2(-100, 300), 
            pygame.math.Vector2(-890, 452), 
            pygame.math.Vector2(532, 336)
            ]
        
        spawner_norte = EnemySpawner(500, -100, rota_norte, spawn_interval=10.0)
        spawner_sul = EnemySpawner(500, 800,  rota_sul, spawn_interval=5.0)
        spawner_leste = EnemySpawner(1100, 300, rota_leste, spawn_interval=8.0)
        spawner_oeste = EnemySpawner(-100, 300, rota_oeste, spawn_interval=3.0)

        self.world.add_object(spawner_norte)
        self.world.add_object(spawner_sul)
        self.world.add_object(spawner_leste)
        self.world.add_object(spawner_oeste)
        
        self.initialized = True
    
    def exit(self):
        EventManager.get_instance().unsubscribe(
            GameEventEnum.GAME_OVER, self._game_over)
        EventManager.get_instance().unsubscribe(
            GameEventEnum.ENEMY_SPAWNED, self._on_enemy_spawned)


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

    def _on_enemy_spawned(self, enemy):
        """Callback acionado quando um ninho cria um inimigo."""
        if self.world:
            self.world.add_object(enemy)
    

