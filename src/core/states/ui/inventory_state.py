from typing import TYPE_CHECKING
import pygame

from core.manager.economy_manager import EconomyManager
from core.settings.colors import Colors
from core.states.base_state import GameScene
from core.ui.button import Button
from core.ui.panel import UIPanel

if TYPE_CHECKING:
    from core.manager.state_manager import StateManager


class TowerSlot:
    """Representa um item/torre na grade de seleção do inventário."""

    def __init__(
        self,
        name: str,
        cost: int,
        description: str,
        details: str,
        tower_type: str,
    ):
        self.name = name
        self.cost = cost
        self.description = description
        self.details = details
        self.tower_type = tower_type


class InventoryScene(GameScene):
    """Janela modal de inventário e seleção de torres sobreposta ao jogo."""

    def __init__(self, state_manager: "StateManager", screen_size: tuple[int, int]):
        super().__init__(
            state_manager=state_manager,
            screen_size=screen_size,
            is_transparent=True,
            blocks_update=True,
        )

        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.section_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.item_name_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.item_font = pygame.font.SysFont("Arial", 15)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.feedback_font = pygame.font.SysFont("Arial", 16, bold=True)

        self.feedback_message: str = ""
        self.feedback_timer: float = 0.0
        self.selected_tower_idx: int = 0

        # Definição das torres e melhorias disponíveis
        self.slots: list[TowerSlot] = [
            TowerSlot(
                name="Torre Básica (Gatling)",
                cost=50,
                description="Cadência alta e alcance médio.",
                details="Dano: 10 | Alcance: 200 | Taxa: 10 tps",
                tower_type="basic",
            ),
            TowerSlot(
                name="Torre Rápida (Sniper)",
                cost=100,
                description="Disparos precisos de longo alcance.",
                details="Dano: 30 | Alcance: 350 | Taxa: 2 tps",
                tower_type="rapid",
            ),
            TowerSlot(
                name="Torre Pesada (Plasma)",
                cost=150,
                description="Projéteis explosivos de alto impacto.",
                details="Dano: 70 | Alcance: 160 | Taxa: 1.2 tps",
                tower_type="heavy",
            ),
            TowerSlot(
                name="Kit de Reparo da Base",
                cost=75,
                description="Restaura integridade estrutural.",
                details="Efeito: +30 HP para a Base Central",
                tower_type="repair",
            ),
        ]

        # Layout do painel principal
        panel_w = min(860, self.screen_size[0] - 100)
        panel_h = min(560, self.screen_size[1] - 80)
        panel_x = self.screen_size[0] // 2 - panel_w // 2
        panel_y = self.screen_size[1] // 2 - panel_h // 2
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        self.panel = UIPanel(
            rect=self.panel_rect,
            bg_color=Colors.ui.panel,
            border_color=Colors.brand.primary,
            border_width=2,
            border_radius=12,
            title="INVENTÁRIO & ESTRUTURAS DEFENSIVAS",
            title_font=self.title_font,
            title_color=Colors.text.primary,
        )

        # Botão Fechar
        self.btn_close = Button(
            rect=pygame.Rect(panel_x + panel_w - 140, panel_y + 14, 120, 38),
            text="FECHAR",
            font=self.small_font,
            on_click=self._close,
            bg_color=Colors.ui.button_disabled,
            hover_color=Colors.feedback.error,
        )
        self.panel.add_child(self.btn_close)

        # Botões dos Slots
        self.slot_buttons: list[Button] = []
        self._init_slot_buttons()

    def _init_slot_buttons(self):
        grid_start_x = self.panel_rect.x + 30
        grid_start_y = self.panel_rect.y + 150
        card_w = (self.panel_rect.width - 90) // 2
        card_h = 135

        for i, slot in enumerate(self.slots):
            row = i // 2
            col = i % 2
            slot_x = grid_start_x + col * (card_w + 30)
            slot_y = grid_start_y + row * (card_h + 20)

            btn = Button(
                rect=pygame.Rect(slot_x + card_w - 130, slot_y + card_h - 42, 115, 32),
                text="SELECIONAR" if i == 0 else "COMPRAR",
                font=self.small_font,
                on_click=lambda idx=i: self._on_slot_clicked(idx),
                bg_color=Colors.brand.primary,
                hover_color=Colors.ui.button_hover,
            )
            self.slot_buttons.append(btn)
            self.panel.add_child(btn)

    def _close(self):
        self.state_manager.pop()

    def _on_slot_clicked(self, idx: int):
        slot = self.slots[idx]
        economy = EconomyManager()

        if slot.tower_type == "repair":
            if economy.current_points >= slot.cost:
                economy.spend_points(slot.cost)
                self.feedback_message = "Reparo efetuado com sucesso!"
                self.feedback_timer = 2.5
            else:
                self.feedback_message = f"Pontos insuficientes! Necessário {slot.cost} pts."
                self.feedback_timer = 2.5
        else:
            if economy.current_points >= slot.cost:
                self.selected_tower_idx = idx
                self.feedback_message = f"{slot.name} selecionada para posicionamento!"
                self.feedback_timer = 2.5
            else:
                self.feedback_message = f"Pontos insuficientes! Necessário {slot.cost} pts."
                self.feedback_timer = 2.5

        self._update_button_states()

    def _update_button_states(self):
        economy = EconomyManager()
        for i, (btn, slot) in enumerate(zip(self.slot_buttons, self.slots)):
            if slot.tower_type != "repair":
                if i == self.selected_tower_idx:
                    btn.text = "EQUIPADA"
                    btn.bg_color = Colors.feedback.success
                elif economy.current_points >= slot.cost:
                    btn.text = "SELECIONAR"
                    btn.bg_color = Colors.brand.primary
                else:
                    btn.text = "BLOQUEADA"
                    btn.bg_color = Colors.ui.button_disabled
            else:
                if economy.current_points >= slot.cost:
                    btn.text = "COMPRAR"
                    btn.bg_color = Colors.feedback.warning
                else:
                    btn.text = "SEM PONTOS"
                    btn.bg_color = Colors.ui.button_disabled

    def enter(self) -> None:
        self.feedback_message = ""
        self.feedback_timer = 0.0
        self._update_button_states()

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_message = ""

        self.panel.update(dt)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_i):
                    self._close()
                    return

            if self.panel.handle_event(event):
                continue

    def draw(self, surface: pygame.Surface) -> None:
        # Fundo escurecido translúcido cobrindo a partida
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill(Colors.ui.panel_transparent)
        surface.blit(overlay, (0, 0))

        # Painel principal
        self.panel.draw(surface)

        # Linha divisória do cabeçalho
        header_line_y = self.panel_rect.y + 68
        pygame.draw.line(
            surface,
            Colors.ui.border,
            (self.panel_rect.x + 24, header_line_y),
            (self.panel_rect.right - 24, header_line_y),
            width=1,
        )

        # Seção de Economia
        economy = EconomyManager()
        points_text = (
            f"Pontos Disponíveis: {economy.current_points}    |    "
            f"Total Acumulado: {economy.total_points}"
        )
        points_surf = self.section_font.render(points_text, True, Colors.brand.secondary)
        surface.blit(points_surf, (self.panel_rect.x + 30, header_line_y + 12))

        towers_label = self.section_font.render(
            "Selecione uma Defesa para Posicionar:", True, Colors.text.primary
        )
        surface.blit(towers_label, (self.panel_rect.x + 30, header_line_y + 44))

        # Grade de Slots
        grid_start_x = self.panel_rect.x + 30
        grid_start_y = self.panel_rect.y + 150
        card_w = (self.panel_rect.width - 90) // 2
        card_h = 135

        for i, slot in enumerate(self.slots):
            row = i // 2
            col = i % 2
            slot_x = grid_start_x + col * (card_w + 30)
            slot_y = grid_start_y + row * (card_h + 20)
            slot_rect = pygame.Rect(slot_x, slot_y, card_w, card_h)

            is_selected = i == self.selected_tower_idx and slot.tower_type != "repair"
            border_color = (
                Colors.feedback.success if is_selected else Colors.ui.border
            )
            border_width = 2 if is_selected else 1

            pygame.draw.rect(
                surface, Colors.ui.background_light, slot_rect, border_radius=8
            )
            pygame.draw.rect(
                surface, border_color, slot_rect, width=border_width, border_radius=8
            )

            # Título do Item
            name_color = (
                Colors.brand.secondary if is_selected else Colors.text.primary
            )
            name_surf = self.item_name_font.render(slot.name, True, name_color)
            surface.blit(name_surf, (slot_x + 14, slot_y + 12))

            # Custo
            cost_surf = self.item_font.render(
                f"Custo: {slot.cost} pts", True, Colors.feedback.warning
            )
            surface.blit(cost_surf, (slot_x + 14, slot_y + 36))

            # Descrição e Detalhes
            desc_surf = self.item_font.render(
                slot.description, True, Colors.text.secondary
            )
            surface.blit(desc_surf, (slot_x + 14, slot_y + 60))

            details_surf = self.item_font.render(
                slot.details, True, Colors.text.disabled
            )
            surface.blit(details_surf, (slot_x + 14, slot_y + 82))

        # Mensagem de Feedback
        if self.feedback_message:
            fb_surf = self.feedback_font.render(
                self.feedback_message, True, Colors.brand.secondary
            )
            surface.blit(
                fb_surf,
                (
                    self.panel_rect.centerx - fb_surf.get_width() // 2,
                    self.panel_rect.bottom - 60,
                ),
            )

        # Dica de Rodapé
        hint_surf = self.small_font.render(
            "Pressione [ I ] ou [ ESC ] para fechar o inventário e voltar ao combate",
            True,
            Colors.text.disabled,
        )
        surface.blit(
            hint_surf,
            (
                self.panel_rect.centerx - hint_surf.get_width() // 2,
                self.panel_rect.bottom - 28,
            ),
        )


# Alias para retrocompatibilidade
InventoryState = InventoryScene
