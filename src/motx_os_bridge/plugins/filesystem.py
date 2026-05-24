import os


class FileSystemPlugin:
    def create_folder(self, target: str) -> str:
        path = os.path.abspath(target)
        try:
            os.makedirs(path, exist_ok=True)
            return f"Dossier créé ou déjà existant : {path}"
        except OSError as exc:
            return f"Erreur de création du dossier : {exc}"

    def list_folder(self, target: str) -> list[str]:
        path = os.path.abspath(target)
        try:
            return os.listdir(path)
        except OSError:
            return []
