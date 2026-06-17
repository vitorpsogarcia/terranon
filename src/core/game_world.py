import pygame
from core.camera_group import CameraGroup
from abc import ABC, abstractmethod
from typing import List, Tuple
from core.enums.game_event_enum import GameEventEnum
from core.event_manager import EventManager
from core.game_object import GameObject, StaticObject, DynamicObject
from entities.enemy import Enemy
from entities.obstacle import Obstacle
from entities.projectiles.projectile import Projectile
from entities.character.player import Player
from entities.enemy_spawner import EnemySpawner



class GameScene(ABC):
    @abstractmethod
    def update(self, dt: float): 
        pass
    
    @abstractmethod
    def handle_events(self, events: List[pygame.event.Event]): 
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface): 
        pass

class GameWorld(GameScene):
    def __init__(self, screen_size: Tuple[int, int]):
        self.all_sprites = CameraGroup()
        self.camera_group = self.all_sprites
        self.screen_size = screen_size
        self.obstacles = pygame.sprite.Group()
        self.dynamic_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.friend_projectiles_group = pygame.sprite.Group()
        self.enemy_projectiles_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.spawners: dict[str, EnemySpawner] = {}


    def set_target(self, target: GameObject):
        self.target = target
        if not hasattr(self.all_sprites, 'set_target'):
            raise AttributeError("CameraGroup deve possuir um método 'set_target'.")
        self.all_sprites.set_target(target)
        self.player_group.add(target._sprite)

    def add_object(self, obj: GameObject):

        layer = 0
        if isinstance(obj, Projectile):
            if obj.friendly:
                self.friend_projectiles_group.add(obj._sprite)
            else:
                self.enemy_projectiles_group.add(obj._sprite)
        
        if isinstance(obj, DynamicObject):
            layer = 2 + int(round(obj.pos.y))
            self.dynamic_group.add(obj._sprite)

            if isinstance(obj, Enemy):
                self.enemies_group.add(obj._sprite)
                
        elif isinstance(obj, EnemySpawner):
            if obj.spawner_id in self.spawners:
                raise ValueError(f"Spawner ID já existe: {obj.spawner_id}")
            
            self.spawners[obj.spawner_id] = obj
            layer = getattr(obj, "render_layer", 0)

        elif isinstance(obj, StaticObject):
            if isinstance(obj, Obstacle):
                layer = 1
                self.obstacles.add(obj._sprite)
            else:
                layer = 0
        else:
            layer = getattr(obj, "render_layer", 0)

        obj.render_layer = layer
        self.all_sprites.add(obj._sprite, layer=layer)

    def remove_object(self, obj: GameObject):
        self.all_sprites.remove(obj._sprite)

    def update(self, dt: float):
        for sprite in self.camera_group.sprites():
            obj = sprite.owner
            if obj.active and hasattr(obj, "update"):
                obj.update(dt)
        
            if not obj.alive():
                continue

        self._resolve_player_obstacle_collisions()
        self._resolve_player_enemy_collisions()

        for sprite in self.camera_group.sprites():
            obj = sprite.owner
            if obj.active and isinstance(obj, DynamicObject):
                new_layer = 2 + int(round(obj.pos.y))
                if new_layer != getattr(obj, "render_layer", None):
                    if hasattr(self.all_sprites, "change_layer"):
                        self.camera_group.change_layer(sprite, new_layer)
                    elif hasattr(self.all_sprites, "change_layer"):
                        self.all_sprites.change_layer(sprite, new_layer)
                    obj.render_layer = new_layer

        hits = pygame.sprite.groupcollide(self.enemies_group, self.friend_projectiles_group, False, True)
        for enemy_sprite, shots in hits.items():
            enemy = enemy_sprite.owner
            for shot_sprite in shots:
                shot = shot_sprite.owner
                enemy.health.take_damage(shot.damage)

        enemy_obstacle_hits = pygame.sprite.groupcollide(self.obstacles, self.enemy_projectiles_group, False, True)
        friend_obstacle_hits = pygame.sprite.groupcollide(self.obstacles, self.friend_projectiles_group, False, True)

        for hits_dict in [enemy_obstacle_hits, friend_obstacle_hits]:
            for obstacle_sprite, shots in hits_dict.items():
                obstacle = obstacle_sprite.owner
                for shot_sprite in shots:
                    shot = shot_sprite.owner
                    if hasattr(obstacle, "health"):
                        obstacle.health.take_damage(shot.damage)

    def handle_events(self, events: List[pygame.event.Event]):
        for obj in self.camera_group.sprites():
            if obj.active:
                for event in events:
                    obj.process_event(event)

    def draw(self, surface: pygame.Surface):
        if hasattr(self.all_sprites, "custom_draw"):
            self.all_sprites.custom_draw(surface)
        else:
            self.all_sprites.draw(surface)

    def _iterate_objects(self):
        for obj in self.all_sprites:
            yield obj

    def _iterate_active_objects(self):
        for obj in self._iterate_objects():
            if obj.active:
                yield obj

    def _resolve_player_obstacle_collisions(self):
        if not hasattr(self, "target") or self.target is None:
            return

        player = self.target
        if not isinstance(player, GameObject):
            return
        
        player_sprite = player._sprite

        def collide_hitbox(p_sprite, o_sprite):
            p_owner = p_sprite.owner
            o_owner = o_sprite.owner
            p_rect = p_owner.feet_hitbox if hasattr(p_owner, "feet_hitbox") else (p_owner.hitbox if hasattr(p_owner, "hitbox") else p_owner.rect)
            o_rect = o_owner.rect
            return p_rect.colliderect(o_rect)

        collisions = pygame.sprite.spritecollide(player_sprite, self.obstacles, False, collided=collide_hitbox)
        if collisions:
            if hasattr(player, "prev_pos"):
                player.pos.x = player.prev_pos.x
                player.pos.y = player.prev_pos.y
                if hasattr(player, "hitbox"):
                    player.hitbox.center = (round(player.pos.x), round(player.pos.y))
                if hasattr(player, "feet_hitbox"):
                    player.feet_hitbox.midbottom = player.hitbox.midbottom

                player_sprite.rect.center = (round(player.pos.x), round(player.pos.y))
                    
    def _resolve_player_enemy_collisions(self):
        if not hasattr(self, "target") or self.target is None:
            return
        player = self.target
        if player.rect is None or not isinstance(player, Player):
            return
        player_sprite = player._sprite

        def collide_hitbox(p_sprite, e_sprite):
            p_owner = p_sprite.owner
            e_owner = e_sprite.owner
            p_rect = p_owner.hitbox if hasattr(p_owner, "hitbox") else p_owner.rect
            e_rect = e_owner.hitbox if hasattr(e_owner, "hitbox") else e_owner.rect
            return p_rect.colliderect(e_rect)

        touching_enemies = pygame.sprite.spritecollide(player_sprite, self.enemies_group, False, collided=collide_hitbox)
        for enemy_sprite in touching_enemies:
            if isinstance(player, Player):
                player.health.take_damage(10.0)
                try:
                    EventManager.get_instance().emit(GameEventEnum.PLAY_SFX, filename="effects/damage.mp3")
                except Exception as e:
                    print(f"Erro ao reproduzir som de hit: {e}")
            
                if hasattr(player, "prev_pos"):
                    player.pos.x = player.prev_pos.x
                    player.pos.y = player.prev_pos.y
                    if hasattr(player, "hitbox"):
                        player.hitbox.center = (round(player.pos.x), round(player.pos.y))
                    if hasattr(player, "feet_hitbox"):
                        player.feet_hitbox.midbottom = player.hitbox.midbottom
                    player_sprite.rect.center = (round(player.pos.x), round(player.pos.y))