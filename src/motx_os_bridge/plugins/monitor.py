import asyncio


class MonitorPlugin:
    async def monitor_cpu(self) -> str:
        await asyncio.sleep(0.1)
        return "Surveillance CPU activée : informations collectées"

    async def monitor_memory(self) -> str:
        await asyncio.sleep(0.1)
        return "Surveillance mémoire activée : informations collectées"
