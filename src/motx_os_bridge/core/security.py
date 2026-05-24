from pathlib import Path

from ..utils.config_loader import load_settings


class SecurityManager:
    def __init__(self):
        settings = load_settings()
        self.security_settings = settings.get("security", {}) if isinstance(settings, dict) else {}
        self.allowed_paths = [Path(p).expanduser().resolve() for p in self.security_settings.get("allowed_paths", []) if isinstance(p, str)]
        self.blocked_paths = [Path(p).expanduser().resolve() for p in self.security_settings.get("blocked_paths", []) if isinstance(p, str)]

    def validate(self, task: dict) -> tuple[bool, str | None, bool]:
        task_type = task.get("type")

        if task_type == "DELETE_SYSTEM_FILE":
            return False, "Action interdite : suppression de fichiers système", False

        sensitive_tasks = {
            "FILE_DELETE",
            "FILE_MOVE",
            "FILE_RENAME",
            "RESTART_PC",
            "SHUTDOWN_PC",
            "EXECUTE_POWERSHELL",
            "EXECUTE_BATCH",
            "EXECUTE_PYTHON",
        }
        if task_type in sensitive_tasks and self.security_settings.get("require_confirmation", False):
            return False, "Confirmation requise pour action sensible", True

        if not self.security_settings.get("allow_root_actions", False):
            for path_key in ("path", "source", "destination", "target", "script"):
                path_value = task.get(path_key)
                if path_value and isinstance(path_value, str):
                    if self._is_blocked_path(path_value):
                        return False, f"Chemin bloqué : {path_value}", False

        return True, None, False

    def _is_blocked_path(self, path_value: str) -> bool:
        try:
            path = Path(path_value).expanduser().resolve()
        except Exception:
            return False

        for allowed in self.allowed_paths:
            if allowed == path or allowed in path.parents:
                return False

        for blocked in self.blocked_paths:
            if blocked == path or blocked in path.parents:
                return True

        blocked_roots = [
            Path("C:/Windows"),
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
            Path("C:/System Volume Information"),
        ]
        if Path("/").exists():
            blocked_roots.append(Path("/"))

        for root in blocked_roots:
            if root and (root == path or root in path.parents):
                return True

        return False
