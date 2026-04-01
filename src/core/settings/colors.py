from typing import TypeAlias

Color: TypeAlias = tuple[int, int, int] | tuple[int, int, int, int]


class Colors:
    class brand:
        """Cores principais que definem a identidade visual do jogo."""
        primary: Color = (13, 148, 136)  # Teal
        secondary: Color = (234, 179, 8) # Amber

    class feedback:
        """Cores para fornecer feedback ao jogador (sucesso, erro, etc.)."""
        success: Color = (34, 197, 94)   # Green
        warning: Color = (234, 179, 8)  # Amber
        error: Color = (239, 68, 68)    # Red
        info: Color = (59, 130, 246)    # Blue

    class ui:
        """Cores para elementos de interface do usuário."""
        background: Color = (17, 24, 39)        # Dark Slate
        background_light: Color = (31, 41, 55)  # Lighter Slate

        button_primary: Color = (13, 148, 136)
        button_hover: Color = (15, 118, 110)
        button_disabled: Color = (55, 65, 81)

        border: Color = (55, 65, 81)

        panel: Color = (31, 41, 55)
        panel_transparent: Color = (31, 41, 55, 230)

    class text:
        """Cores para texto."""
        primary: Color = (243, 244, 246)     # Off-white
        secondary: Color = (156, 163, 175)   # Gray
        disabled: Color = (107, 114, 128)  # Darker Gray
        on_brand: Color = (255, 255, 255)    # White (para uso em botões com a cor primária)
        error: Color = (252, 165, 165)      # Light Red

    class game:
        """Cores específicas para elementos do mundo do jogo."""
        player_outline: Color = (59, 130, 246)
        enemy_outline: Color = (239, 68, 68)
        neutral_outline: Color = (209, 213, 219)
