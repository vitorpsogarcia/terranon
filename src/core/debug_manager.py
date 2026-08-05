from core.enums.debug_option_enum import DebugOption
import pygame

class DebugManager:
    _debug_flags = {option: False for option in DebugOption}

    @staticmethod
    def is_option_enabled(option: DebugOption) -> bool:
        return DebugManager._debug_flags.get(option, False)

    @staticmethod
    def toggle_option(option: DebugOption):
        DebugManager._debug_flags[option] = not DebugManager._debug_flags[option]

    @staticmethod
    def draw_world_debug(surface: pygame.Surface, camera_group):
        if DebugManager.is_option_enabled(DebugOption.COLLIDERS):
            for sprite in camera_group.sprites():
                owner = getattr(sprite, 'owner', None)
                # Renderiza o colisor (hitbox) em amarelo para visualização/debug
                if hasattr(sprite, 'hitbox'):
                    hitboxes_rect = sprite.hitbox.copy()
                    hitboxes_rect.topleft -= camera_group.offset
                    pygame.draw.rect(surface, (255, 255, 0), hitboxes_rect, 1)

                if hasattr(owner, 'hitboxes'):
                    hitboxes_rect = sprite.owner.hitboxes.copy()
                    for hitbox in hitboxes_rect:
                        hitbox.topleft -= camera_group.offset
                        pygame.draw.rect(surface, (255, 255, 0), hitbox, 1)

                # Renderiza o colisor de pés (feet_hitbox) em azul claro para visualização/debug
                if hasattr(sprite, 'feet_hitbox'):
                    feet_rect = sprite.feet_hitbox.copy()
                    feet_rect.topleft -= camera_group.offset
                    pygame.draw.rect(surface, (0, 255, 255), feet_rect, 1)

    @staticmethod
    def draw_ui_debug(surface: pygame.Surface, state, clock, font):
        from core.states.play_state import PlayState
        if DebugManager.is_option_enabled(DebugOption.PLAYER_STATUS):
            if isinstance(state, PlayState) and state.world is not None:
                camera_group = state.world.camera_group
                player = camera_group.target

                if player:
                    txt_pos = font.render(
                        f"Pos Real do Player: X: {player.pos.x:.0f}, Y: {player.pos.y:.0f}", True, (255, 255, 0))
                    surface.blit(txt_pos, (10, 10))

                    offset = camera_group.offset
                    txt_cam = font.render(
                        f"Offset da Câmera: X: {offset.x:.0f}, Y: {offset.y:.0f}", True, (0, 255, 255))
                    surface.blit(txt_cam, (10, 35))

                    txt_fps = font.render(
                        f"FPS: {clock.get_fps():.0f}", True, (0, 255, 0))
                    surface.blit(txt_fps, (10, 60))

                    txt_life = font.render(
                        f"Vida: {player.health.current_hp:.0f}/{player.health.max_hp:.0f}", True, (255, 0, 0))
                    surface.blit(txt_life, (10, 85))

