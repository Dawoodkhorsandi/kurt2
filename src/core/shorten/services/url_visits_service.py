from src.core.common.exceptions import NotFoundException
from src.core.infrastructures.cache.abstract_cache_storage import AbstractCacheStorage
from src.core.infrastructures.cache.decorators import cache
from src.core.infrastructures.message_queue.abstract_message_queue import (
    AbstractMessageQueue,
)
from src.core.infrastructures.message_queue.decorators import log_visit
from src.core.shorten.entities.urls import URL
from src.core.shorten.repositories.url_repository import UrlRepository

A_DAY = 24 * 60 * 60


class UrlVisitsService:
    def __init__(
        self,
        url_repository: UrlRepository,
        message_queue: AbstractMessageQueue,
        cache_storage: AbstractCacheStorage,
    ) -> None:
        self.url_repository = url_repository
        self.message_queue = message_queue
        self.cache_storage = cache_storage

    async def _get_url_or_raise(self, short_code: str) -> URL:
        url = await self.url_repository.get_by_short_code(short_code=short_code)
        if not url:
            raise NotFoundException("Short code not found.")
        return url

    @log_visit
    @cache(prefix="get_original_url", expire=A_DAY)
    async def get_original_url(
        self,
        short_code: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> URL:
        return await self._get_url_or_raise(short_code)

    async def get_url_stats(self, short_code: str) -> int:
        url = await self._get_url_or_raise(short_code)
        return url.visit_count
