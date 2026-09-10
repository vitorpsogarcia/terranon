import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.ui import Button, Panel, TextInput, UIElement, UIPanel


class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.font = pygame.font.SysFont("Arial", 16)
        self.surface = pygame.Surface((800, 600))

    # --- UIElement tests ---
    def test_ui_element_is_abstract(self):
        with self.assertRaises(TypeError):
            UIElement(pygame.Rect(0, 0, 10, 10))

    # --- Button tests ---
    def test_button_hover(self):
        rect = pygame.Rect(10, 10, 100, 40)
        btn = Button(rect, "Test", self.font)

        # Mouse fora
        motion_outside = pygame.event.Event(pygame.MOUSEMOTION, pos=(200, 200))
        btn.handle_event(motion_outside)
        self.assertFalse(btn.is_hovered)

        # Mouse dentro
        motion_inside = pygame.event.Event(pygame.MOUSEMOTION, pos=(50, 25))
        btn.handle_event(motion_inside)
        self.assertTrue(btn.is_hovered)

    def test_button_click_triggers_callback(self):
        clicked = False

        def on_click():
            nonlocal clicked
            clicked = True

        rect = pygame.Rect(10, 10, 100, 40)
        btn = Button(rect, "Test", self.font, on_click=on_click)

        # Clique fora
        click_outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 200))
        result = btn.handle_event(click_outside)
        self.assertFalse(result)
        self.assertFalse(clicked)

        # Clique dentro
        click_inside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 25))
        result = btn.handle_event(click_inside)
        self.assertTrue(result)
        self.assertTrue(clicked)

    def test_disabled_button_ignores_events(self):
        clicked = False

        def on_click():
            nonlocal clicked
            clicked = True

        rect = pygame.Rect(10, 10, 100, 40)
        btn = Button(rect, "Test", self.font, on_click=on_click)
        btn.enabled = False

        click_inside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 25))
        result = btn.handle_event(click_inside)
        self.assertFalse(result)
        self.assertFalse(clicked)

    def test_button_draw(self):
        rect = pygame.Rect(10, 10, 100, 40)
        btn = Button(rect, "Test", self.font)
        btn.draw(self.surface)

    # --- TextInput tests ---
    def test_text_input_typing_and_backspace(self):
        rect = pygame.Rect(10, 10, 200, 35)
        text_input = TextInput(rect, self.font, max_length=5)
        text_input.is_active = True

        # Digitar "A"
        event_a = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode="A")
        text_input.handle_event(event_a)
        self.assertEqual(text_input.text, "A")

        # Digitar "B"
        event_b = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b, unicode="B")
        text_input.handle_event(event_b)
        self.assertEqual(text_input.text, "AB")

        # Backspace
        event_back = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode="")
        text_input.handle_event(event_back)
        self.assertEqual(text_input.text, "A")

    def test_text_input_max_length(self):
        rect = pygame.Rect(10, 10, 200, 35)
        text_input = TextInput(rect, self.font, max_length=3)
        text_input.is_active = True

        for char in "ABCD":
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode=char)
            text_input.handle_event(event)

        # Deve limitar em 3 caracteres
        self.assertEqual(text_input.text, "ABC")

    def test_text_input_submit(self):
        submitted_text = ""

        def on_submit(val):
            nonlocal submitted_text
            submitted_text = val

        rect = pygame.Rect(10, 10, 200, 35)
        text_input = TextInput(rect, self.font, on_submit=on_submit)
        text_input.is_active = True
        text_input.text = "Hero"

        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r")
        handled = text_input.handle_event(enter_event)
        self.assertTrue(handled)
        self.assertEqual(submitted_text, "Hero")

    def test_text_input_cursor_blink(self):
        rect = pygame.Rect(10, 10, 200, 35)
        text_input = TextInput(rect, self.font)
        text_input.is_active = True
        self.assertTrue(text_input.cursor_visible)

        # Simular passagem de 0.6s
        text_input.update(0.6)
        self.assertFalse(text_input.cursor_visible)

        text_input.update(0.6)
        self.assertTrue(text_input.cursor_visible)

    def test_text_input_draw(self):
        rect = pygame.Rect(10, 10, 200, 35)
        text_input = TextInput(rect, self.font, placeholder="Nome")
        text_input.draw(self.surface)

    # --- UIPanel tests ---
    def test_panel_children_management(self):
        panel = UIPanel(pygame.Rect(50, 50, 400, 300))
        btn = Button(pygame.Rect(60, 60, 100, 40), "Btn", self.font)

        panel.add_child(btn)
        self.assertEqual(len(panel.children), 1)
        self.assertIn(btn, panel.children)

        panel.remove_child(btn)
        self.assertEqual(len(panel.children), 0)

        panel.add_child(btn)
        panel.clear_children()
        self.assertEqual(len(panel.children), 0)

    def test_panel_delegates_event_to_children(self):
        clicked = False

        def on_click():
            nonlocal clicked
            clicked = True

        panel = UIPanel(pygame.Rect(50, 50, 400, 300))
        btn = Button(pygame.Rect(60, 60, 100, 40), "Btn", self.font, on_click=on_click)
        panel.add_child(btn)

        # Clicar dentro do botão que está dentro do painel
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(80, 80))
        handled = panel.handle_event(event)
        self.assertTrue(handled)
        self.assertTrue(clicked)

    def test_panel_consumes_internal_click(self):
        panel = UIPanel(pygame.Rect(50, 50, 400, 300), consume_clicks=True)
        # Clicar no painel, mas fora de qualquer botão filho
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 200))
        handled = panel.handle_event(event)
        self.assertTrue(handled, "Painel deve consumir clique dentro de sua área para não vazar")

        # Clicar fora do painel
        event_outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
        handled_outside = panel.handle_event(event_outside)
        self.assertFalse(handled_outside, "Painel não deve consumir clique fora de sua área")

    def test_panel_update_and_draw(self):
        panel = UIPanel(
            pygame.Rect(50, 50, 400, 300),
            bg_color=(31, 41, 55, 200),
            title="Painel Teste",
            title_font=self.font,
        )
        text_input = TextInput(pygame.Rect(70, 100, 200, 35), self.font)
        btn = Button(pygame.Rect(70, 150, 100, 40), "OK", self.font)
        panel.add_child(text_input)
        panel.add_child(btn)

        panel.update(0.1)
        panel.draw(self.surface)

    def test_panel_alias(self):
        self.assertIs(Panel, UIPanel)


if __name__ == "__main__":
    unittest.main()
