from abc import ABC, abstractmethod

import pygame

from core.camera_group import CameraGroup
from core.enums.game_event_enum import GameEventEnum
from core.game_object import DynamicObject, GameObject
from core.manager.event_manager import EventManager
from entities.character.player import Player
from entities.enemy import Enemy
from entities.enemy_spawner import EnemySpawner
from entities.obstacle import Obstacle
from entities.projectiles.projectile import Projectile
from entities.structures.main_base import MainBase
from entities.structures.towers.generic_tower import GenericTower


class GameScene(ABC):
    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass


class GameWorld(GameScene):
    def __init__(self, screen_size: tuple[int, int]):
        self.camera_group = CameraGroup()
        self.screen_size = screen_size
        self.obstacles = pygame.sprite.Group()
        self.dynamic_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.friend_projectiles_group = pygame.sprite.Group()
        self.enemy_projectiles_group = pygame.sprite.Group()
        self.structures_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.spawners: dict[str, EnemySpawner] = {}
        self.world_colliders: list[pygame.Rect] = []

    def set_target(self, target: GameObject):
        self.target = target
        self.camera_group.target = target
        self.player_group.add(target._sprite)

    def add_object(self, obj: GameObject):
        layer = getattr(obj, "render_layer", 0)

        self._add_obj_to_group(obj)

        if isinstance(obj, DynamicObject) and obj.rect is not None:
            layer = round(obj.rect.bottom)

        if not obj._fixed_layer and obj.rect is not None:
            layer = round(obj.rect.bottom)

        obj.render_layer = layer
        self.camera_group.add(obj._sprite, layer=layer)

    def remove_object(self, obj: GameObject):
        self.camera_group.remove(obj._sprite)

    def update(self, dt: float):
        for sprite in self.camera_group.sprites():
            obj = sprite.owner
            if obj.active and hasattr(obj, "update"):
                obj.update(dt)

            if obj.active and obj.rect is not None and isinstance(obj, DynamicObject):
                new_layer = round(obj.rect.bottom)
                if new_layer != obj.render_layer:
                    self.camera_group.change_layer(sprite, new_layer)
                    obj.render_layer = new_layer

            if not obj.alive():
                continue

        self._resolve_player_world_collisions()
        self._resolve_player_obstacle_collisions()
        self._resolve_player_enemy_collisions()
        self._resolve_collisions(self.enemies_group, self.friend_projectiles_group)
        self._resolve_collisions(self.enemies_group, self.structures_group)
        self._resolve_collisions(self.friend_projectiles_group, self.structures_group)

    def handle_events(self, events: list[pygame.event.Event]):
        for obj in self.camera_group.sprites():
            if obj.active:
                for event in events:
                    obj.process_event(event)

    def draw(self, surface: pygame.Surface):
        if hasattr(self.camera_group, "custom_draw"):
            self.camera_group.custom_draw(surface)
        else:
            self.camera_group.draw(surface)

    def _iterate_objects(self):
        yield from self.camera_group

    def _iterate_active_objects(self):
        for obj in self._iterate_objects():
            if obj.active:
                yield obj

    def _resolve_player_world_collisions(self):
        if not hasattr(self, "target") or self.target is None:
            return

        player = self.target

        if not isinstance(player, Player):
            return

        for collider in self.world_colliders:
            if player.feet_hitbox.colliderect(collider):
                player.pos.x = player.prev_pos.x
                player.pos.y = player.prev_pos.y
                player.sync_colliders()
                if player.rect is not None:
                    player._sprite.rect = player.rect.copy()
                break

    def _resolve_player_obstacle_collisions(self):
        if not hasattr(self, "target") or self.target is None:
            return

        player = self.target

        if not isinstance(player, Player):
            return

        player_sprite = player._sprite

        pottential_collisions = pygame.sprite.spritecollide(
            player_sprite, self.obstacles, False
        )
        if not pottential_collisions:
            return

        actual_collision = False

        for obstacle_sprites in pottential_collisions:
            obstacle = obstacle_sprites.owner

            obstacle_hitboxes = getattr(obstacle, "hitboxes", [obstacle.rect])
            for hitbox in obstacle_hitboxes:
                if player.feet_hitbox.colliderect(hitbox):
                    actual_collision = True
                    break

            if actual_collision:
                break

        if actual_collision:
            player.pos.x = player.prev_pos.x
            player.pos.y = player.prev_pos.y
            player.sync_colliders()
            if player.rect is not None:
                player._sprite.rect = player.rect.copy()

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

        touching_enemies = pygame.sprite.spritecollide(
            player_sprite, self.enemies_group, False, collided=collide_hitbox
        )

        for enemy_sprite in touching_enemies:
            enemy = enemy_sprite.owner

            player.health.take_damage(10.0)
            player.apply_knockback(enemy.pos, force=1500.0)

            try:
                EventManager().emit(
                    GameEventEnum.PLAY_SFX, filename="effects/damage.mp3"
                )
            except Exception as e:
                print(f"Erro ao reproduzir som de hit: {e}")

    def _resolve_collisions(
        self,
        group1: pygame.sprite.Group,
        group2: pygame.sprite.Group,
    ):
        hits = pygame.sprite.groupcollide(group1, group2, False, False)

        for sprite1, sprites2 in hits.items():
            obj1 = sprite1.owner
            for sprite2 in sprites2:
                obj2 = sprite2.owner
                if hasattr(obj1, "on_collision"):
                    obj1.on_collision(obj2)
                if hasattr(obj2, "on_collision"):
                    obj2.on_collision(obj1)

    def _add_obj_to_group(self, obj: GameObject):
        if isinstance(obj, Projectile):
            if obj.friendly:
                self.friend_projectiles_group.add(obj._sprite)
            else:
                self.enemy_projectiles_group.add(obj._sprite)

        elif isinstance(obj, DynamicObject):
            self.dynamic_group.add(obj._sprite)
            if isinstance(obj, Enemy):
                self.enemies_group.add(obj._sprite)

        elif isinstance(obj, EnemySpawner):
            if obj.spawner_id in self.spawners:
                raise ValueError(f"Spawner ID já existe: {obj.spawner_id}")
            self.spawners[obj.spawner_id] = obj

        elif isinstance(obj, Obstacle):
            self.obstacles.add(obj._sprite)

        if isinstance(obj, (MainBase, GenericTower)):
            self.structures_group.add(obj._sprite)
