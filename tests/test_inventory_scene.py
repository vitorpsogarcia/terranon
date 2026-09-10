import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.manager.economy_manager import EconomyManager
from core.manager.game_manager import GameManager
from core.manager.state_manager import StateManager
from core.states.base_state import GameScene
from core.states.ui.inventory_state import InventoryScene, InventoryState


class TestInventoryScene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.screen_size = (1056, 720)
        self.surface = pygame.Surface(self.screen_size)
        self.gm = GameManager(self.surface)
        self.sm = StateManager(self.gm)
        self.inv = InventoryScene(self.sm, self.screen_size)
        self.inv.enter()
        EconomyManager().reset_points()

    def test_inheritance_and_modal_flags(self):
        """InventoryScene deve ser GameScene modal transparente e com blocks_update=True."""
        self.assertTrue(issubclass(InventoryScene, GameScene))
        self.assertIs(InventoryState, InventoryScene)
        self.assertTrue(self.inv.is_transparent, "Deve ser transparente para jogo ser visto ao fundo")
        self.assertTrue(self.inv.blocks_update, "Deve bloquear update para congelar a partida")

    def test_close_via_key_i(self):
        """Pressionar a tecla I deve desempilhar a cena."""
        pop_called = False

        def mock_pop():
            nonlocal pop_called
            pop_called = True

        self.sm.pop = mock_pop

        event_i = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i)
        self.inv.handle_events([event_i])
        self.assertTrue(pop_called)

    def test_close_via_key_esc(self):
        """Pressionar a tecla ESC deve desempilhar a cena."""
        pop_called = False

        def mock_pop():
            nonlocal pop_called
            pop_called = True

        self.sm.pop = mock_pop

        event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.inv.handle_events([event_esc])
        self.assertTrue(pop_called)

    def test_close_via_button(self):
        """Clicar no botão Fechar deve desempilhar a cena."""
        pop_called = False

        def mock_pop():
            nonlocal pop_called
            pop_called = True

        self.sm.pop = mock_pop

        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=self.inv.btn_close.rect.center,
        )
        self.inv.handle_events([click_event])
        self.assertTrue(pop_called)

    def test_tower_selection_with_sufficient_points(self):
        """Com pontos suficientes, selecionar uma torre atualiza o índice selecionado."""
        EconomyManager().add_points(200)

        # Selecionar Torre Rápida (índice 1, custo 100)
        self.inv._on_slot_clicked(1)
        self.assertEqual(self.inv.selected_tower_idx, 1)
        self.assertIn("selecionada", self.inv.feedback_message)

    def test_tower_selection_insufficient_points(self):
        """Sem pontos suficientes, a seleção define aviso de pontos insuficientes."""
        EconomyManager().current_points = 10

        orig_idx = self.inv.selected_tower_idx
        self.inv._on_slot_clicked(2)  # Torre Pesada (custo 150)

        self.assertEqual(self.inv.selected_tower_idx, orig_idx)
        self.assertIn("insuficientes", self.inv.feedback_message.lower())

    def test_repair_kit_spends_points(self):
        """Comprar o kit de reparo consome pontos da economia."""
        EconomyManager().add_points(100)
        initial_points = EconomyManager().current_points

        # Índice 3 é o Kit de Reparo (custo 75)
        self.inv._on_slot_clicked(3)
        self.assertEqual(EconomyManager().current_points, initial_points - 75)
        self.assertIn("sucesso", self.inv.feedback_message.lower())

    def test_draw_renders_overlay_and_panel(self):
        """draw deve renderizar o overlay e o painel de inventário sem erros."""
        self.inv.draw(self.surface)


if __name__ == "__main__":
    unittest.main()
