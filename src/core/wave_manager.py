# src/core/wave_manager.py
from core.enums.enemy_enum import EnemyEnum
from core.enums.enemy_spawner_enum import EnemySpawnerEnum


class WaveManager:
    def __init__(self, spawners_dict):
        self.spawners = spawners_dict
        self.wave_timer = 0.0
        self.current_event_index = 0
        self.pending_spawns = []   
        self.spawn_delay = 0.5
        self.current_delay_timer = 0.0

        self.current_wave_script = [
            {"time": 5.0, "spawner": EnemySpawnerEnum.SPWN_GAMA.value, "enemy": EnemyEnum.GOBLIN, "qtd": 3},
            {"time": 15.0, "spawner": EnemySpawnerEnum.SPWN_DELTA.value, "enemy": EnemyEnum.GOBLIN, "qtd": 5}
        ]
        
        self.current_wave_script.sort(key=lambda x: x["time"])

    def update(self, dt: float):
        # 1. PROCESSA A FILA DE SPAWN (Loop com delay)
        if self.pending_spawns:
            self.current_delay_timer += dt
            if self.current_delay_timer >= self.spawn_delay:
                spawn_task = self.pending_spawns.pop(0)
                spawner_id = spawn_task["spawner"]
                enemy_type = spawn_task["enemy"]
                
                if spawner_id in self.spawners:
                    self.spawners[spawner_id].spawn_enemy(enemy_type)
                else:
                    print(f"Aviso: Ninho {spawner_id} não encontrado no mapa!")
                
                self.current_delay_timer = 0.0

        if self.current_event_index < len(self.current_wave_script):
            self.wave_timer += dt
            next_event = self.current_wave_script[self.current_event_index]
            
            if self.wave_timer >= next_event["time"]:
                qtd = next_event["qtd"]
                
                for _ in range(qtd):
                    self.pending_spawns.append({
                        "spawner": next_event["spawner"],
                        "enemy": next_event["enemy"]
                    })
                
                self.current_event_index += 1
                self.current_event_index += 1