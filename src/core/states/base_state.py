from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pygame

from core.settings.settings import SCREEN_HEIGHT, SCREEN_WIDTH

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager


class GameScene(ABC):
    def __init__(
        self,
        state_manager: "StateManager | None" = None,
        screen_size: tuple[int, int] = (SCREEN_WIDTH, SCREEN_HEIGHT),
        is_transparent: bool = False,
        blocks_update: bool = True,
    ):
        self.state_manager = state_manager
        self.screen_size = screen_size
        self.is_transparent: bool = is_transparent
        self.blocks_update: bool = blocks_update

    @abstractmethod
    def enter(self) -> None:
        """Chamado quando a cena é empilhada ou ativada."""
        pass

    @abstractmethod
    def exit(self) -> None:
        """Chamado quando a cena é desempilhada ou substituída."""
        pass

    def on_pause(self) -> None:
        """Chamado quando outra cena é empilhada sobre esta cena."""
        pass

    def on_resume(self) -> None:
        """Chamado quando a cena acima é desempilhada e esta cena recupera o foco."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Atualiza o estado lógico da cena com base no delta time."""
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processa eventos de entrada recebidos pelo loop do jogo."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza os elementos da cena sobre a superfície informada."""
        pass


BaseState = GameScene

