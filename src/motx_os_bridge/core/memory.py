import json
from datetime import datetime, timedelta, timezone
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.history.append(entry)
        self._save_history()
        return entry

    def purge_old_entries(self, max_age_days: int = 7) -> int:
        """Supprime les entrées plus vieilles que max_age_days jours.
        Retourne le nombre d'entrées supprimées."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        before = len(self.history)
        self.history = [
            entry for entry in self.history
            if self._entry_timestamp(entry) >= cutoff
        ]
        removed = before - len(self.history)
        if removed > 0:
            self._save_history()
        return removed

    def _entry_timestamp(self, entry: dict) -> datetime:
        """Extrait le timestamp d'une entrée, retourne epoch si absent (ancienne entrée sans timestamp)."""
        ts = entry.get("timestamp")
        if ts:
            try:
                return datetime.fromisoformat(ts)
            except ValueError:
                pass
        # Ancienne entrée sans timestamp : on la considère expirée immédiatement
        return datetime.min.replace(tzinfo=timezone.utc)

    def get_history(self) -> list[dict]:
        return list(self.history)

