from typing import TYPE_CHECKING
import pygame

from core.enums.game_state_enum import GameStateEnum
from core.manager.highscore_manager import HighscoreManager
from core.manager.sound_manager import SoundManager
from core.settings.colors import Colors
from core.states.base_state import GameScene
from core.ui.button import Button

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager


class GameOverState(GameScene):
    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.font = pygame.font.SysFont("Arial", 72, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 28)
        self.info_font = pygame.font.SysFont("Arial", 22)

        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        self.btn_restart = Button(
            rect=pygame.Rect(center_x - 140, center_y + 40, 280, 48),
            text="JOGAR NOVAMENTE",
            font=self.info_font,
            on_click=self._restart_game,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        self.btn_menu = Button(
            rect=pygame.Rect(center_x - 140, center_y + 100, 280, 48),
            text="MENU PRINCIPAL",
            font=self.info_font,
            on_click=self._go_to_menu,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.ui.button_hover,
        )

    def enter(self):
        try:
            SoundManager().stop_music(fade_ms=500)
            SoundManager().play_sfx("effects/death.mp3")
        except Exception as e:
            pass

    def exit(self):
        pass

    def _restart_game(self):
        self.state_manager.change_to(GameStateEnum.PLAY)

    def _go_to_menu(self):
        self.state_manager.change_to(GameStateEnum.MENU)

    def update(self, dt: float):
        pass

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._go_to_menu()
                return

            if self.btn_restart.handle_event(event):
                return
            if self.btn_menu.handle_event(event):
                return

    def draw(self, surface: pygame.Surface):
        surface.fill(Colors.ui.background)

        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        game_over_text = self.font.render("GAME OVER", True, Colors.feedback.error)
        surface.blit(
            game_over_text,
            (center_x - game_over_text.get_width() // 2, center_y - 120),
        )

        player_name = HighscoreManager().current_player_name
        name_surf = self.small_font.render(f"Jogador: {player_name}", True, Colors.text.secondary)
        surface.blit(name_surf, (center_x - name_surf.get_width() // 2, center_y - 30))

        self.btn_restart.draw(surface)
        self.btn_menu.draw(surface)
