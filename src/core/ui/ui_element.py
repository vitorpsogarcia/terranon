from abc import ABC, abstractmethod

import pygame


class UIElement(ABC):
    def __init__(
        self, rect: pygame.Rect, auto_size: bool = True, clip_overflow: bool = True
    ):
        self.rect = rect
        self.visible: bool = True
        self.enabled: bool = True
        self.auto_size: bool = auto_size
        self.clip_overflow: bool = clip_overflow

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass

    def get_intrinsic_size(self) -> tuple[int, int]:
        """Retorna o tamanho natural do elemento (largura, altura)."""
        return self.rect.size

    def update_layout(self) -> None:
        """Atualiza recursivamente o tamanho e posição deste elemento e de seus filhos."""
        pass

    def draw_with_clip(self, surface: pygame.Surface, draw_func):
        """Helper para aplicar o clip rect caso clip_overflow seja True."""
        if getattr(self, "clip_overflow", False) and not getattr(
            self, "auto_size", True
        ):
            old_clip = surface.get_clip()
            surface.set_clip(self.rect)
            draw_func(surface)
            surface.set_clip(old_clip)
        else:
            draw_func(surface)
