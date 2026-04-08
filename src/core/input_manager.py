import pygame
from core.settings.settings import PLAYER_KEYS

class InputManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InputManager, cls).__new__(cls)
            cls._instance.keys = None
            cls._instance.mouse_buttons = None
        return cls._instance

    def update(self):
        """Atualiza o estado atual do teclado e do mouse. Deve ser chamado 1x por frame."""
        self.keys = pygame.key.get_pressed()
        self.mouse_buttons = pygame.mouse.get_pressed()

    def is_action_pressed(self, action_name: str) -> bool:
        """Retorna True se a tecla configurada para a ação estiver pressionada."""
        if self.keys is None:
            return False
            
        key_code = PLAYER_KEYS.get(action_name)
        if key_code is not None:
            return self.keys[key_code]
            
        return False