import json
from pathlib import Path


class MemoryManager:
    def __init__(self, history_file: str | Path | None = None):
        self.history_file = Path(history_file) if history_file else Path(__file__).resolve().parents[1] / "config" / "history.json"
        self.history = self._load_history()

    def _load_history(self) -> list[dict]:
        try:
            if self.history_file.exists():
                return json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:
            pass
        return []

    def _save_history(self) -> None:
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text(json.dumps(self.history, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def store(self, task: dict, result):
        entry = {
            "task": task,
            "result": result,
        }
        self.history.append(entry)
        self._save_history()
        return entry

    def get_history(self) -> list[dict]:
        return list(self.history)
