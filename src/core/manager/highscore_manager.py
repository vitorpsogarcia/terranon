import json
import logging
from typing import TypedDict

from core.settings.settings import HIGHSCORES_FILE, SAVES_FOLDER
from core.singleton_meta import SingletonMeta


class ScoreEntry(TypedDict):
    nome: str
    score: int


class HighscoreManager(metaclass=SingletonMeta):
    _logger = logging.getLogger("HighscoreManager")

    def __init__(self):
        self.current_player_name: str = "Player"
        self._ensure_saves_dir()

    @classmethod
    def get_instance(cls) -> "HighscoreManager":
        return cls()

    def _ensure_saves_dir(self):
        try:
            SAVES_FOLDER.mkdir(parents=True, exist_ok=True)
            if not HIGHSCORES_FILE.exists():
                with open(HIGHSCORES_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4, ensure_ascii=False)
        except Exception as e:
            self._logger.error(f"Erro ao criar diretório/arquivo de saves: {e}")

    def load_scores(self) -> list[ScoreEntry]:
        self._ensure_saves_dir()
        try:
            with open(HIGHSCORES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            self._logger.error(f"Erro ao ler {HIGHSCORES_FILE}: {e}")
            return []

    def save_scores(self, scores: list[ScoreEntry]) -> bool:
        self._ensure_saves_dir()
        try:
            with open(HIGHSCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self._logger.error(f"Erro ao salvar {HIGHSCORES_FILE}: {e}")
            return False

    def add_score(self, name: str, score: int) -> list[ScoreEntry]:
        cleaned_name = name.strip() or "Player"
        scores = self.load_scores()
        scores.append({"nome": cleaned_name, "score": int(score)})
        scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.save_scores(scores)
        return scores

    def get_top_scores(self, limit: int = 10) -> list[ScoreEntry]:
        scores = self.load_scores()
        scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        return scores[:limit]
