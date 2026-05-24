from datetime import datetime


class SchedulerPlugin:
    def schedule_task(self, task: dict, run_at: datetime) -> str:
        return f"Tâche planifiée : {task.get('type')} à {run_at.isoformat()}"
