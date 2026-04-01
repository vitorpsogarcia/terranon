import pygame
from core.settings.settings import FPS
from core.states.base_state import BaseState
from core.settings.colors import Colors
from core.states.play_state import PlayState


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
        for event in events:
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
            

            if type(self.current_state) is PlayState and self.current_state.world is not None:
                camera_group = self.current_state.world.camera_group
                player = camera_group.target
            
                if player:
                    txt_pos = self.debug_font.render(f"Pos Real do Player: X: {player.pos.x:.0f}, Y: {player.pos.y:.0f}", True, (255, 255, 0))
                    self.tela.blit(txt_pos, (10, 10))
                    
                    offset = camera_group.offset
                    txt_cam = self.debug_font.render(f"Offset da Câmera: X: {offset.x:.0f}, Y: {offset.y:.0f}", True, (0, 255, 255))
                    self.tela.blit(txt_cam, (10, 35))
                    
                    txt_fps = self.debug_font.render(f"FPS: {self.clock.get_fps():.0f}", True, (0, 255, 0))
                    self.tela.blit(txt_fps, (10, 60))

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
