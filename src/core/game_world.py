import pygame
from core.camera_group import CameraGroup
from abc import ABC, abstractmethod
from typing import List, Tuple
from core.game_object import GameObject, StaticObject, DynamicObject
from entities.obstacle import Obstacle

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
        self.shots_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()


    def set_target(self, target: GameObject):
        self.target = target
        if not hasattr(self.all_sprites, 'set_target'):
            raise AttributeError("CameraGroup deve possuir um método 'set_target'.")
        self.all_sprites.set_target(target)

    def add_object(self, obj: GameObject):

        if isinstance(obj, DynamicObject):
            layer = 2 + int(round(obj.pos.y))
            self.dynamic_group.add(obj)
        elif isinstance(obj, StaticObject):
            if isinstance(obj, Obstacle):
                layer = 1
                self.obstacles.add(obj)
            else:
                layer = 0
        else:
            layer = getattr(obj, "render_layer", 0)

        obj.render_layer = layer
        self.all_sprites.add(obj, layer=layer)

    def remove_object(self, obj: GameObject):
        self.all_sprites.remove(obj)

    def update(self, dt: float):
        for obj in self.camera_group.sprites():
            if obj.active:
                obj.update(dt)
        
        self._resolve_player_obstacle_collisions()

        for obj in self.camera_group.sprites():
            if obj.active and isinstance(obj, DynamicObject):
                new_layer = 2 + int(round(obj.pos.y))
                if new_layer != getattr(obj, "render_layer", None):
                    if hasattr(self.all_sprites, "change_layer"):
                        self.all_sprites.change_layer(obj, new_layer)
                    obj.render_layer = new_layer

        hits = pygame.sprite.groupcollide(self.enemies_group, self.shots_group, False, True)
        if hits:
            for enemy, shots in hits.items():
                for shot in shots:
                    enemy.health.take_damage(shot.damage)
                if enemy.health.current_health <= 0:
                    enemy.kill()

        obstacle_hits = pygame.sprite.groupcollide(self.obstacles, self.shots_group, False, True)

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

        collisions = pygame.sprite.spritecollide(player, self.obstacles, False)
        for obstacle in collisions:
            if player.rect.colliderect(obstacle.rect):
                if player.prev_rect is not None:
                    player.rect.topleft = player.prev_rect.topleft
                    player.pos.x = player.rect.x
                    player.pos.y = player.rect.y
