import pygame

from core.ui.ui_element import UIElement


class CircleHighlight(UIElement):
    def __init__(self, child: UIElement, color=(255, 255, 255, 50), radius=35):
        super().__init__(pygame.Rect(0, 0, radius * 2, radius * 2))
        self.child = child
        self.color = color
        self.radius = radius
        self.update_layout()

    def get_intrinsic_size(self):
        return (self.radius * 2, self.radius * 2)

    def update_layout(self):
        self.child.rect.center = self.rect.center
        self.child.update_layout()

    def handle_event(self, event):
        return self.child.handle_event(event)

    def update(self, dt):
        self.child.update(dt)

    def draw(self, surface):
        if not self.visible:
            return

        # Desenha o círculo
        target_rect = pygame.Rect(
            self.rect.centerx - self.radius,
            self.rect.centery - self.radius,
            self.radius * 2,
            self.radius * 2,
        )
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(
            shape_surf, self.color, (self.radius, self.radius), self.radius
        )
        surface.blit(shape_surf, target_rect)

        self.child.draw(surface)
