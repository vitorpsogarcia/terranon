import pygame

from core.manager.debug_manager import DebugManager
from core.manager.input_manager import InputManager
from core.settings.colors import Colors
from core.settings.settings import FPS
from core.states.base_state import BaseState


class GameManager:
    current_state: BaseState | None = None

    def __init__(self, tela: pygame.Surface):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self._running = True
        self.debug_font = pygame.font.SysFont(None, 24)

    def change_state(self, new_state: BaseState):
        if self.current_state is not None:
            self.current_state.exit()

        self.current_state = new_state
        self.current_state.enter()

    def on_execute(self):
        dt = self.clock.tick(FPS) / 1000.0

        while self._running:
            self.on_events()
            dt = max(0.001, min(0.05, dt))
            self.update(dt)
            self.on_render()
            dt = self.clock.tick(FPS) / 1000.0

        self.on_cleanup()

    def on_events(self):
        events = pygame.event.get()
        InputManager().update()
        for event in events:
            InputManager().handle_event(event)
            if event.type == pygame.QUIT:
                self._running = False

        if self.current_state:
            self.current_state.handle_events(events)

    def update(self, dt: float):
        if self.current_state:
            self.current_state.update(dt)

    def on_render(self):
        self.tela.fill(Colors.ui.background)

        if self.current_state:
            self.current_state.draw(self.tela)

        DebugManager().draw_ui_debug(
            self.tela, self.current_state, self.clock, self.debug_font
        )

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
