import asyncio
import subprocess
import sys
from ..plugins.filesystem import FileSystemPlugin
from ..plugins.advanced_filesystem import AdvancedFileSystemPlugin
from ..plugins.monitor import MonitorPlugin
from ..plugins.scripts import ScriptsPlugin
from ..plugins.system_info import SystemInfoPlugin
from ..plugins.web import WebPlugin
from ..plugins.communication import CommunicationPlugin
from ..plugins.macros import MacrosPlugin
from ..plugins.notes import NotesPlugin
from ..plugins.translation import TranslationPlugin
from ..plugins.llm import LLMPlugin


class TaskExecutor:
    def __init__(self):
        self.fs = FileSystemPlugin()
        self.adv_fs = AdvancedFileSystemPlugin()
        self.monitor = MonitorPlugin()
        self.scripts = ScriptsPlugin()
        self.system = SystemInfoPlugin()
        self.web = WebPlugin()
        self.comms = CommunicationPlugin()
        self.macros = MacrosPlugin()
        self.notes = NotesPlugin()
        self.translation = TranslationPlugin()
        self.llm = LLMPlugin()

    async def execute(self, task: dict):
        task_type = task.get("type")

        # Original features
        if task_type == "OPEN_APP":
            return await self.open_application(task.get("target"))
        if task_type == "CREATE_FOLDER":
            return self.fs.create_folder(task.get("target"))
        if task_type == "MONITOR_CPU":
            return await self.monitor.monitor_cpu()

        # File operations
        if task_type == "FILE_COPY":
            return self.adv_fs.copy_file(task.get("source"), task.get("destination"))
        if task_type == "FILE_MOVE":
            return self.adv_fs.move_file(task.get("source"), task.get("destination"))
        if task_type == "FILE_RENAME":
            return self.adv_fs.rename_file(task.get("source"), task.get("new_name"))
        if task_type == "FILE_DELETE":
            return self.adv_fs.delete_file(task.get("path"), confirm=True)
        if task_type == "FILE_LIST":
            return self.adv_fs.list_files(task.get("directory"))
        if task_type == "FILE_COMPRESS":
            return self.adv_fs.compress_files(task.get("source"), task.get("destination"))

        # Script execution
        if task_type == "EXECUTE_PYTHON":
            return self.scripts.execute_python(task.get("script"))
        if task_type == "EXECUTE_POWERSHELL":
            return self.scripts.execute_powershell(task.get("command"))
        if task_type == "EXECUTE_BATCH":
            return self.scripts.execute_batch(task.get("script"))

        # System info
        if task_type == "SYSTEM_INFO":
            return self.system.get_system_info()
        if task_type == "RESTART_PC":
            return self.system.restart_pc(task.get("delay", 60))
        if task_type == "SHUTDOWN_PC":
            return self.system.shutdown_pc(task.get("delay", 60))

        # Web operations
        if task_type == "OPEN_URL":
            return self.web.open_url(task.get("url"))
        if task_type == "SEARCH_GOOGLE":
            return self.web.search_google(task.get("query"))
        if task_type == "SEARCH_BING":
            return self.web.search_bing(task.get("query"))
        if task_type == "DOWNLOAD_FILE":
            return self.web.download_file(task.get("url"), task.get("destination", "download"))

        # Communication
        if task_type == "SEND_EMAIL":
            return self.comms.send_email(task.get("to"), task.get("subject"), task.get("body"))
        if task_type == "SEND_NOTIFICATION":
            return self.comms.send_notification(task.get("title", "Notification"), task.get("message", ""))
        if task_type == "PLAY_SOUND":
            return self.comms.play_sound(task.get("sound_type", "default"))

        # Notes
        if task_type == "CREATE_NOTE":
            return self.notes.add_note(task.get("content"), task.get("title"))
        if task_type == "LIST_NOTES":
            return self.notes.list_notes()
        if task_type == "DELETE_NOTE":
            return self.notes.delete_note(task.get("title"))

        # Macros
        if task_type == "CREATE_MACRO":
            return self.macros.create_macro(task.get("name"), task.get("commands", []))
        if task_type == "EXECUTE_MACRO":
            return self.macros.execute_macro(task.get("name"))
        if task_type == "LIST_MACROS":
            return self.macros.list_macros()

        # Traduction
        if task_type == "TRANSLATE_TO_FRENCH":
            return self.translation.translate_to_french(task.get("text"))

        # LLM
        if task_type == "LLM_GENERATE":
            return self.llm.generate(task.get("prompt", ""), task.get("max_tokens", 200))
        if task_type == "LLM_TRANSLATE":
            return self.llm.translate_en_to_fr(task.get("text", ""))

        return f"⚠️ Type de tâche non supporté: {task_type}"

    async def open_application(self, target: str) -> str:
        if not target:
            return "❌ Aucune cible d'application fournie"

        try:
            if sys.platform == "win32":
                subprocess.Popen(target)
            else:
                subprocess.Popen([target])
            return f"✅ Application lancée: {target}"
        except FileNotFoundError:
            return f"⚠️ Application introuvable: {target}"
        except Exception as e:
            return f"⚠️ Erreur lancement {target}: {e}"
