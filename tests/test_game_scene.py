import os
import sys
import unittest
import pygame

# Adicionar src ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.game_world import GameWorld
from core.states.base_state import BaseState, GameScene
from core.states.play_state import PlayState
from core.states.ui.game_over import GameOverState
from core.states.ui.inventory_state import InventoryState
from core.states.ui.menu_state import MenuState
from core.states.ui.pause_menu_state import PauseMenuState


class ConcreteTestScene(GameScene):
    """Cena concreta mínima para validar a interface."""

    def __init__(self, state_manager=None, screen_size=(800, 600), is_transparent=False, blocks_update=True):
        super().__init__(state_manager, screen_size, is_transparent, blocks_update)
        self.entered = False
        self.exited = False
        self.updated = False
        self.events_handled = False
        self.drawn = False

    def enter(self) -> None:
        self.entered = True

    def exit(self) -> None:
        self.exited = True

    def update(self, dt: float) -> None:
        self.updated = True

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        self.events_handled = True

    def draw(self, surface: pygame.Surface) -> None:
        self.drawn = True


class IncompleteTestScene(GameScene):
    """Cena que não implementa os métodos abstratos."""
    pass


class TestGameSceneInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_gamescene_cannot_be_instantiated_directly(self):
        """GameScene é abstrata e deve lançar TypeError se instanciada sem implementar métodos."""
        with self.assertRaises(TypeError):
            GameScene()

    def test_incomplete_subclass_cannot_be_instantiated(self):
        """Subclasse que não implementa todos os métodos abstratos não pode ser instanciada."""
        with self.assertRaises(TypeError):
            IncompleteTestScene()

    def test_concrete_subclass_lifecycle(self):
        """Uma subclasse concreta deve responder a todo o ciclo de vida polimórfico."""
        scene = ConcreteTestScene(is_transparent=True, blocks_update=False)
        self.assertTrue(scene.is_transparent)
        self.assertFalse(scene.blocks_update)

        surface = pygame.Surface((100, 100))
        events = [pygame.event.Event(pygame.USEREVENT)]

        scene.enter()
        self.assertTrue(scene.entered)

        scene.handle_events(events)
        self.assertTrue(scene.events_handled)

        scene.update(0.016)
        self.assertTrue(scene.updated)

        scene.draw(surface)
        self.assertTrue(scene.drawn)

        scene.exit()
        self.assertTrue(scene.exited)

    def test_base_state_is_alias_for_game_scene(self):
        """BaseState deve ser exatamente GameScene para retrocompatibilidade."""
        self.assertIs(BaseState, GameScene)

    def test_all_scene_classes_inherit_from_gamescene(self):
        """Todas as cenas do jogo e de UI devem herdar de GameScene."""
        scene_classes = [
            GameWorld,
            PlayState,
            MenuState,
            InventoryState,
            PauseMenuState,
            GameOverState,
        ]
        for cls in scene_classes:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(
                    issubclass(cls, GameScene),
                    f"{cls.__name__} não herda de GameScene",
                )

    def test_required_methods_signature_on_all_scenes(self):
        """Garantir que todas as cenas implementam enter, exit, update, handle_events, draw."""
        required_methods = ["enter", "exit", "update", "handle_events", "draw"]
        scene_classes = [
            GameWorld,
            PlayState,
            MenuState,
            InventoryState,
            PauseMenuState,
            GameOverState,
        ]

        for cls in scene_classes:
            for method_name in required_methods:
                with self.subTest(cls=cls.__name__, method=method_name):
                    self.assertTrue(
                        hasattr(cls, method_name),
                        f"{cls.__name__} não possui o método {method_name}",
                    )
                    method = getattr(cls, method_name)
                    self.assertTrue(
                        callable(method),
                        f"{cls.__name__}.{method_name} não é chamável",
                    )

    def test_ui_states_instantiation_and_attributes(self):
        """Verifica atributos is_transparent e blocks_update nas instâncias dos estados de UI."""
        screen_size = (800, 600)

        menu = MenuState(state_manager=None, screen_size=screen_size)
        self.assertFalse(menu.is_transparent)
        self.assertTrue(menu.blocks_update)

        inv = InventoryState(state_manager=None, screen_size=screen_size)
        self.assertTrue(inv.is_transparent)
        self.assertTrue(inv.blocks_update)

        pause = PauseMenuState(state_manager=None, screen_size=screen_size)
        self.assertTrue(pause.is_transparent)
        self.assertTrue(pause.blocks_update)

        game_over = GameOverState(state_manager=None, screen_size=screen_size)
        self.assertFalse(game_over.is_transparent)
        self.assertTrue(game_over.blocks_update)


if __name__ == "__main__":
    unittest.main()

