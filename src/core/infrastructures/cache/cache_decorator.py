import functools
from typing import Any, Callable, Optional

from .abstract_cache_storage import AbstractCacheStorage


def cache(cache_storage: AbstractCacheStorage, prefix: str, expire: Optional[int] = None):
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{args}:{kwargs}"
            cached_result = await cache_storage.get(key)
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            await cache_storage.set(key, result, expire)
            return result

        return wrapper

    return decorator


def invalidate_cache(cache_storage: AbstractCacheStorage, prefix: str):
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{args}:{kwargs}"
            await cache_storage.delete(key)
            return await func(*args, **kwargs)

        return wrapper

    return decorator
