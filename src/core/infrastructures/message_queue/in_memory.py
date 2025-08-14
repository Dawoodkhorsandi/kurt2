import asyncio
from .abstract_message_queue import AbstractMessageQueue


class InMemoryMessageQueue(AbstractMessageQueue):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, message: dict):
        await self.queue.put(message)

    async def get_batch(self, batch_size: int) -> list[dict]:
        messages = []
        for _ in range(batch_size):
            try:
                message = self.queue.get_nowait()
                messages.append(message)
            except asyncio.QueueEmpty:
                break
        return messages

    async def close(self):
        pass
