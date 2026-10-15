import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.manager.build_manager import BuildManager
from core.manager.economy_manager import EconomyManager
from core.manager.spatial_manager import SpatialManager
from core.settings.colors import Colors
from core.ui.build_menu_panel import AVAILABLE_STRUCTURES, BuildCardButton, BuildMenuPanel
from core.ui.icon import Icon
from entities.structures.towers.generic_tower import GenericTower


class DummyWorld:
    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)


class TestBuildSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        EconomyManager().reset_points()
        self.world = DummyWorld()
        self.panel_rect = pygame.Rect(100, 100, 900, 600)
        self.build_menu = BuildMenuPanel(self.panel_rect, self.world)
        self.surface = pygame.Surface((1056, 720))

    def tearDown(self):
        if BuildManager().is_building:
            BuildManager().cancel_build()

    def test_build_menu_panel_semi_transparent(self):
        """Verifica se o painel de construção é semi-opaco."""
        self.assertEqual(self.build_menu.bg_color, Colors.ui.panel_semi_transparent)
        self.assertTrue(len(self.build_menu.bg_color) == 4)
        self.assertLess(self.build_menu.bg_color[3], 255)
        self.assertGreater(self.build_menu.bg_color[3], 100)

    def test_build_menu_uses_criptcoins_and_coin_icon(self):
        """Garante que o nome exibido é Criptcoins e que utiliza o ícone de moeda."""
        EconomyManager().add_points(150)
        self.build_menu.update(0.016)

        # O texto deve conter 'Criptcoins: 150' e não 'Cristais'
        self.assertIn("Criptcoins: 150", self.build_menu.currency_text.text)
        self.assertNotIn("Cristais", self.build_menu.currency_text.text)

        # O menu deve possuir o ícone de moeda
        self.assertIsInstance(self.build_menu.coin_icon, Icon)
        self.assertEqual(self.build_menu.coin_icon.icon_type, "coin")

    def test_build_card_button_has_coin_icon_and_affordability(self):
        """Testa o botão do card de construção com ícone e verificação de custo."""
        item = AVAILABLE_STRUCTURES["Torres"][0]
        selected_class = None

        def on_select(cls):
            nonlocal selected_class
            selected_class = cls

        font_sm = pygame.font.SysFont("Arial", 14)
        font_ti = pygame.font.SysFont("Arial", 18, bold=True)

        card = BuildCardButton(item, on_select, font_sm, font_ti)

        # Deve conter o ícone de moeda
        self.assertIsInstance(card.cost_icon, Icon)
        self.assertEqual(card.cost_icon.icon_type, "coin")

        # Com 0 moedas, não deve conseguir comprar
        self.assertFalse(card.affordable)
        card._on_click()
        self.assertIsNone(selected_class)

        # Adiciona pontos suficientes
        EconomyManager().add_points(item["cost"] + 10)
        card.update(0.016)
        self.assertTrue(card.affordable)

        # Ao clicar, seleciona a classe
        card._on_click()
        self.assertEqual(selected_class, item["class"])

    def test_build_menu_draw_does_not_crash(self):
        """Renderização do menu semi-opaco não deve gerar exceções."""
        EconomyManager().add_points(200)
        self.build_menu.update(0.016)
        self.build_menu.draw(self.surface)

    def test_generic_tower_ghost_properties_and_no_shooting(self):
        """Verifica que uma GenericTower em modo ghost é translúcida e não atira."""
        ghost = GenericTower(pygame.Vector2(100, 100), is_ghost=True)
        self.assertTrue(ghost.is_ghost)
        self.assertEqual(ghost.render_component.opacity, 128)

        # Update no ghost não deve criar projéteis nem definir alvos
        ghost.update(1.0)
        self.assertIsNone(ghost.target)

        # Torre real (não ghost)
        real = GenericTower(pygame.Vector2(200, 200), is_ghost=False)
        self.assertFalse(real.is_ghost)
        self.assertEqual(real.render_component.opacity, 255)

    def test_build_manager_workflow(self):
        """Testa o ciclo de construção: selecionar fantasma, encaixe no grid, dedução de pontos e cancelamento."""
        EconomyManager().add_points(100)
        bm = BuildManager()

        # Inicia colocação de torre
        bm.set_ghost(GenericTower, self.world)
        self.assertTrue(bm.is_building)
        self.assertIsNotNone(bm.current_ghost)
        self.assertIn(bm.current_ghost, self.world.objects)

        # Movimento e snap ao grid (64 px)
        bm.update(pygame.Vector2(130, 270))
        self.assertEqual(bm.current_ghost.transform.pos.x, 128)
        self.assertEqual(bm.current_ghost.transform.pos.y, 256)

        # Finaliza construção
        bm.attempt_build()
        self.assertFalse(bm.is_building)
        self.assertIsNone(bm.current_ghost)
        self.assertEqual(EconomyManager().current_points, 50)  # 100 - 50 custo da torre

    def test_category_buttons_left_aligned_and_ghost_style(self):
        """Verifica se os botões de categoria são alinhados à esquerda, tipo ghost com linha inferior e mantêm fundo quando selecionados."""
        self.assertEqual(self.build_menu.category_column.align, "left")

        cat_buttons = self.build_menu.category_column.children
        self.assertGreaterEqual(len(cat_buttons), 2)

        # "Torres" deve estar selecionada por padrão
        torres_btn = cat_buttons[0]
        self.assertEqual(torres_btn.text, "Torres")
        self.assertEqual(torres_btn.text_align, "left")
        self.assertTrue(torres_btn.bottom_line_only)
        self.assertEqual(torres_btn.bg_color, Colors.ui.button_primary)
        self.assertEqual(torres_btn.border_color, Colors.brand.secondary)

        # "Economia" deve ser ghost (sem cor de fundo sólida quando não selecionada)
        eco_btn = cat_buttons[1]
        self.assertEqual(eco_btn.text, "Economia")
        self.assertEqual(eco_btn.text_align, "left")
        self.assertTrue(eco_btn.bottom_line_only)
        self.assertIsNone(eco_btn.bg_color)
        self.assertEqual(eco_btn.border_color, Colors.ui.border)

        # Ao selecionar Economia, ela passa a manter a cor de fundo e Torres passa a ser ghost
        eco_btn.on_click()
        self.assertEqual(self.build_menu.current_category, "Economia")

        new_torres_btn = self.build_menu.category_column.children[0]
        new_eco_btn = self.build_menu.category_column.children[1]

        self.assertIsNone(new_torres_btn.bg_color)
        self.assertEqual(new_eco_btn.bg_color, Colors.ui.button_primary)
        self.assertEqual(new_eco_btn.border_color, Colors.brand.secondary)

