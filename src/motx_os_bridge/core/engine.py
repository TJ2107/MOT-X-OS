import asyncio

from .planner import TaskPlanner
from .executor import TaskExecutor
from .memory import MemoryManager
from .security import SecurityManager


class MOTXAutomationEngine:
    def __init__(self, interactive: bool = False, dry_run: bool = False):
        self.planner = TaskPlanner()
        self.executor = TaskExecutor()
        self.memory = MemoryManager()
        self.security = SecurityManager()
        self.interactive = interactive
        self.dry_run = dry_run

    async def process_instruction(self, instruction: str):
        print(f"\n🧠 Processing: {instruction}")
        plan = self.planner.build_plan(instruction)
        print(f"⚡ Plan generated with {len(plan)} tasks")

        results = []

        for task in plan:
            allowed, reason, requires_confirmation = self.security.validate(task)
            if not allowed and requires_confirmation and self.interactive:
                confirmed = self.confirm_task(task, reason)
                if confirmed:
                    allowed = True
                else:
                    print(f"⛔ Action annulée par l'utilisateur : {task}")
                    continue

            if not allowed:
                reason_text = f" — {reason}" if reason else ""
                print(f"⛔ Blocked task: {task}{reason_text}")
                continue

            if self.dry_run:
                print(f"✅ [DRY-RUN] Tâche simulée avec succès : {task.get('type')}")
                result = {"status": "success", "simulated": True, "task": task}
            else:
                result = await self.executor.execute(task)
                
            results.append(result)
            self.memory.store(task, result)

        return results

    def confirm_task(self, task: dict, reason: str | None) -> bool:
        prompt = f"⚠️ {reason or 'Confirmation requise'}. Confirmer exécution de {task.get('type')} ? [y/N] "
        while True:
            answer = input(prompt).strip().lower()
            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no", ""}:
                return False
            print("Répondez par y/n.")
