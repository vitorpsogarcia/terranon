import pygame

from core.components.health_component import HealthComponent
from core.components.static_render_component import StaticRenderComponent
from core.enums.game_event_enum import GameEventEnum
from core.game_object import GameObject
from core.manager.asset_manager import AssetManager
from core.manager.event_manager import EventManager
from core.settings.settings import MAIN_BASE_HEALTH, MAIN_BASE_SIZE
from entities.enemy import Enemy
from entities.obstacle import Obstacle


class MainBase(Obstacle):
    def __init__(self, position: pygame.Vector2, *groups: pygame.sprite.Group):

        # Ajusta a posição para o centro da base
        position.x = round(position.x - MAIN_BASE_SIZE / 2)
        position.y = round(position.y - MAIN_BASE_SIZE / 2)
        super().__init__(position, *groups)

        self.image = AssetManager().load_image(
            name="main_base",
            path="Nave-D.png",
            size=(MAIN_BASE_SIZE, MAIN_BASE_SIZE),
        )
        
        self.render_component = StaticRenderComponent(self, self.image)

        self.hitbox = pygame.Rect(
            self.pos.x, self.pos.y, MAIN_BASE_SIZE, MAIN_BASE_SIZE
        )
        self.rect = self.hitbox
        self.relative_hitboxes = [pygame.Rect(0, 0, MAIN_BASE_SIZE, MAIN_BASE_SIZE)]

        self.health = HealthComponent(max_hp=MAIN_BASE_HEALTH, on_death_callback=self.on_death)

    def update(self, dt: float):
        self.health.update(dt)
        super().update(dt)

    def on_death(self):
        self.active = False
        self.kill()
        print("A BASE CAIU! GAME OVER!")
        EventManager().emit(GameEventEnum.GAME_OVER)

    def on_collision(self, other: GameObject):
        if isinstance(other, Enemy):
            self.health.take_damage(other.health.current_hp)
            other.health.die()
