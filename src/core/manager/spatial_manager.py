from typing import ClassVar

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.game_object import DynamicObject, GameObject
from core.manager.event_manager import EventManager
from core.singleton_meta import SingletonMeta
from entities.character.player import Player
from entities.enemy import Enemy
from entities.enemy_spawner import EnemySpawner
from entities.obstacle import Obstacle
from entities.projectiles.projectile import Projectile
from entities.structures.main_base import MainBase
from entities.structures.towers.generic_tower import GenericTower


class SpatialManager(metaclass=SingletonMeta):
    obstacles = pygame.sprite.Group()
    dynamic_group = pygame.sprite.Group()
    player_group = pygame.sprite.GroupSingle()
    friend_projectiles_group = pygame.sprite.Group()
    enemy_projectiles_group = pygame.sprite.Group()
    structures_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()

    spawners: ClassVar[dict[str, EnemySpawner]] = {}
    world_colliders: ClassVar[list[pygame.Rect]] = []

    def add_obj_to_group(self, obj: GameObject):
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

    def rem_obj_from_group(self, obj: GameObject):
        if isinstance(obj, Projectile):
            if obj.friendly:
                self.friend_projectiles_group.remove(obj._sprite)
            else:
                self.enemy_projectiles_group.remove(obj._sprite)

        elif isinstance(obj, DynamicObject):
            self.dynamic_group.remove(obj._sprite)
            if isinstance(obj, Enemy):
                self.enemies_group.remove(obj._sprite)

        elif isinstance(obj, EnemySpawner):
            if obj.spawner_id in self.spawners:
                raise ValueError(f"Spawner ID já existe: {obj.spawner_id}")
            self.spawners[obj.spawner_id] = obj
            del self.spawners[obj.spawner_id]

        elif isinstance(obj, Obstacle):
            self.obstacles.remove(obj._sprite)

        if isinstance(obj, (MainBase, GenericTower)):
            self.structures_group.remove(obj._sprite)

    def update_collisions(self):
        self._resolve_collisions(self.enemies_group, self.friend_projectiles_group)
        self._resolve_collisions(self.enemies_group, self.structures_group)
        self._resolve_collisions(self.friend_projectiles_group, self.structures_group)

    def update_target_collisions(self, target: GameObject):
        self._resolve_player_world_collisions(target)
        self._resolve_player_obstacle_collisions(target)
        self._resolve_player_enemy_collisions(target)

    def _resolve_player_world_collisions(self, target: GameObject):
        if not isinstance(target, Player):
            return

        for collider in self.world_colliders:
            if target.feet_hitbox.colliderect(collider):
                target.pos.x = target.prev_pos.x
                target.pos.y = target.prev_pos.y
                target.sync_colliders()
                if target.rect is not None:
                    target._sprite.rect = target.rect.copy()
                break

    def _resolve_player_obstacle_collisions(self, target):
        if not isinstance(target, Player):
            return

        player = target

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

    def _resolve_player_enemy_collisions(self, target):
        if not isinstance(target, Player):
            return
        player = target
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
