import pygame

from core.enums.game_event_enum import GameEventEnum
from core.manager.build_manager import BuildManager
from core.manager.economy_manager import EconomyManager
from core.manager.event_manager import EventManager
from core.settings.colors import Colors
from core.ui.button import Button
from core.ui.layout import Column, Row
from core.ui.layout_grid import GridLayout
from core.ui.panel import Panel
from core.ui.text import Text
from core.ui.ui_element import UIElement
from entities.structures.towers.generic_tower import GenericTower

# Dictionary holding the available categories and structures
AVAILABLE_STRUCTURES = {
    "Towers": [
        {
            "class": GenericTower,
            "name": "Turret",
            "cost": 50,
            "desc": "Basic defense tower.",
            "range": 100,
            "damage": 10,
        },
    ],
    "Economy": [
        # Example of another category
        # {"class": None, "name": "Mine", "cost": 100, "desc": "Generates crystals over time."},
    ],
}


class BuildCardButton(Button):
    def __init__(self, item_info, on_select, font_small, font_title):
        self.item_info = item_info
        self.on_select = on_select
        self.font_small = font_small
        self.font_title = font_title

        self.affordable = EconomyManager().current_points >= item_info["cost"]

        border_color = (
            Colors.building.greenish if self.affordable else Colors.building.reddish
        )

        children = [
            Text(item_info["name"], font=font_title, color=Colors.text.primary),
            Text(f"Cost: {item_info['cost']}", font=font_small, color=border_color),
        ]

        content = Column(children=children, spacing=4, padding=8)

        super().__init__(
            rect=pygame.Rect(0, 0, 120, 140),
            bg_color=Colors.ui.panel,
            hover_color=Colors.ui.button_hover,
            border_color=border_color,
            border_hover_color=Colors.ui.button_hover,
            child=content,
            on_click=self._on_click,
            auto_size=False,
        )

    def _on_click(self):
        if EconomyManager().current_points >= self.item_info["cost"]:
            self.on_select(self.item_info["class"])
        else:
            EventManager().emit(GameEventEnum.PLAY_SFX, filename="ui/error.wav")


class BuildMenuPanel(Panel):
    def __init__(self, rect: pygame.Rect, game_world):
        super().__init__(
            rect=rect,
            title="Build Menu",
            title_font=pygame.font.SysFont("Arial", 24, bold=True),
            border_color=Colors.ui.border,
            bg_color=Colors.ui.panel,
            auto_size=False,
        )
        self.game_world = game_world
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.font_medium = pygame.font.SysFont("Arial", 18)
        self.font_title = pygame.font.SysFont("Arial", 20, bold=True)

        self.current_category = "Towers"

        # Top-Right Currency Display
        self.currency_text = Text(
            "", font=self.font_medium, color=Colors.text.points_currency
        )
        self.currency_text.rect.topright = (self.rect.width - 20, 20)
        self.add_child(self.currency_text)

        # Main Layout
        self.main_row = Row(spacing=20, padding=20)
        self.main_row.rect.topleft = (20, 60)
        self.add_child(self.main_row)

        self.category_column = Column(spacing=10, auto_size=True)
        self.cards_grid = GridLayout(columns=3, spacing=15)

        self.main_row.children.append(self.category_column)
        self.main_row.children.append(self.cards_grid)

        self._build_categories()
        self._build_cards()

    def update(self, dt: float):
        super().update(dt)
        self.currency_text.text = f"Crystals: {EconomyManager().current_points}"

        # We could also dynamically update card borders here if economy changes while menu is open

    def _build_categories(self):
        self.category_column.children.clear()
        for cat in AVAILABLE_STRUCTURES:
            btn = Button(
                rect=pygame.Rect(0, 0, 100, 40),
                text=cat,
                font=self.font_medium,
                bg_color=Colors.ui.button_primary
                if cat != self.current_category
                else Colors.ui.button_hover,
                on_click=lambda c=cat: self._set_category(c),
                auto_size=False,
            )
            self.category_column.children.append(btn)
        self.category_column.update_layout()
        self.main_row.update_layout()

    def _set_category(self, category_name: str):
        self.current_category = category_name
        self._build_categories()  # Rebuild to update colors
        self._build_cards()

    def _build_cards(self):
        self.cards_grid.children.clear()
        items = AVAILABLE_STRUCTURES.get(self.current_category, [])

        for item in items:
            card = BuildCardButton(
                item_info=item,
                on_select=self._on_item_selected,
                font_small=self.font_small,
                font_title=self.font_title,
            )
            self.cards_grid.children.append(card)

        self.cards_grid.update_layout()
        self.main_row.update_layout()

    def _on_item_selected(self, structure_class):
        if structure_class:
            BuildManager().set_ghost(structure_class, self.game_world)
            self.visible = False  # Close menu
