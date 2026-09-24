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
from entities.structures.towers.generic_tower import GenericTower

# Dictionary holding the available categories and structures
AVAILABLE_STRUCTURES = {
    "Torres": [
        {
            "class": GenericTower,
            "name": "Torreta",
            "cost": 50,
            "desc": "Torre básica de defesa.",
            "range": 100,
            "damage": 10,
            "image_name": "generic_tower_64",
            "image_path": "Tower_gun.png",
        },
    ],
    "Economia": [
        # Example of another category
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

        children = []

        if "image_name" in item_info and "image_path" in item_info:
            from core.ui.image import Image
            from core.ui.circle_highlight import CircleHighlight

            img = Image(
                image_name=item_info["image_name"],
                image_path=item_info["image_path"],
                size=(64, 64),
            )
            children.append(CircleHighlight(img, color=(255, 255, 255, 30), radius=40))

        children.extend([
            Text(item_info["name"], font=font_title, color=Colors.text.primary),
            Text(f"Custo: {item_info['cost']}", font=font_small, color=border_color),
        ])

        content = Column(children=children, spacing=8, padding=8)

        super().__init__(
            rect=pygame.Rect(0, 0, 130, 160),
            bg_color=(60, 70, 85),  # Lighter background for the card
            hover_color=(80, 90, 105),
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

    def update(self, dt: float):
        super().update(dt)
        self.affordable = EconomyManager().current_points >= self.item_info["cost"]
        self.border_color = (
            Colors.building.greenish if self.affordable else Colors.building.reddish
        )

        # We also need to update the color of the text child that shows cost
        for c in self.children[0].children:
            if isinstance(c, Text) and c.text.startswith("Custo:"):
                c.color = self.border_color


class BuildMenuPanel(Panel):
    def __init__(self, rect: pygame.Rect, game_world):
        super().__init__(
            rect=rect,
            title="Menu de Construção",
            title_font=pygame.font.SysFont("Arial", 24, bold=True),
            border_color=Colors.ui.border,
            bg_color=Colors.ui.panel,
            auto_size=False,
        )
        self.game_world = game_world
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.font_medium = pygame.font.SysFont("Arial", 18)
        self.font_title = pygame.font.SysFont("Arial", 20, bold=True)

        self.current_category = "Torres"

        # Top-Right Currency Display
        self.currency_text = Text(
            "", font=self.font_medium, color=Colors.text.points_currency
        )
        self.currency_text.rect.topright = (self.rect.right - 20, self.rect.top + 20)
        self.add_child(self.currency_text)

        # Main Layout
        self.main_row = Row(spacing=20, padding=20)
        self.main_row.rect.topleft = (self.rect.left + 20, self.rect.top + 60)
        self.add_child(self.main_row)

        self.category_column = Column(spacing=10, auto_size=True)
        self.cards_grid = GridLayout(columns=3, spacing=15)

        self.main_row.children.append(self.category_column)
        self.main_row.children.append(self.cards_grid)

        self._build_categories()
        self._build_cards()

    def update(self, dt: float):
        super().update(dt)
        self.currency_text.text = f"Cristais: {EconomyManager().current_points}"
        self.currency_text.rect.size = self.currency_text.get_intrinsic_size()
        # Pin to top-right
        self.currency_text.rect.topright = (self.rect.right - 20, self.rect.top + 20)

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
