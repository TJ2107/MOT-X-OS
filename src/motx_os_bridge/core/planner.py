import ast
import json
import re

from ..utils.llm_client import LocalLLMClient


class TaskPlanner:
    def __init__(self):
        self.llm_client = LocalLLMClient()
        self.enable_llm_planning = True

    def build_plan(self, instruction: str) -> list[dict]:
        if self.enable_llm_planning:
            llm_tasks = self._build_plan_with_llm(instruction)
            if llm_tasks:
                return llm_tasks

        return self._build_plan_with_rules(instruction)

    def _build_plan_with_llm(self, instruction: str) -> list[dict]:
        prompt = self._get_planning_prompt(instruction)
        response = self.llm_client.generate(prompt, max_tokens=512)

        if not response or response.startswith("[LLM stub]") or response.startswith("⚠️"):
            return []

        parsed = self._parse_llm_response(response)
        return parsed or []

    def _get_planning_prompt(self, instruction: str) -> str:
        examples = [
            {
                "instruction": "Ouvre notepad et crée un dossier 'projet'",
                "plan": [
                    {"type": "OPEN_APP", "target": "notepad.exe"},
                    {"type": "CREATE_FOLDER", "target": "projet"}
                ]
            },
            {
                "instruction": "Copier C:\\Users\\john\\document.txt vers D:\\backup\\document.txt",
                "plan": [
                    {"type": "FILE_COPY", "source": "C:\\Users\\john\\document.txt", "destination": "D:\\backup\\document.txt"}
                ]
            },
            {
                "instruction": "Cherche une recette de tarte aux pommes",
                "plan": [
                    {"type": "SEARCH_GOOGLE", "query": "recette de tarte aux pommes"}
                ]
            }
        ]

        return (
            "Tu es un planificateur de tâches pour une application d'automatisation locale. "
            "Reçois une instruction en français ou en anglais et retourne uniquement une liste JSON de tâches à exécuter. "
            "Ne fournis aucun texte explicatif additionnel, seulement le JSON. "
            "Chaque tâche doit être un objet avec un champ 'type' et les paramètres nécessaires. "
            "Les types possibles incluent: OPEN_APP, CREATE_FOLDER, MONITOR_CPU, FILE_COPY, FILE_MOVE, FILE_RENAME, FILE_DELETE, FILE_LIST, FILE_COMPRESS, "
            "EXECUTE_PYTHON, EXECUTE_POWERSHELL, EXECUTE_BATCH, SYSTEM_INFO, RESTART_PC, SHUTDOWN_PC, OPEN_URL, SEARCH_GOOGLE, SEARCH_BING, DOWNLOAD_FILE, SEND_EMAIL, SEND_NOTIFICATION, PLAY_SOUND, CREATE_NOTE, LIST_NOTES, DELETE_NOTE, CREATE_MACRO, EXECUTE_MACRO, LIST_MACROS, TRANSLATE_TO_FRENCH, "
            "BROWSER_NAVIGATE, BROWSER_SEARCH, BROWSER_EXTRACT, VISION_CAPTURE, VISION_OCR, VISION_DETECT_UI, VOICE_LISTEN, VOICE_SPEAK, AGENT_COORDINATE, SECURITY_AUDIT, SECURITY_SCAN, RESEARCH_ANALYZE, DEV_ANALYZE_CODE, MONITOR_REPORT. "
            "Utilise toujours un format JSON valide, sans commentaire, et évite tout texte additionnel. "
            "Voici des exemples :\n" + json.dumps(examples, ensure_ascii=False, indent=2) + "\n" +
            f"Instruction : {instruction}\n" +
            "Plan :"
        )

    def _parse_llm_response(self, text: str) -> list[dict]:
        cleaned = text.strip()
        if not cleaned:
            return []

        # try strict JSON first
        for candidate in self._extract_json_candidates(cleaned):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass

        # fallback to Python literal eval for lists/dicts with single quotes
        try:
            parsed = ast.literal_eval(cleaned)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        return []

    def _extract_json_candidates(self, text: str) -> list[str]:
        candidates = []
        if text.startswith("["):
            candidates.append(text)
        bracket_match = re.search(r'(\[.*\])', text, re.DOTALL)
        if bracket_match:
            candidates.append(bracket_match.group(1))
        return candidates

    def _build_plan_with_rules(self, instruction: str) -> list[dict]:
        tasks = []
        text = instruction.lower()

        # OPEN_APP detection
        if any(x in text for x in ["ouvrir", "open", "lancer", "launch", "run", "notepad", "calc", "paint", "explorer"]):
            if "exit" not in text and "quit" not in text:
                target = self._extract_app_name(text)
                tasks.append({
                    "type": "OPEN_APP",
                    "target": target or "notepad"
                })

        # CREATE_FOLDER detection
        if any(x in text for x in ["créer", "create", "folder", "dossier", "make directory"]):
            target = self._extract_folder_name(text)
            tasks.append({
                "type": "CREATE_FOLDER",
                "target": target or "workspace"
            })

        # MONITOR_CPU detection
        if any(x in text for x in ["monitor", "surveiller", "cpu", "performance", "resources"]):
            tasks.append({"type": "MONITOR_CPU"})

        # FILE OPERATIONS
        if "copier" in text or "copy" in text:
            src, dst = self._extract_file_paths(text)
            if src and dst:
                tasks.append({"type": "FILE_COPY", "source": src, "destination": dst})

        if "déplacer" in text or "move" in text:
            src, dst = self._extract_file_paths(text)
            if src and dst:
                tasks.append({"type": "FILE_MOVE", "source": src, "destination": dst})

        if "renommer" in text or "rename" in text:
            src, dst = self._extract_file_paths(text)
            if src and dst:
                tasks.append({"type": "FILE_RENAME", "source": src, "new_name": dst})

        if ("supprimer" in text or "delete" in text) and "fichier" in text:
            file_path = self._extract_path(text)
            if file_path:
                tasks.append({"type": "FILE_DELETE", "path": file_path})

        if "lister" in text or "list" in text or "dir" in text:
            dir_path = self._extract_path(text) or "."
            tasks.append({"type": "FILE_LIST", "directory": dir_path})

        if "compresser" in text or "compress" in text or "zip" in text:
            src, dst = self._extract_file_paths(text)
            if src:
                tasks.append({"type": "FILE_COMPRESS", "source": src, "destination": dst or "archive"})

        # SCRIPT EXECUTION
        if "python" in text and ".py" in text:
            script = self._extract_filename(text, ".py")
            if script:
                tasks.append({"type": "EXECUTE_PYTHON", "script": script})

        if "powershell" in text or "pwsh" in text:
            cmd = self._extract_command(text, ["powershell", "pwsh"])
            if cmd:
                tasks.append({"type": "EXECUTE_POWERSHELL", "command": cmd})

        if ".bat" in text:
            script = self._extract_filename(text, ".bat")
            if script:
                tasks.append({"type": "EXECUTE_BATCH", "script": script})

        # SYSTEM INFO
        if any(x in text for x in ["système", "system info", "info", "ram", "disk", "cpu usage"]):
            tasks.append({"type": "SYSTEM_INFO"})

        if "redémarrer" in text or "restart" in text or "reboot" in text:
            tasks.append({"type": "RESTART_PC"})

        if "arrêter" in text or "shutdown" in text or "fermer" in text:
            tasks.append({"type": "SHUTDOWN_PC"})

        # WEB OPERATIONS
        if "url" in text or "http" in text or "site" in text or ".com" in text:
            url = self._extract_url(text)
            if url:
                tasks.append({"type": "OPEN_URL", "url": url})

        if "google" in text and "chercher" in text or "search" in text:
            query = self._extract_search_query(text)
            if query:
                tasks.append({"type": "SEARCH_GOOGLE", "query": query})

        if "bing" in text and "chercher" in text or "bing" in text:
            query = self._extract_search_query(text)
            if query:
                tasks.append({"type": "SEARCH_BING", "query": query})

        if "télécharger" in text or "download" in text:
            url = self._extract_url(text)
            if url:
                tasks.append({"type": "DOWNLOAD_FILE", "url": url})

        # COMMUNICATION
        if "email" in text or "gmail" in text:
            tasks.append({"type": "SEND_EMAIL"})

        if "notification" in text:
            msg = self._extract_quoted_string(text)
            if msg:
                tasks.append({"type": "SEND_NOTIFICATION", "message": msg})

        if "son" in text or "sound" in text or "alert" in text:
            sound_type = self._extract_sound_type(text)
            tasks.append({"type": "PLAY_SOUND", "sound_type": sound_type})

        # NOTES
        if any(x in text for x in ["prendre une note", "prendre note", "add note", "ajouter note", "save note", "take note", "note:"]):
            content = self._extract_note_content(text)
            title = self._extract_note_title(text)
            if content:
                tasks.append({"type": "CREATE_NOTE", "content": content, "title": title})

        if any(x in text for x in ["lister notes", "voir notes", "list notes", "show notes"]):
            tasks.append({"type": "LIST_NOTES"})

        if any(x in text for x in ["supprimer note", "delete note"]):
            title = self._extract_note_title(text)
            if title:
                tasks.append({"type": "DELETE_NOTE", "title": title})

        # TRADUCTION
        if "traduire" in text or "translate" in text or ("anglais" in text and "français" in text) or ("english" in text and "french" in text):
            source_text = self._extract_translation_text(text)
            if source_text:
                tasks.append({"type": "TRANSLATE_TO_FRENCH", "text": source_text})

        # MACROS
        if "macro" in text or "routine" in text:
            if "créer" in text or "create" in text:
                name = self._extract_macro_name(text)
                if name:
                    tasks.append({"type": "CREATE_MACRO", "name": name})
            elif "exécuter" in text or "execute" in text or "run" in text:
                name = self._extract_macro_name(text)
                if name:
                    tasks.append({"type": "EXECUTE_MACRO", "name": name})
            elif "lister" in text or "list" in text:
                tasks.append({"type": "LIST_MACROS"})

        # BROWSER TASKS
        if "navigate" in text or "navigue" in text or "visite" in text:
            url = self._extract_url(text)
            if url:
                tasks.append({"type": "BROWSER_NAVIGATE", "url": url})

        if "browser" in text and "search" in text:
            query = self._extract_search_query(text)
            if query:
                tasks.append({"type": "BROWSER_SEARCH", "query": query})

        if "extract" in text and ("data" in text or "content" in text):
            tasks.append({"type": "BROWSER_EXTRACT"})

        # VISION TASKS
        if "capture" in text and ("screen" in text or "écran" in text):
            tasks.append({"type": "VISION_CAPTURE"})

        if "ocr" in text or "reconnaître" in text:
            image_path = self._extract_path(text)
            tasks.append({"type": "VISION_OCR", "image_path": image_path})

        if "detect" in text and ("ui" in text or "interface" in text):
            tasks.append({"type": "VISION_DETECT_UI"})

        # VOICE TASKS
        if "listen" in text or "écoute" in text or "voice" in text:
            tasks.append({"type": "VOICE_LISTEN"})

        if "speak" in text or "parle" in text or "say" in text:
            text_content = self._extract_quoted_string(text)
            if text_content:
                tasks.append({"type": "VOICE_SPEAK", "text": text_content})

        # MULTI-AGENT TASKS
        if "coordinate" in text or "orchestrate" in text or "agents" in text:
            tasks.append({"type": "AGENT_COORDINATE", "instruction": text})

        # SECURITY TASKS
        if "audit" in text and ("security" in text or "sécurité" in text):
            tasks.append({"type": "SECURITY_AUDIT"})

        if "scan" in text and ("security" in text or "sécurité" in text or "files" in text):
            directory = self._extract_path(text) or "."
            tasks.append({"type": "SECURITY_SCAN", "directory": directory})

        # RESEARCH TASKS
        if "analyze" in text and ("data" in text or "research" in text):
            tasks.append({"type": "RESEARCH_ANALYZE"})

        # DEVELOPMENT TASKS
        if "analyze" in text and ("code" in text or "fichier" in text):
            file_path = self._extract_path(text)
            if file_path:
                tasks.append({"type": "DEV_ANALYZE_CODE", "file_path": file_path})

        # MONITORING TASKS
        if "monitor" in text or "surveille" in text or "report" in text:
            tasks.append({"type": "MONITOR_REPORT"})

        return tasks

    def _extract_app_name(self, text: str) -> str:
        apps = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "vscode": "code.exe"
        }
        
        for app_key, app_name in apps.items():
            if app_key in text:
                return app_name
        
        return None

    def _extract_folder_name(self, text: str) -> str:
        match = re.search(r'["\']([^"\']+)["\']', text)
        if match:
            return match.group(1)
        
        for trigger in ["créer", "create", "folder", "dossier", "make"]:
            if trigger in text:
                parts = text.split(trigger)
                if len(parts) > 1:
                    remaining = parts[-1].strip()
                    if remaining and not remaining.startswith(('c:', 'd:', 'e:', 'f:')):
                        words = remaining.split()
                        if words:
                            return words[0].strip("\"'")
        
        return None

    def _extract_path(self, text: str) -> str:
        # Try to find quoted paths first
        match = re.search(r'["\']([^"\']*[/\\][^"\']*)["\']', text)
        if match:
            return match.group(1)
        
        # Try to find drive letters
        match = re.search(r'([a-zA-Z]:[/\\][^\s]*)', text)
        if match:
            return match.group(1)
        
        return None

    def _extract_file_paths(self, text: str) -> tuple:
        paths = re.findall(r'["\']([^"\']*[/\\][^"\']*)["\']', text)
        if len(paths) >= 2:
            return paths[0], paths[1]
        
        paths = re.findall(r'([a-zA-Z]:[/\\][^\s]+)', text)
        if len(paths) >= 2:
            return paths[0], paths[1]
        
        return None, None

    def _extract_filename(self, text: str, extension: str) -> str:
        pattern = rf'["\']?([^\s"\']*{re.escape(extension)})["\']?'
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def _extract_command(self, text: str, triggers: list) -> str:
        for trigger in triggers:
            if trigger in text:
                parts = text.split(trigger)
                if len(parts) > 1:
                    cmd = parts[-1].strip()
                    return cmd if cmd else None
        return None

    def _extract_url(self, text: str) -> str:
        match = re.search(r'https?://[^\s]+', text)
        if match:
            return match.group(0)
        
        match = re.search(r'(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', text)
        if match:
            url = match.group(0)
            return f"https://{url}" if not url.startswith("http") else url
        
        return None

    def _extract_search_query(self, text: str) -> str:
        for trigger in ["chercher", "search", "google", "bing"]:
            if trigger in text:
                parts = text.split(trigger)
                if len(parts) > 1:
                    query = parts[-1].strip()
                    # Remove quotes if present
                    query = query.strip("\"'")
                    return query if query else None
        return None

    def _extract_quoted_string(self, text: str) -> str:
        match = re.search(r'["\']([^"\']+)["\']', text)
        return match.group(1) if match else None

    def _extract_sound_type(self, text: str) -> str:
        types = {"info": "info", "warning": "warning", "error": "error"}
        for type_name in types:
            if type_name in text:
                return type_name
        return "default"

    def _extract_macro_name(self, text: str) -> str:
        match = re.search(r'(?:macro|routine)\s+["\']?([a-zA-Z0-9_]+)', text)
        return match.group(1) if match else None

    def _extract_note_title(self, text: str) -> str:
        match = re.search(r'(?:titre|title)\s+["\']([^"\']+)["\']', text)
        if match:
            return match.group(1)
        match = re.search(r'note\s+([a-zA-Z0-9_\-]+)', text)
        return match.group(1) if match else None

    def _extract_note_content(self, text: str) -> str:
        content = self._extract_quoted_string(text)
        if content:
            return content
        parts = re.split(r'\b(?:note|notes|prendre|add|ajouter|save|take)\b', text)
        if len(parts) > 1:
            return parts[-1].strip(' :"\'')
        return None

    def _extract_translation_text(self, text: str) -> str:
        content = self._extract_quoted_string(text)
        if content:
            return content
        if "traduire" in text:
            parts = text.split("traduire")
            if len(parts) > 1:
                return parts[-1].strip(' :"\'')
        if "translate" in text:
            parts = text.split("translate")
            if len(parts) > 1:
                return parts[-1].strip(' :"\'')
        return text
