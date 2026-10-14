import pygame

_crosshair_cursor: pygame.cursors.Cursor | None = None


def create_crosshair_surface(
    size: int = 31,
    color: tuple[int, int, int] = (0, 255, 220),
) -> pygame.Surface:
    """Creates a high-contrast, pixel-crisp arcade crosshair surface."""
    center = size // 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.circle(surf, (0, 0, 0, 220), (center, center), 8, width=3)
    pygame.draw.line(surf, (0, 0, 0, 220), (center, 2), (center, 9), width=3)
    pygame.draw.line(surf, (0, 0, 0, 220), (center, 21), (center, 28), width=3)
    pygame.draw.line(surf, (0, 0, 0, 220), (2, center), (9, center), width=3)
    pygame.draw.line(surf, (0, 0, 0, 220), (21, center), (28, center), width=3)
    pygame.draw.circle(surf, (0, 0, 0, 220), (center, center), 2)

    pygame.draw.circle(surf, color, (center, center), 8, width=1)
    pygame.draw.line(surf, color, (center, 3), (center, 9), width=1)
    pygame.draw.line(surf, color, (center, 21), (center, 27), width=1)
    pygame.draw.line(surf, color, (3, center), (9, center), width=1)
    pygame.draw.line(surf, color, (21, center), (27, center), width=1)
    pygame.draw.circle(surf, (255, 255, 255), (center, center), 1)

    return surf


def get_crosshair_cursor() -> pygame.cursors.Cursor:
    """Returns or lazily creates the crosshair Cursor instance."""
    global _crosshair_cursor
    if _crosshair_cursor is None:
        size = 31
        center = size // 2
        surf = create_crosshair_surface(size=size)
        _crosshair_cursor = pygame.cursors.Cursor((center, center), surf)
    return _crosshair_cursor


def set_game_cursor():
    """Sets the cursor to the arcade crosshair reticle."""
    try:
        cursor = get_crosshair_cursor()
        pygame.mouse.set_cursor(cursor)
    except Exception:
        try:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        except Exception:
            pass


def set_ui_cursor():
    """Restores the standard arrow cursor for menus and UI navigation."""
    try:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    except Exception:
        pass
