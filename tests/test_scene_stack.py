import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.manager.game_manager import GameManager
from core.states.base_state import GameScene


class MockScene(GameScene):
    def __init__(
        self,
        name: str,
        is_transparent: bool = False,
        blocks_update: bool = True,
    ):
        super().__init__(
            state_manager=None,
            screen_size=(800, 600),
            is_transparent=is_transparent,
            blocks_update=blocks_update,
        )
        self.name = name
        self.enter_called = 0
        self.exit_called = 0
        self.pause_called = 0
        self.resume_called = 0
        self.update_called = 0
        self.events_called = 0
        self.draw_called = 0

    def enter(self) -> None:
        self.enter_called += 1

    def exit(self) -> None:
        self.exit_called += 1

    def on_pause(self) -> None:
        self.pause_called += 1

    def on_resume(self) -> None:
        self.resume_called += 1

    def update(self, dt: float) -> None:
        self.update_called += 1

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        self.events_called += 1

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_called += 1


class TestSceneStack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        # Cria uma surface e obtém o GameManager singleton
        self.surface = pygame.Surface((800, 600))
        self.gm = GameManager(self.surface)
        self.gm.state_stack.clear()

    def tearDown(self):
        self.gm.state_stack.clear()

    def test_push_state_lifecycle(self):
        """push_state deve chamar on_pause na cena anterior e enter na nova cena."""
        scene1 = MockScene("play")
        scene2 = MockScene("inventory", is_transparent=True)

        self.gm.push_state(scene1)
        self.assertEqual(len(self.gm.state_stack), 1)
        self.assertEqual(scene1.enter_called, 1)
        self.assertEqual(scene1.pause_called, 0)
        self.assertIs(self.gm.current_state, scene1)

        self.gm.push_state(scene2)
        self.assertEqual(len(self.gm.state_stack), 2)
        self.assertEqual(scene1.pause_called, 1)
        self.assertEqual(scene2.enter_called, 1)
        self.assertIs(self.gm.current_state, scene2)

    def test_pop_state_lifecycle(self):
        """pop_state deve chamar exit na cena removida e on_resume na cena que recupera o foco."""
        scene1 = MockScene("play")
        scene2 = MockScene("pause", is_transparent=True)

        self.gm.push_state(scene1)
        self.gm.push_state(scene2)

        popped = self.gm.pop_state()
        self.assertIs(popped, scene2)
        self.assertEqual(scene2.exit_called, 1)
        self.assertEqual(scene1.resume_called, 1)
        self.assertEqual(len(self.gm.state_stack), 1)
        self.assertIs(self.gm.current_state, scene1)

    def test_pop_empty_stack(self):
        """pop_state em pilha vazia deve retornar None sem exceção."""
        self.assertIsNone(self.gm.pop_state())

    def test_change_state_cleans_full_stack(self):
        """change_state deve limpar toda a pilha chamando exit em todas e enter na nova cena."""
        scene1 = MockScene("play")
        scene2 = MockScene("pause")
        scene3 = MockScene("menu")

        self.gm.push_state(scene1)
        self.gm.push_state(scene2)
        self.assertEqual(len(self.gm.state_stack), 2)

        self.gm.change_state(scene3)
        self.assertEqual(len(self.gm.state_stack), 1)
        self.assertEqual(scene2.exit_called, 1)
        self.assertEqual(scene1.exit_called, 1)
        self.assertEqual(scene3.enter_called, 1)
        self.assertIs(self.gm.current_state, scene3)

    def test_only_top_scene_receives_events(self):
        """Apenas a cena no topo da pilha deve processar handle_events."""
        scene1 = MockScene("play")
        scene2 = MockScene("inventory")

        self.gm.push_state(scene1)
        self.gm.push_state(scene2)

        # Simular envio de evento chamando on_events
        # mockando pygame.event.get
        dummy_event = pygame.event.Event(pygame.USEREVENT)
        orig_get = pygame.event.get
        try:
            pygame.event.get = lambda: [dummy_event]
            self.gm.on_events()
        finally:
            pygame.event.get = orig_get

        self.assertEqual(scene1.events_called, 0, "Cena abaixo não deve receber eventos")
        self.assertEqual(scene2.events_called, 1, "Cena do topo deve receber eventos")

    def test_update_blocks_update_behavior(self):
        """Se cena do topo tiver blocks_update=True, apenas ela atualiza."""
        scene1 = MockScene("play", blocks_update=True)
        scene2 = MockScene("pause", blocks_update=True)

        self.gm.push_state(scene1)
        self.gm.push_state(scene2)

        self.gm.update(0.016)

        self.assertEqual(scene1.update_called, 0, "Cena abaixo não deve ser atualizada com blocks_update=True")
        self.assertEqual(scene2.update_called, 1, "Cena do topo deve ser atualizada")

    def test_update_non_blocking_behavior(self):
        """Se cena do topo tiver blocks_update=False, cena inferior também atualiza."""
        scene1 = MockScene("play", blocks_update=True)
        scene2 = MockScene("hud_overlay", blocks_update=False)

        self.gm.push_state(scene1)
        self.gm.push_state(scene2)

        self.gm.update(0.016)

        self.assertEqual(scene1.update_called, 1, "Cena abaixo deve atualizar se topo não bloqueia")
        self.assertEqual(scene2.update_called, 1, "Cena do topo deve atualizar")

    def test_render_cascade_transparent(self):
        """Se o topo for transparente, a cena de baixo também deve ser desenhada."""
        scene1 = MockScene("play", is_transparent=False)
        scene2 = MockScene("inventory", is_transparent=True)

        self.gm.push_state(scene1)
        self.gm.push_state(scene2)

        # Evita flip real com display do pygame em ambiente headless
        orig_flip = pygame.display.flip
        try:
            pygame.display.flip = lambda: None
            self.gm.on_render()
        finally:
            pygame.display.flip = orig_flip

        self.assertEqual(scene1.draw_called, 1, "Cena inferior deve ser desenhada por causa de is_transparent=True")
        self.assertEqual(scene2.draw_called, 1, "Cena superior deve ser desenhada")

    def test_render_opaque_skips_lower_scenes(self):
        """Se o topo for opaco (is_transparent=False), cenas de baixo não são desenhadas."""
        scene1 = MockScene("play", is_transparent=False)
        scene2 = MockScene("menu", is_transparent=False)

        self.gm.push_state(scene1)
        self.gm.push_state(scene2)

        orig_flip = pygame.display.flip
        try:
            pygame.display.flip = lambda: None
            self.gm.on_render()
        finally:
            pygame.display.flip = orig_flip

        self.assertEqual(scene1.draw_called, 0, "Cena inferior opaca não deve ser desenhada")
        self.assertEqual(scene2.draw_called, 1, "Cena do topo deve ser desenhada")


if __name__ == "__main__":
    unittest.main()

