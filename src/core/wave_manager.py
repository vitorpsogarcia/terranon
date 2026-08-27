# src/core/wave_manager.py
from core.enums.enemy_enum import EnemyEnum
from core.enums.enemy_spawner_enum import EnemySpawnerEnum
from core.enums.game_event_enum import GameEventEnum
from core.manager.event_manager import EventManager


class WaveManager:
    def __init__(self, spawners_dict):
        self.spawners = spawners_dict
        self.wave_timer = 0.0
        self.current_event_index = 0
        self.active_batches = []
        self.spawn_delay = 0.5
        self.current_delay_timer = 0.0

        self.current_wave_script = [
            {"time": 1.0, "spawner": EnemySpawnerEnum.SPWN_ALPHA.value,
                "enemy": EnemyEnum.GOBLIN, "qtd": 10},
            {"time": 2.0, "spawner": EnemySpawnerEnum.SPWN_GAMA.value,
                "enemy": EnemyEnum.GOBLIN, "qtd": 10},
            {"time": 1.0, "spawner": EnemySpawnerEnum.SPWN_BETA.value,
                "enemy": EnemyEnum.GOBLIN, "qtd": 10},
            {"time": 2.0, "spawner": EnemySpawnerEnum.SPWN_DELTA.value,
                "enemy": EnemyEnum.GOBLIN, "qtd": 10}
        ]


        self.current_wave_script.sort(key=lambda x: x["time"])
        EventManager.get_instance().subscribe(
            event=GameEventEnum.RESET_WAVES, listener=self.reset
        )

    def update(self, dt: float):
        if self.active_batches:
            self.current_delay_timer += dt
            if self.current_delay_timer >= self.spawn_delay:

                for batch in self.active_batches[:]:
                    spawner_id = batch["spawner"]
                    enemy_type = batch["enemy"]

                    if spawner_id in self.spawners:
                        self.spawners[spawner_id].spawn_enemy(enemy_type)
                    else:
                        print(
                            f"Aviso: Ninho {spawner_id} não encontrado no mapa!")

                    batch["remaining"] -= 1

                    if batch["remaining"] <= 0:
                        self.active_batches.remove(batch)

                self.current_delay_timer = 0.0

        self.wave_timer += dt

        while self.current_event_index < len(self.current_wave_script):
            next_event = self.current_wave_script[self.current_event_index]


            if self.wave_timer >= next_event["time"]:
                self.active_batches.append({
                    "spawner": next_event["spawner"],
                    "enemy": next_event["enemy"],
                    "remaining": next_event["qtd"]
                })

                self.current_event_index += 1
            else:
                break

    def reset(self):
        self.wave_timer = 0.0
        self.current_event_index = 0
        self.active_batches.clear()
