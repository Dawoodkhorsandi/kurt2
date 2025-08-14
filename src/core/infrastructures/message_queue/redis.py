import json
import redis.asyncio as redis
from .abstract_message_queue import AbstractMessageQueue


class RedisMessageQueue(AbstractMessageQueue):
    def __init__(self, dsn: str, queue_name: str = "default_queue"):
        self.redis = redis.from_url(dsn)
        self.queue_name = queue_name

    async def publish(self, message: dict):
        await self.redis.rpush(self.queue_name, json.dumps(message))

    async def get_batch(self, batch_size: int) -> list[dict]:
        pipe = self.redis.pipeline()
        pipe.lrange(self.queue_name, 0, batch_size - 1)
        pipe.ltrim(self.queue_name, batch_size, -1)
        messages, _ = await pipe.execute()
        return [json.loads(msg) for msg in messages]

    async def close(self):
        await self.redis.close()
