import pygame

from core.camera_group import CameraGroup
from core.factories.enemy_factory import EnemyFactory
from core.game_object import DynamicObject, GameObject
from core.manager.spatial_manager import SpatialManager
from core.states.base_state import GameScene


class GameWorld(GameScene):
    def __init__(self, screen_size: tuple[int, int]):
        super().__init__(None, screen_size)
        self.camera_group = CameraGroup()
        self.screen_size = screen_size
        self.spatial_manager = SpatialManager()
        from core.factories.projectile_factory import ProjectileFactory

        self.projectile_factory = ProjectileFactory(self)

        EnemyFactory.preload_all_enemies()

    def destroy(self):
        self.projectile_factory.destroy()

    def enter(self):
        pass

    def exit(self):
        pass

    def set_target(self, target: GameObject):
        self.target = target
        self.camera_group.target = target

    def add_object(self, obj: GameObject):
        layer = getattr(obj, "render_layer", 0)

        self.spatial_manager.add_obj_to_group(obj)

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
            if obj.active and hasattr(sprite, "update"):
                sprite.update(dt)

            if obj.active and obj.rect is not None and isinstance(obj, DynamicObject):
                new_layer = round(obj.rect.bottom)
                if new_layer != obj.render_layer:
                    self.camera_group.change_layer(sprite, new_layer)
                    obj.render_layer = new_layer

            if not obj.alive():
                continue

        self.spatial_manager.update_collisions()
        self.spatial_manager.update_target_collisions(self.target)

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
