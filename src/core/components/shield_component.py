from core.component import Component


class ShieldComponent(Component):
    def __init__(self, max_shield: float = 10.0, current_shield: float | None = None, is_active: bool = False):
        self.max_shield = max_shield
        self.current_shield = max_shield if current_shield is None else current_shield
        self.is_active = is_active

    def unlock(self, initial_shield: float = 10.0, max_shield: float = 10.0):
        self.max_shield = max_shield
        self.current_shield = initial_shield
        self.is_active = True

    def recharge(self, amount: float):
        if not self.is_active or amount <= 0:
            return

        self.current_shield = min(self.max_shield, self.current_shield + amount)