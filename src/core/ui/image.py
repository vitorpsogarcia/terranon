import pygame

from core.manager.asset_manager import AssetManager
from core.ui.ui_element import UIElement


class Image(UIElement):
    """Componente que carrega e exibe uma imagem usando o AssetManager."""

    def __init__(
        self,
        image_name: str,
        image_path: str | None = None,
        rect: pygame.Rect | None = None,
        scale: float | None = None,
        size: tuple[int, int] | None = None,
        auto_size: bool = True,
        clip_overflow: bool = True,
    ):
        super().__init__(
            rect or pygame.Rect(0, 0, 0, 0),
            auto_size=auto_size,
            clip_overflow=clip_overflow,
        )
        self.image_name = image_name

        am = AssetManager()
        if image_path:
            self.surface = am.load_image(
                name=image_name, path=image_path, size=size, scale=scale
            )
        else:
            self.surface = am.get_image(name=image_name)

            # Se não fornecemos path mas fornecemos scale/size para uma imagem já carregada
            if size:
                self.surface = pygame.transform.scale(self.surface, size)
            elif scale:
                new_w = int(self.surface.get_width() * scale)
                new_h = int(self.surface.get_height() * scale)
                self.surface = pygame.transform.scale(self.surface, (new_w, new_h))

        # Auto-dimensiona o rect inicial para o tamanho da imagem se for 0
        if self.rect.width == 0 and self.rect.height == 0:
            self.rect.size = self.surface.get_size()

    def get_intrinsic_size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        # Desenha centralizado em seu próprio rect
        x = self.rect.centerx - self.surface.get_width() // 2
        y = self.rect.centery - self.surface.get_height() // 2
        surface.blit(self.surface, (x, y))
