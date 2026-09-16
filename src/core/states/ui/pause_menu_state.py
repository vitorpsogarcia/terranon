from typing import TYPE_CHECKING
import pygame

from core.enums.game_state_enum import GameStateEnum
from core.settings.colors import Colors
from core.states.base_state import GameScene
from core.ui.button import Button
from core.ui.panel import UIPanel

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager


class PauseMenuScene(GameScene):
    """Menu de Pausa modal sobreposto à partida durante a jogatina."""

    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(
            state_manager=state_manager,
            screen_size=screen_size,
            is_transparent=True,
            blocks_update=True,
        )
        self.title_font = pygame.font.SysFont("Arial", 44, bold=True)
        self.btn_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)

        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        panel_w = 380
        panel_h = 340
        panel_x = center_x - panel_w // 2
        panel_y = center_y - panel_h // 2
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        self.panel = UIPanel(
            rect=self.panel_rect,
            bg_color=Colors.ui.panel,
            border_color=Colors.brand.primary,
            border_width=2,
            border_radius=12,
            title="JOGO PAUSADO",
            title_font=self.title_font,
            title_color=Colors.brand.secondary,
        )

        btn_w = 300
        btn_h = 48
        btn_x = center_x - btn_w // 2

        # Opção 1: Continuar Partida
        self.btn_resume = Button(
            rect=pygame.Rect(btn_x, panel_y + 85, btn_w, btn_h),
            text="CONTINUAR",
            font=self.btn_font,
            on_click=self._resume,
            bg_color=Colors.brand.primary,
            hover_color=Colors.ui.button_hover,
        )

        # Opção 2: Reiniciar Partida
        self.btn_restart = Button(
            rect=pygame.Rect(btn_x, panel_y + 145, btn_w, btn_h),
            text="REINICIAR PARTIDA",
            font=self.btn_font,
            on_click=self._restart,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.brand.primary,
        )

        # Opção 3: Retornar ao Menu Principal
        self.btn_menu = Button(
            rect=pygame.Rect(btn_x, panel_y + 205, btn_w, btn_h),
            text="MENU PRINCIPAL",
            font=self.btn_font,
            on_click=self._go_to_menu,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )

        self.panel.add_child(self.btn_resume)
        self.panel.add_child(self.btn_restart)
        self.panel.add_child(self.btn_menu)

    def _resume(self):
        """Desempilha o menu de pausa e retorna à partida de onde parou."""
        self.state_manager.pop()

    def _restart(self):
        """Reinicia a partida limpando a pilha e recarregando o PlayState."""
        self.state_manager.change_to(GameStateEnum.PLAY)

    def _go_to_menu(self):
        """Retorna à tela inicial (TitleMenuScene)."""
        self.state_manager.change_to(GameStateEnum.MENU)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        self.panel.update(dt)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._resume()
                    return
                elif event.key == pygame.K_RETURN:
                    self._resume()
                    return

            if self.panel.handle_event(event):
                continue

    def draw(self, surface: pygame.Surface) -> None:
        # Fundo escurecido translúcido cobrindo a partida
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill(Colors.ui.panel_transparent)
        surface.blit(overlay, (0, 0))

        # Painel central de pausa
        self.panel.draw(surface)

        # Dica de atalho
        hint_surf = self.small_font.render(
            "Pressione ESC ou ENTER para Continuar", True, Colors.text.disabled
        )
        surface.blit(
            hint_surf,
            (
                self.panel_rect.centerx - hint_surf.get_width() // 2,
                self.panel_rect.bottom - 42,
            ),
        )


# Alias para retrocompatibilidade
PauseMenuState = PauseMenuScene
