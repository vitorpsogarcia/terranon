import pygame

from core.manager.debug_manager import DebugManager
from core.manager.input_manager import InputManager
from core.settings.colors import Colors
from core.settings.settings import FPS
from core.singleton_meta import SingletonMeta
from core.states.base_state import BaseState


class GameManager(metaclass=SingletonMeta):
    def __init__(self, tela: pygame.Surface):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self._running = True
        self.debug_font = pygame.font.SysFont(None, 24)
        self.state_stack: list[BaseState] = []

    @property
    def current_state(self) -> BaseState | None:
        if self.state_stack:
            return self.state_stack[-1]
        return None

    def change_state(self, new_state: BaseState):
        while self.state_stack:
            old_state = self.state_stack.pop()
            old_state.exit()

        self.state_stack.append(new_state)
        new_state.enter()

    def push_state(self, new_state: BaseState):
        self.state_stack.append(new_state)
        new_state.enter()

    def pop_state(self):
        if self.state_stack:
            old_state = self.state_stack.pop()
            old_state.exit()

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
        if not self.state_stack:
            return

        top_index = len(self.state_stack) - 1
        active_index = top_index

        while active_index > 0 and not getattr(self.state_stack[active_index], "blocks_update", True):
            active_index -= 1

        for i in range(active_index, top_index + 1):
            self.state_stack[i].update(dt)

    def on_render(self):
        self.tela.fill(Colors.ui.background)

        for state in self.state_stack:
            state.draw(self.tela)

        DebugManager().draw_ui_debug(
            self.tela, self.current_state, self.clock, self.debug_font
        )

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
