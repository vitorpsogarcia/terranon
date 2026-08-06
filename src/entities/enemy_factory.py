from entities.character.goblin import Goblin


class EnemyFactory:

    _registry = {  # noqa: RUF012
        "goblin": Goblin,
    }

    @classmethod
    def create_enemy(self,enemy_type: str, x: float, y: float, path: list):
        enemy_class = EnemyFactory._registry.get(enemy_type)

        if enemy_class is None:
            raise ValueError(f"Inimigo desconhecido: {enemy_type}")

        return enemy_class(x, y, path=path)
