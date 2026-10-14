import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.components.health_component import HealthComponent
from core.components.shield_component import ShieldComponent
from core.manager.economy_manager import EconomyManager
from core.ui.game_hud import GameHUD
from core.ui.icon import Icon


class DummyEntity:
    def __init__(self, hp: float = 100.0, max_hp: float = 100.0, has_shield: bool = False, shield_active: bool = False):
        self.health = HealthComponent(max_hp=max_hp)
        self.health.current_hp = hp
        if has_shield:
            self.shield = ShieldComponent(max_shield=50.0, current_shield=25.0, is_active=shield_active)
        else:
            self.shield = None


class TestGameHUD(unittest.TestCase):
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
        self.hud = GameHUD(self.screen_size)
        EconomyManager().reset_points()

    def test_icon_intrinsic_sizes(self):
        """Verifica se os novos tipos de ícones retornam os tamanhos esperados."""
        coin = Icon(icon_type="coin")
        avatar = Icon(icon_type="avatar")
        shield = Icon(icon_type="shield")
        trash = Icon(icon_type="trash")

        self.assertEqual(coin.get_intrinsic_size(), (24, 24))
        self.assertEqual(avatar.get_intrinsic_size(), (72, 72))
        self.assertEqual(shield.get_intrinsic_size(), (24, 24))
        self.assertEqual(trash.get_intrinsic_size(), (16, 16))

    def test_icon_draw_procedural(self):
        """Garante que todos os ícones desenham proceduralmente sem falhas."""
        icons = [
            Icon(icon_type="coin", rect=pygame.Rect(10, 10, 24, 24)),
            Icon(icon_type="avatar", rect=pygame.Rect(50, 50, 60, 60)),
            Icon(icon_type="shield", rect=pygame.Rect(120, 120, 24, 24)),
            Icon(icon_type="trash", rect=pygame.Rect(160, 160, 16, 16)),
        ]
        for icon in icons:
            icon.draw(self.surface)

    def test_hud_draw_basic_player(self):
        """HUD deve renderizar vida do jogador, moeda e score sem erros."""
        EconomyManager().add_points(150)
        player = DummyEntity(hp=80.0, max_hp=100.0, has_shield=False)

        self.hud.draw(self.surface, player=player, main_base=None)
        self.assertEqual(self.hud.economy.current_points, 150)
        self.assertEqual(self.hud.economy.total_points, 150)

    def test_hud_draw_shield_when_active(self):
        """Barra de escudo deve ser desenhada quando o escudo estiver ativo."""
        player = DummyEntity(hp=100.0, max_hp=100.0, has_shield=True, shield_active=True)
        self.hud.draw(self.surface, player=player, main_base=None)

    def test_hud_draw_shield_hidden_when_inactive(self):
        """Barra de escudo não deve quebrar quando o escudo estiver inativo."""
        player = DummyEntity(hp=100.0, max_hp=100.0, has_shield=True, shield_active=False)
        self.hud.draw(self.surface, player=player, main_base=None)

    def test_hud_draw_with_main_base(self):
        """HUD deve renderizar barra da base central quando presente."""
        player = DummyEntity(hp=100.0, max_hp=100.0)
        base = DummyEntity(hp=500.0, max_hp=1000.0)

        self.hud.draw(self.surface, player=player, main_base=base)

    def test_hud_clamping_values(self):
        """Valores negativos ou superiores ao máximo devem ser tratados defensivamente."""
        player = DummyEntity(hp=-20.0, max_hp=100.0, has_shield=True, shield_active=True)
        player.shield.current_shield = 999.0
        player.shield.max_shield = 50.0

        # Não deve lançar erro
        self.hud.draw(self.surface, player=player)


if __name__ == "__main__":
    unittest.main()
