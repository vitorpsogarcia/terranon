import pygame

from core.enums.collider_tag_enum import ColliderTagEnum
from core.enums.debug_option_enum import DebugOption
from core.game_object import GameObject
from core.manager.economy_manager import EconomyManager
from core.settings.colors import Colors
from core.singleton_meta import SingletonMeta


class DebugManager(metaclass=SingletonMeta):
    def __init__(self):
        self._debug_flags: dict[DebugOption, bool] = {
            option: False for option in DebugOption
        }

    def is_option_enabled(self, option: DebugOption) -> bool:
        return self._debug_flags.get(option, False)

    def toggle_option(self, option: DebugOption):
        self._debug_flags[option] = not self._debug_flags[option]

    def draw_world_debug(self, surface: pygame.Surface, camera_group):
        if not (
            self.is_option_enabled(DebugOption.COLLIDERS)
            or self.is_option_enabled(DebugOption.CREATURE_DIRECTIONS)
        ):
            return
        for sprite in camera_group.sprites():
            if self.is_option_enabled(DebugOption.COLLIDERS):
                owner = getattr(sprite, "owner", None)
                if not isinstance(owner, GameObject):
                    continue

                if owner.collider is not None:
                    for rect, tag in owner.collider.get_world_rects():
                        hitbox_rect = rect.copy()
                        hitbox_rect.topleft -= camera_group.offset
                        color = (
                            Colors.debug.feet_hitbox
                            if tag == ColliderTagEnum.FEET
                            else Colors.debug.hitbox
                        )
                        pygame.draw.rect(surface, color, hitbox_rect, 1)
                elif hasattr(owner, "hitbox") and owner.hitbox:
                    hitbox_rect = owner.hitbox.copy()
                    hitbox_rect.topleft -= camera_group.offset
                    pygame.draw.rect(surface, Colors.debug.hitbox, hitbox_rect, 1)

            if self.is_option_enabled(DebugOption.CREATURE_DIRECTIONS):
                owner = getattr(sprite, "owner", None)
                if owner is not None and hasattr(owner, "direction"):
                    direction_vector = owner.direction
                    start_pos = sprite.rect.center - camera_group.offset
                    end_pos = start_pos + direction_vector * 25
                    pygame.draw.line(
                        surface, Colors.debug.direction_vector, start_pos, end_pos, 2
                    )
                    arrow_size = 10
                    angle = direction_vector.angle_to(pygame.math.Vector2(1, 0))
                    left_wing = end_pos + pygame.math.Vector2(
                        -arrow_size, arrow_size / 2
                    ).rotate(-angle)
                    right_wing = end_pos + pygame.math.Vector2(
                        -arrow_size, -arrow_size / 2
                    ).rotate(-angle)
                    pygame.draw.polygon(
                        surface,
                        Colors.debug.direction_vector,
                        [end_pos, left_wing, right_wing],
                    )

            if self.is_option_enabled(DebugOption.TARGETING_LINES):
                owner = getattr(sprite, "owner", None)
                if isinstance(owner, GameObject) and owner._is_turret_target:
                    target = owner
                    turret = owner._turret
                    if turret is not None:
                        start_pos = (
                            turret.render_component.center() - camera_group.offset
                        )
                        end_pos = target.transform.pos - camera_group.offset
                        pygame.draw.line(
                            surface, Colors.debug.targeting_line, start_pos, end_pos, 1
                        )

    def draw_ui_debug(self, surface: pygame.Surface, state, clock, font):
        from core.states.play_state import PlayState

        if (
            self.is_option_enabled(DebugOption.PLAYER_STATUS)
            and isinstance(state, PlayState)
            and state.world is not None
        ):
            camera_group = state.world.camera_group
            player = camera_group.target
            points = EconomyManager().current_points, EconomyManager().total_points

            if player:
                txt_pos = font.render(
                    f"Pos Real do Player: X: {player.transform.pos.x:.0f}, Y: {player.transform.pos.y:.0f}",
                    True,
                    Colors.text.primary,
                )
                surface.blit(txt_pos, (10, 10))

                offset = camera_group.offset
                txt_cam = font.render(
                    f"Offset da Câmera: X: {offset.x:.0f}, Y: {offset.y:.0f}",
                    True,
                    Colors.text.primary,
                )
                surface.blit(txt_cam, (10, 35))

                txt_fps = font.render(f"FPS: {clock.get_fps():.0f}", True, (0, 255, 0))
                surface.blit(txt_fps, (10, 60))

                txt_life = font.render(
                    f"Vida: {player.health.current_hp:.0f}/{player.health.max_hp:.0f}",
                    True,
                    Colors.text.primary,
                )
                surface.blit(txt_life, (10, 85))

            txt_points = font.render(
                f"Pontos: {points[0]}/{points[1]}", True, Colors.text.primary
            )
            surface.blit(txt_points, (10, 110))
