import logging
from typing import TYPE_CHECKING

import pygame

from core.enums.collider_tag_enum import ColliderTagEnum
from core.enums.game_event_enum import GameEventEnum
from core.manager.event_manager import EventManager
from core.singleton_meta import SingletonMeta
from entities.character.player import Player
from entities.enemy import Enemy
from entities.enemy_spawner import EnemySpawner
from entities.nature.world_collider import WorldCollider
from entities.obstacle import Obstacle
from entities.projectiles.projectile import Projectile
from entities.structures.main_base import MainBase

if TYPE_CHECKING:
    from core.game_object import GameObject


class SpatialManager(metaclass=SingletonMeta):
    _logger = logging.getLogger("SpatialManager")

    def __init__(self):
        self.obstacles = pygame.sprite.Group()
        self.dynamic_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.friend_projectiles_group = pygame.sprite.Group()
        self.enemy_projectiles_group = pygame.sprite.Group()
        self.structures_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()

        self.spawners: dict[str, EnemySpawner] = {}
        self.world_colliders: list[WorldCollider] = []

        EventManager().subscribe(GameEventEnum.GAME_OVER, self.reset)

    def add_obj_to_group(self, obj: "GameObject"):
        from entities.structures.towers.generic_tower import GenericTower

        if isinstance(obj, Projectile):
            if obj.friendly:
                self.friend_projectiles_group.add(obj._sprite)
            else:
                self.enemy_projectiles_group.add(obj._sprite)

        elif hasattr(obj, "rigidbody"):
            self.dynamic_group.add(obj._sprite)
            if isinstance(obj, Enemy):
                self.enemies_group.add(obj._sprite)

        elif isinstance(obj, EnemySpawner):
            if obj.spawner_id in self.spawners:
                self._logger.error(f"Spawner ID já existe: {obj.spawner_id}")
            self.spawners[obj.spawner_id] = obj

        elif isinstance(obj, Obstacle):
            self.obstacles.add(obj._sprite)

        if isinstance(obj, (MainBase, GenericTower)):
            self.structures_group.add(obj._sprite)

    def rem_obj_from_group(self, obj: "GameObject"):
        if isinstance(obj, Projectile):
            if obj.friendly:
                self.friend_projectiles_group.remove(obj._sprite)
            else:
                self.enemy_projectiles_group.remove(obj._sprite)

        elif hasattr(obj, "rigidbody"):
            self.dynamic_group.remove(obj._sprite)
            if isinstance(obj, Enemy):
                self.enemies_group.remove(obj._sprite)

        elif isinstance(obj, EnemySpawner):
            if obj.spawner_id not in self.spawners:
                self._logger.error(f"Spawner ID não encontrado: {obj.spawner_id}")
            else:
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

    def update_target_collisions(self, target: "GameObject"):
        self._resolve_player_world_collisions(target)
        self._resolve_player_obstacle_collisions(target)
        self._resolve_player_enemy_collisions(target)

    def _resolve_player_world_collisions(self, target: "GameObject"):
        if not isinstance(target, Player) or not target.collider:
            return

        for collider_obj in self.world_colliders:
            if collider_obj.collider:
                if target.collider.collides_with(
                    collider_obj.collider,
                    my_tag=ColliderTagEnum.FEET,
                    other_tag=ColliderTagEnum.SOLID,
                ):
                    if hasattr(target, "rigidbody"):
                        target.transform.pos.x = target.rigidbody.prev_pos.x
                        target.transform.pos.y = target.rigidbody.prev_pos.y
                    else:
                        target.transform.pos.x = target.prev_pos.x
                        target.transform.pos.y = target.prev_pos.y
                    if hasattr(target, "sync_colliders"):
                        target.sync_colliders()
                    break

    def _resolve_player_obstacle_collisions(self, target: "GameObject"):
        if not isinstance(target, Player) or not target.collider:
            return

        for obstacle_sprite in self.obstacles:
            obstacle = getattr(obstacle_sprite, "owner", None)
            if obstacle and obstacle.collider:
                if target.collider.collides_with(
                    obstacle.collider,
                    my_tag=ColliderTagEnum.FEET,
                    other_tag=ColliderTagEnum.SOLID,
                ):
                    if hasattr(target, "rigidbody"):
                        target.transform.pos.x = target.rigidbody.prev_pos.x
                        target.transform.pos.y = target.rigidbody.prev_pos.y
                    else:
                        target.transform.pos.x = target.prev_pos.x
                        target.transform.pos.y = target.prev_pos.y
                    if hasattr(target, "sync_colliders"):
                        target.sync_colliders()
                    break

    def _resolve_player_enemy_collisions(self, target: "GameObject"):
        if not isinstance(target, Player) or not target.collider:
            return

        for enemy_sprite in self.enemies_group:
            enemy = getattr(enemy_sprite, "owner", None)
            if enemy and enemy.collider:
                if target.collider.collides_with(
                    enemy.collider,
                    my_tag=ColliderTagEnum.BODY,
                    other_tag=ColliderTagEnum.BODY,
                ):
                    target.health.take_damage(10.0)
                    target.apply_knockback(enemy.transform.pos, force=1500.0)

                    try:
                        EventManager().emit(
                            GameEventEnum.PLAY_SFX, filename="effects/damage.mp3"
                        )
                    except Exception as e:
                        self._logger.error(f"Erro ao reproduzir som de hit: {e}")

    def _resolve_collisions(
        self,
        group1: pygame.sprite.Group,
        group2: pygame.sprite.Group,
    ):
        def collide_components(sprite1, sprite2):
            obj1 = getattr(sprite1, "owner", None)
            obj2 = getattr(sprite2, "owner", None)
            if obj1 and obj2 and obj1.collider and obj2.collider:
                return obj1.collider.collides_with(obj2.collider)
            r1 = getattr(obj1, "rect", getattr(sprite1, "rect", None))
            r2 = getattr(obj2, "rect", getattr(sprite2, "rect", None))
            return r1.colliderect(r2) if r1 and r2 else False

        hits = pygame.sprite.groupcollide(
            group1, group2, False, False, collided=collide_components
        )

        for sprite1, sprites2 in hits.items():
            obj1 = sprite1.owner
            for sprite2 in sprites2:
                obj2 = sprite2.owner
                if hasattr(obj1, "on_collision"):
                    obj1.on_collision(obj2)
                if hasattr(obj2, "on_collision"):
                    obj2.on_collision(obj1)

    def get_nearest_enemy(self, position: pygame.Vector2, range: float) -> Enemy | None:
        nearest_enemy = None
        nearest_distance = float("inf")

        for enemy_sprite in self.enemies_group:
            enemy = enemy_sprite.owner
            if not isinstance(enemy, Enemy):
                continue

            distance = (enemy.transform.pos - position).length()
            if distance <= range and distance < nearest_distance:
                nearest_enemy = enemy
                nearest_distance = distance

        return nearest_enemy

    def reset(self):
        self.obstacles.empty()
        self.dynamic_group.empty()
        self.player_group.empty()
        self.friend_projectiles_group.empty()
        self.enemy_projectiles_group.empty()
        self.structures_group.empty()
        self.enemies_group.empty()
        self.spawners.clear()
        self.world_colliders.clear()
