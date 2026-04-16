from typing import Callable, Optional

class HealthComponent:
    def __init__(
        self, 
        max_hp: float, 
        on_death_callback: Optional[Callable[[], None]] = None,
        iframes_duration: float = 0.5
    ):
        self.max_hp = max_hp
        self.current_hp = max_hp
        
        self.is_invulnerable = False
        self.invulnerability_timer = 0.0
        self.iframes_duration = iframes_duration
        
        self.is_dead = False
        self.on_death_callback = on_death_callback

    def take_damage(self, amount: float):
        if self.is_dead or self.is_invulnerable or amount <= 0:
            return

        self.current_hp -= amount
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.die()
        else:
            self.is_invulnerable = True
            self.invulnerability_timer = self.iframes_duration

    def heal(self, amount: float):
        if self.is_dead or amount <= 0:
            return
            
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
    
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