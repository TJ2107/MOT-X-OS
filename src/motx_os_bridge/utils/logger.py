import json
import os
from datetime import datetime


class Logger:
    def __init__(self):
        self.log_file = "motx_os_bridge/logs/actions.json"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log_action(self, instruction: str, task_type: str, result: str, status: str = "success"):
        try:
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
            
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "instruction": instruction,
                "task_type": task_type,
                "result": result,
                "status": status
            })
            
            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Erreur logging: {e}")

    def get_history(self, limit: int = 10) -> list:
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
                    return logs[-limit:]
        except Exception:
            pass
        return []
