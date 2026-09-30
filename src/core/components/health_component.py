from collections.abc import Callable

from core.component import Component
from core.components.shield_component import ShieldComponent


class HealthComponent(Component):
    def __init__(
        self,
        max_hp: float,
        on_death_callback: Callable[[], None] | None = None,
        iframes_duration: float = 0.5,
        allow_invulnerability: bool = False,
        damage_reduction: float = 0.0,
        max_damage_reduction: float = 0.75,
        shield: ShieldComponent | None = None,
        owner: object | None = None,
    ):
        self.owner = owner
        self.max_hp = max_hp
        self.current_hp = max_hp

        self.is_invulnerable = False
        self.invulnerability_timer = 0.0
        self.allow_invulnerability = allow_invulnerability
        self.iframes_duration = iframes_duration

        self.is_dead = False
        self.on_death_callback = on_death_callback

        self.damage_reduction = damage_reduction
        self.max_damage_reduction = max_damage_reduction
        self.shield = shield

    def take_damage(self, amount: float):
        if self.is_dead or self.is_invulnerable or amount <= 0:
            return

        effective_reduction = min(self.damage_reduction, self.max_damage_reduction)
        mitigated_damage = amount * (1.0 - effective_reduction)

        owner = getattr(self, "owner", None)
        render_comp = getattr(owner, "render_component", None) if owner else None
        animator_comp = getattr(owner, "animator", None) if owner else None
        if render_comp and hasattr(render_comp, "trigger_flash"):
            render_comp.trigger_flash()
        elif animator_comp and hasattr(animator_comp, "trigger_flash"):
            animator_comp.trigger_flash()

        owner_name = owner.__class__.__name__ if owner else ""
        is_player_or_base = (
            "player" in owner_name.lower()
            or "mainbase" in owner_name.lower()
            or self.allow_invulnerability
        )
        if is_player_or_base:
            try:
                from core.enums.game_event_enum import GameEventEnum
                from core.manager.event_manager import EventManager

                shake_intensity = 10.0 if "mainbase" in owner_name.lower() else 7.0
                EventManager().emit(
                    GameEventEnum.SCREEN_SHAKE,
                    {"intensity": shake_intensity, "duration": 0.25},
                )
            except Exception:
                pass

        remaning_damage = mitigated_damage
        if self.shield and self.shield.is_active and self.shield.current_shield > 0:
            if self.shield.current_shield >= remaning_damage:
                self.shield.current_shield -= remaning_damage
                remaning_damage = 0.0
            else: 
                remaning_damage -= self.shield.current_shield
                self.shield.current_shield = 0.0

        if remaning_damage > 0:
            self.current_hp -= remaning_damage

        if self.current_hp <= 0:
            self.current_hp = 0
            self.die()
        elif self.allow_invulnerability:
            self.is_invulnerable = True
            self.invulnerability_timer = self.iframes_duration

    def heal(self, amount: float):
        if self.is_dead or amount <= 0:
            return

        self.current_hp += amount
        self.current_hp = min(self.current_hp, self.max_hp)

    def update(self, dt: float):
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                self.invulnerability_timer = 0.0

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            if self.on_death_callback:
                self.on_death_callback()
