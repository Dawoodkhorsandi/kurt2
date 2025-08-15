from functools import wraps

from src.core.infrastructures.message_queue.decorators import logger


def cache(func):
    """
    A decorator that caches the result of a function call.
    It assumes the wrapped object has a `cache_storage` attribute.
    """

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        cache_storage = self.cache_storage
        short_code = kwargs.get("short_code")

        cached_result = await cache_storage.get(short_code)
        if cached_result:
            logger.debug("CacheUtil: cache hit", extra={"short_code": short_code})
            return cached_result
        logger.debug("CacheUtil: cache miss", extra={"short_code": short_code})
        result = await func(self, *args, **kwargs)

        if result:
            await cache_storage.set(short_code, result)

        return result

    return wrapper
