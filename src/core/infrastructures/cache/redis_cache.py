from typing import Any, Optional

import redis.asyncio as redis

from .abstract_cache_storage import AbstractCacheStorage


class RedisCacheStorage(AbstractCacheStorage):
    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        return await self._redis.get(key)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        await self._redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
