from typing import TypeAlias

from pygame import Color


class Colors:
    class brand:
        """Cores principais que definem a identidade visual do jogo."""

        primary: Color = Color(13, 148, 136)  # Teal
        secondary: Color = Color(234, 179, 8)  # Amber

    class feedback:
        """Cores para fornecer feedback ao jogador (sucesso, erro, etc.)."""

        success: Color = Color(34, 197, 94)  # Green
        warning: Color = Color(234, 179, 8)  # Amber
        error: Color = Color(239, 68, 68)  # Red
        info: Color = Color(59, 130, 246)  # Blue

    class ui:
        """Cores para elementos de interface do usuário."""

        background: Color = Color(17, 24, 39)  # Dark Slate
        background_light: Color = Color(31, 41, 55)  # Lighter Slate

        button_primary: Color = Color(13, 148, 136)
        button_hover: Color = Color(15, 118, 110)
        button_disabled: Color = Color(55, 65, 81)

        border: Color = Color(55, 65, 81)

        panel: Color = Color(31, 41, 55)
        panel_transparent: Color = Color(31, 41, 55, 230)

        building_grid: Color = Color(200, 200, 200, 50)  # Light Gray with transparency

    class building:
        greenish: Color = Color(34, 197, 94, 100)  # Green with transparency
        reddish: Color = Color(239, 68, 68, 100)  # Red with transparency

    class text:
        """Cores para texto."""

        primary: Color = Color(243, 244, 246)  # Off-white
        secondary: Color = Color(156, 163, 175)  # Gray
        disabled: Color = Color(107, 114, 128)  # Darker Gray
        on_brand: Color = Color(
            255,
            255,
            255,
        )  # White (para uso em botões com a cor primária)
        error: Color = Color(252, 165, 165)  # Light Red

        points_currency: Color = Color(202, 138, 4)  # Green

    class game:
        """Cores específicas para elementos do mundo do jogo."""

        player_outline: Color = Color(59, 130, 246)
        enemy_outline: Color = Color(239, 68, 68)
        neutral_outline: Color = Color(209, 213, 219)

    class debug:
        """Cores para elementos de depuração."""

        hitbox: Color = Color(255, 255, 0)  # Yellow
        feet_hitbox: Color = Color(0, 255, 255)  # Cyan
        direction_vector: Color = Color(94, 234, 212)  # Teal

        turret: Color = Color(251, 191, 36)
        turret_range: Color = Color(16, 185, 129)
        targeting_line: Color = Color(239, 68, 68)

        base: Color = Color(3, 105, 161)
