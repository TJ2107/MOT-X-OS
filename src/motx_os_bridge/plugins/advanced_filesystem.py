import shutil
import os


class AdvancedFileSystemPlugin:
    def copy_file(self, source: str, destination: str) -> str:
        try:
            shutil.copy2(source, destination)
            return f"✅ Fichier copié : {source} → {destination}"
        except Exception as e:
            return f"❌ Erreur copie : {e}"

    def move_file(self, source: str, destination: str) -> str:
        try:
            shutil.move(source, destination)
            return f"✅ Fichier déplacé : {source} → {destination}"
        except Exception as e:
            return f"❌ Erreur déplacement : {e}"

    def rename_file(self, source: str, new_name: str) -> str:
        try:
            os.rename(source, new_name)
            return f"✅ Fichier renommé : {source} → {new_name}"
        except Exception as e:
            return f"❌ Erreur renaming : {e}"

    def delete_file(self, file_path: str, confirm: bool = True) -> str:
        if not confirm:
            return "❌ Suppression refusée (confirmation requise)"
        try:
            os.remove(file_path)
            return f"✅ Fichier supprimé : {file_path}"
        except Exception as e:
            return f"❌ Erreur suppression : {e}"

    def list_files(self, directory: str) -> str:
        try:
            files = os.listdir(directory)
            return f"📁 Contenu de {directory}:\n" + "\n".join(f"  - {f}" for f in files[:20])
        except Exception as e:
            return f"❌ Erreur listing : {e}"

    def compress_files(self, source: str, destination: str) -> str:
        try:
            shutil.make_archive(destination, "zip", source)
            return f"✅ Fichiers compressés : {destination}.zip"
        except Exception as e:
            return f"❌ Erreur compression : {e}"
