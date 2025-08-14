import time
from typing import Any, Optional

from .abstract_cache_storage import AbstractCacheStorage


class InMemoryCacheStorage(AbstractCacheStorage):
    def __init__(self):
        self._cache = {}
        self._expirations = {}

    async def get(self, key: str) -> Optional[Any]:
        if key in self._expirations and self._expirations[key] < time.time():
            self.delete(key)
            return None
        return self._cache.get(key)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        self._cache[key] = value
        if expire:
            self._expirations[key] = time.time() + expire

    async def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
        if key in self._expirations:
            del self._expirations[key]
