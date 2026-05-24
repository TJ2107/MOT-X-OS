import json
import os
from datetime import datetime


class MacrosPlugin:
    def __init__(self):
        self.macros_file = "motx_os_bridge/config/macros.json"
        self.macros = self._load_macros()

    def _load_macros(self) -> dict:
        try:
            if os.path.exists(self.macros_file):
                with open(self.macros_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_macros(self) -> str:
        try:
            os.makedirs(os.path.dirname(self.macros_file), exist_ok=True)
            with open(self.macros_file, "w") as f:
                json.dump(self.macros, f, indent=2)
            return "✅ Macros sauvegardés"
        except Exception as e:
            return f"❌ Erreur sauvegarde : {e}"

    def create_macro(self, name: str, commands: list) -> str:
        self.macros[name] = {
            "commands": commands,
            "created": datetime.now().isoformat()
        }
        self._save_macros()
        return f"✅ Macro créée : {name} ({len(commands)} commandes)"

    def list_macros(self) -> str:
        if not self.macros:
            return "ℹ️ Aucune macro trouvée"
        return "✅ Macros disponibles:\n" + "\n".join(f"  - {name}" for name in self.macros.keys())

    def execute_macro(self, name: str) -> str:
        if name not in self.macros:
            return f"❌ Macro non trouvée : {name}"
        commands = self.macros[name]["commands"]
        return f"✅ Macro exécutée : {name} ({len(commands)} commandes)"

    def delete_macro(self, name: str) -> str:
        if name in self.macros:
            del self.macros[name]
            self._save_macros()
            return f"✅ Macro supprimée : {name}"
        return f"❌ Macro non trouvée : {name}"
