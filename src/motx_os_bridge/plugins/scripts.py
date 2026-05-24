import subprocess
import sys


class ScriptsPlugin:
    def execute_python(self, script_path: str, args: str = "") -> str:
        try:
            cmd = f"python {script_path} {args}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return f"✅ Python script exécuté:\n{result.stdout}" if result.stdout else "✅ Script exécuté"
        except subprocess.TimeoutExpired:
            return "⚠️ Script timeout (30s)"
        except Exception as e:
            return f"❌ Erreur Python : {e}"

    def execute_powershell(self, command: str) -> str:
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            return f"✅ PowerShell exécuté:\n{result.stdout}" if result.stdout else "✅ Commande exécutée"
        except Exception as e:
            return f"❌ Erreur PowerShell : {e}"

    def execute_batch(self, batch_file: str) -> str:
        try:
            result = subprocess.run(batch_file, capture_output=True, text=True, timeout=30, shell=True)
            return f"✅ Batch exécuté:\n{result.stdout}" if result.stdout else "✅ Batch exécuté"
        except Exception as e:
            return f"❌ Erreur batch : {e}"
