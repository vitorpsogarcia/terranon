import pygame

from core.debug_manager import DebugManager
from core.event_manager import EventManager
from core.enums.debug_option_enum import DebugOption
from core.enums.game_event_enum import GameEventEnum
from core.settings.settings import PLAYER_KEYS


class InputManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.keys = None
            cls._instance.mouse_buttons = None
            cls._instance.f3_pressed = False
        return cls._instance

    def update(self):
        """Atualiza o estado atual do teclado e do mouse. Deve ser chamado 1x por frame."""
        self.keys = pygame.key.get_pressed()
        self.mouse_buttons = pygame.mouse.get_pressed()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                self.f3_pressed = True
            
            if self.f3_pressed:
                if event.key == pygame.K_c:
                    DebugManager.toggle_option(DebugOption.COLLIDERS)
                elif event.key == pygame.K_s:
                    DebugManager.toggle_option(DebugOption.PLAYER_STATUS)
                elif event.key == pygame.K_d:
                    DebugManager.toggle_option(DebugOption.CREATURE_DIRECTIONS)
                elif event.key == pygame.K_z:
                    EventManager.get_instance().emit(GameEventEnum.RESET_WAVES)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_F3:
                self.f3_pressed = False

    def is_action_pressed(self, action_name: str) -> bool:
        """Retorna True se a tecla configurada para a ação estiver pressionada."""
        if self.keys is None:
            return False
            
        key_code = PLAYER_KEYS.get(action_name)
        if key_code is not None:
            return self.keys[key_code]
            
        return False