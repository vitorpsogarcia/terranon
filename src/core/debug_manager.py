from typing import ClassVar

import pygame

from core.enums.debug_option_enum import DebugOption
from core.settings.colors import Colors


class DebugManager:
    _debug_flags: ClassVar[dict[DebugOption, bool]] = {
        option: False for option in DebugOption
    }

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._debug_flags = {option: False for option in DebugOption}
        return cls._instance

    @staticmethod
    def is_option_enabled(option: DebugOption) -> bool:
        return DebugManager._debug_flags.get(option, False)

    @staticmethod
    def toggle_option(option: DebugOption):
        DebugManager._debug_flags[option] = not DebugManager._debug_flags[option]

    @staticmethod
    def draw_world_debug(surface: pygame.Surface, camera_group):
        if not (
            DebugManager.is_option_enabled(DebugOption.COLLIDERS)
            or DebugManager.is_option_enabled(DebugOption.CREATURE_DIRECTIONS)
        ):
            return
        for sprite in camera_group.sprites():
            if DebugManager.is_option_enabled(DebugOption.COLLIDERS):
                owner = getattr(sprite, "owner", None)
                # Renderiza o colisor (hitbox) em amarelo para visualização/debug
                if hasattr(sprite, "hitbox"):
                    hitboxes_rect = sprite.hitbox.copy()
                    hitboxes_rect.topleft -= camera_group.offset
                    pygame.draw.rect(surface, Colors.debug.hitbox, hitboxes_rect, 1)

                if hasattr(owner, "hitboxes"):
                    hitboxes_rect = sprite.owner.hitboxes.copy()
                    for hitbox in hitboxes_rect:
                        hitbox.topleft -= camera_group.offset
                        pygame.draw.rect(surface, Colors.debug.hitbox, hitbox, 1)

                # Renderiza o colisor de pés (feet_hitbox) em azul claro para visualização/debug
                if hasattr(sprite, "feet_hitbox"):
                    feet_rect = sprite.feet_hitbox.copy()
                    feet_rect.topleft -= camera_group.offset
                    pygame.draw.rect(surface, Colors.debug.feet_hitbox, feet_rect, 1)

            if DebugManager.is_option_enabled(DebugOption.CREATURE_DIRECTIONS):
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

    @staticmethod
    def draw_ui_debug(surface: pygame.Surface, state, clock, font):
        from core.states.play_state import PlayState

        if (
            DebugManager.is_option_enabled(DebugOption.PLAYER_STATUS)
            and isinstance(state, PlayState)
            and state.world is not None
        ):
            camera_group = state.world.camera_group
            player = camera_group.target

            if player:
                txt_pos = font.render(
                    f"Pos Real do Player: X: {player.pos.x:.0f}, Y: {player.pos.y:.0f}",
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
