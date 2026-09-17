import pygame

from core.manager.economy_manager import EconomyManager
from core.manager.upgrade_manager import UpgradeManager
from core.settings.colors import Colors
from core.states.base_state import BaseState
from core.upgrades.upgrades import GameContext, Upgrade


class UpgradeSelectionUI(BaseState):
    def __init__(self, state_manager, screen_size: tuple[int, int]):
        super().__init__(state_manager, screen_size)
        self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_card_title = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_card_desc = pygame.font.SysFont("Arial", 16)
        self.font_shortcut = pygame.font.SysFont("Arial", 20, bold=True)
        self.upgrades: list[Upgrade] = []
        self.card_rects: list[pygame.Rect] = []

    def enter(self):
        play_state = None
        for state in self.state_manager.game_manager.state_stack:
            if hasattr(state, "player") and hasattr(state, "wave_manager"):
                play_state = state
                break

        if play_state and play_state.player:
            context = GameContext(
                wave_manager=play_state.wave_manager,
                economy_manager=EconomyManager(),
            )
            self.play_state = play_state
            self.context = context
            self.upgrades = UpgradeManager().get_random_upgrades(3, play_state.player, context)
        else:
            self.upgrades = []

        self._setup_card_rects()

    def _setup_card_rects(self):
        card_w, card_h = 280, 360
        gap = 40
        total_w = 3 * card_w + 2 * gap
        start_x = (self.screen_size[0] - total_w) // 2
        start_y = (self.screen_size[1] - card_h) // 2 + 30

        self.card_rects = [
            pygame.Rect(start_x + i * (card_w + gap), start_y, card_w, card_h)
            for i in range(len(self.upgrades))
        ]

    def _select(self, index: int):
        if 0 <= index < len(self.upgrades):
            chosen = self.upgrades[index]
            UpgradeManager().select_upgrade(chosen, self.play_state.player, self.context)
            if self.play_state.wave_manager:
                self.play_state.wave_manager.start_next_wave()
            self.state_manager.pop()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self._select(0)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self._select(1)
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self._select(2)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for i, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mouse_pos):
                        self._select(i)
                        break

    def update(self, delta_time):
        pass 

    def draw(self, surface: pygame.Surface):
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 200))
        surface.blit(overlay, (0, 0))

        title_surf = self.font_title.render("ESCOLHA UMA MELHORIA", True, Colors.brand.secondary)
        surface.blit(title_surf, (self.screen_size[0] // 2 - title_surf.get_width() // 2, 80))

        mouse_pos = pygame.mouse.get_pos()
        for i, (upgrade, rect) in enumerate(zip(self.upgrades, self.card_rects)):
            is_hovered = rect.collidepoint(mouse_pos)
            
            bg_color = Colors.ui.background_light if is_hovered else Colors.ui.panel
            pygame.draw.rect(surface, bg_color, rect, border_radius=12)
            
            border_color = Colors.brand.primary if is_hovered else Colors.ui.border
            border_width = 3 if is_hovered else 1
            pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=12)

            badge_surf = self.font_shortcut.render(f"[{i + 1}]", True, Colors.brand.secondary)
            surface.blit(badge_surf, (rect.centerx - badge_surf.get_width() // 2, rect.top + 20))

            card_title = self.font_card_title.render(upgrade.title, True, Colors.text.primary)
            surface.blit(card_title, (rect.centerx - card_title.get_width() // 2, rect.top + 60))

            words = upgrade.description.split(" ")
            lines = []
            curr_line = ""
            for word in words:
                test_line = f"{curr_line} {word}".strip()
                if self.font_card_desc.size(test_line)[0] < rect.width - 30:
                    curr_line = test_line
                else:
                    lines.append(curr_line)
                    curr_line = word
            if curr_line:
                lines.append(curr_line)

            y_text = rect.top + 120
            for line in lines:
                line_surf = self.font_card_desc.render(line, True, Colors.text.secondary)
                surface.blit(line_surf, (rect.centerx - line_surf.get_width() // 2, y_text))
                y_text += 22

    def exit(self):
        self.upgrades.clear()
        self.card_rects.clear()