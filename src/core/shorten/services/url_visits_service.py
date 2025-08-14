from src.core.common.exceptions import NotFoundException
from src.core.infrastructures.cache.abstract_cache_storage import AbstractCacheStorage
from src.core.infrastructures.message_queue.abstract_message_queue import (
    AbstractMessageQueue,
)
from src.core.infrastructures.message_queue.decorators import cache, log_visit
from src.core.shorten.repositories.url_repository import UrlRepository


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

    @log_visit
    @cache
    async def get_original_url(
        self, short_code: str, ip_address: str | None = None, user_agent: str | None = None
    ) -> str:
        """Retrieves the original URL for a given short code, using a cache and logging the visit."""
        url = await self.url_repository.get_by_short_code(short_code=short_code)
        if not url:
            raise NotFoundException("Short code not found.")

        return url.original_url

    async def get_url_stats(self, short_code: str) -> int:
        url = await self.url_repository.get_with_visits_by_short_code(
            short_code=short_code
        )
        if not url:
            raise NotFoundException("Short code not found.")
        return len(url.visits)
