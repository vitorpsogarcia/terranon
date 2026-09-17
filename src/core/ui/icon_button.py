from collections.abc import Callable

import pygame

from core.settings.colors import Colors
from core.ui.button import Button
from core.ui.icon import Icon


class IconButton(Button):
    """Botão compacto para exibição de ícones gráficos (ex: lixeira)."""

    def __init__(
        self,
        rect: pygame.Rect,
        icon_type: str = "trash",
        on_click: Callable[[], None] | None = None,
        bg_color: tuple = Colors.ui.button_disabled,
        hover_color: tuple = Colors.feedback.error,
        icon_color: tuple = Colors.text.primary,
        icon_hover_color: tuple = Colors.text.on_brand,
        border_color: tuple = Colors.ui.border,
        border_radius: int = 4,
        tooltip: str | None = None,
        auto_size: bool = True,
        clip_overflow: bool = True,
    ):
        icon = Icon(
            icon_type=icon_type,
            color=icon_color,
            hover_color=icon_hover_color,
        )

        super().__init__(
            rect=rect,
            on_click=on_click,
            bg_color=bg_color,
            hover_color=hover_color,
            border_color=border_color,
            border_hover_color=hover_color,  # Mantendo comportamento do IconButton antigo
            border_radius=border_radius,
            tooltip=tooltip,
            child=icon,
            auto_size=auto_size,
            clip_overflow=clip_overflow,
        )
