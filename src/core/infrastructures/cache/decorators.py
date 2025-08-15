import functools
import inspect
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def cache(prefix: str, expire: Optional[int] = None):
    def decorator(func: Callable[..., Any]):
        sig = inspect.signature(func)
        return_type = sig.return_annotation

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            key_args_dict = bound_args.arguments
            key_args_dict.pop("self", None)

            key_args = ",".join(f"{k}={v}" for k, v in sorted(key_args_dict.items()))
            key = f"{prefix}:{func.__name__}:({key_args})"

            cached_result = await self.cache_storage.get(key)
            if cached_result:
                logger.debug("Cache hit", extra={"cache_key": key})
                if isinstance(cached_result, str):
                    return return_type.model_validate_json(cached_result)
                return cached_result
            logger.debug("Cache miss", extra={"cache_key": key})
            result = await func(self, *args, **kwargs)

            if result:
                await self.cache_storage.set(key, result.model_dump_json(), expire)

            return result

        return wrapper

    return decorator
