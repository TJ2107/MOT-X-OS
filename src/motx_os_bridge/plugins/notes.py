import json
from datetime import datetime
from pathlib import Path


class NotesPlugin:
    def __init__(self):
        self.notes_file = Path(__file__).resolve().parents[1] / "config" / "notes.json"
        self.notes = self._load_notes()

    def _load_notes(self) -> dict:
        try:
            if self.notes_file.exists():
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_notes(self) -> str:
        try:
            self.notes_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump(self.notes, f, indent=2, ensure_ascii=False)
            return "✅ Notes sauvegardées"
        except Exception as e:
            return f"❌ Erreur sauvegarde : {e}"

    def add_note(self, content: str, title: str | None = None) -> str:
        if not content:
            return "❌ Aucune note à ajouter"

        note_id = datetime.now().strftime("%Y%m%d%H%M%S")
        note_title = title or f"note-{note_id}"
        self.notes[note_id] = {
            "title": note_title,
            "content": content,
            "created": datetime.now().isoformat()
        }
        self._save_notes()
        return f"✅ Note ajoutée : {note_title}"

    def list_notes(self) -> str:
        if not self.notes:
            return "ℹ️ Aucun contenu de notes disponible"

        lines = ["📒 Notes enregistrées :"]
        for note_id, note_data in sorted(self.notes.items()):
            lines.append(f"  - {note_data['title']} ({note_id}): {note_data['content'][:80]}")
        return "\n".join(lines)

    def delete_note(self, title: str) -> str:
        to_remove = [note_id for note_id, note_data in self.notes.items() if note_data["title"] == title]
        if not to_remove:
            return f"❌ Aucune note trouvée avec le titre : {title}"

        for note_id in to_remove:
            del self.notes[note_id]
        self._save_notes()
        return f"✅ Note supprimée : {title}"
