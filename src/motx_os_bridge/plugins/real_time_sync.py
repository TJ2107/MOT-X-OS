import asyncio
import logging

logger = logging.getLogger(__name__)


class RealTimeSync:
    """Synchronisation real-time entre clients."""

    def __init__(self):
        self.subscribers = []
        self.message_queue = asyncio.Queue()

    async def subscribe(self, client_id: str, callback):
        self.subscribers.append({
            "id": client_id,
            "callback": callback
        })

    async def unsubscribe(self, client_id: str):
        self.subscribers = [s for s in self.subscribers if s["id"] != client_id]

    async def broadcast(self, message: dict):
        for subscriber in list(self.subscribers):
            try:
                await subscriber["callback"](message)
            except Exception as e:
                logger.error(f"Error broadcasting: {str(e)}")

    async def process_queue(self):
        while True:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.broadcast(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue error: {str(e)}")
