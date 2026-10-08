import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.enums.game_state_enum import GameStateEnum
from core.states.base_state import GameScene
from core.states.intro_cutscene_scene import IntroCutsceneScene


class MockStateManager:
    def __init__(self):
        self.current_state = None
        self.state_factories = {}

    def change_to(self, state_name):
        self.current_state = state_name


class TestIntroCutscene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        cls.surface = pygame.Surface((1056, 720))

    def setUp(self):
        self.sm = MockStateManager()
        self.intro = IntroCutsceneScene(self.sm, (1056, 720))

    def test_inheritance(self):
        self.assertTrue(issubclass(IntroCutsceneScene, GameScene))

    def test_enter_initializes_state(self):
        self.intro.enter()
        self.assertEqual(self.intro.time, 0.0)
        self.assertFalse(self.intro._started)

    def test_update_and_draw_all_phases(self):
        self.intro.enter()

        # Phase 1: Space descent
        self.intro.update(1.0)
        self.assertEqual(self.intro.time, 1.0)
        self.intro.draw(self.surface)

        # Phase 2: Atmospheric reentry
        self.intro.update(3.0)
        self.assertEqual(self.intro.time, 4.0)
        self.intro.draw(self.surface)

        # Phase 3: Impact at 6.5s
        self.intro.update(3.0)
        self.assertEqual(self.intro.time, 7.0)
        self.assertGreater(self.intro.flash_timer, 0.0)
        self.intro.draw(self.surface)

        # Phase 4: Survivor and enemies
        self.intro.update(3.0)
        self.assertEqual(self.intro.time, 10.0)
        self.intro.draw(self.surface)

    def test_skip_with_space_key(self):
        self.intro.enter()
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.intro.handle_events([space_event])
        self.assertEqual(self.sm.current_state, GameStateEnum.PLAY)

    def test_skip_with_mouse_click(self):
        self.intro.enter()
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
        self.intro.handle_events([click_event])
        self.assertEqual(self.sm.current_state, GameStateEnum.PLAY)

    def test_auto_transition_on_completion(self):
        self.intro.enter()
        self.intro.update(self.intro.total_duration + 0.1)
        self.assertEqual(self.sm.current_state, GameStateEnum.PLAY)


if __name__ == "__main__":
    unittest.main()
