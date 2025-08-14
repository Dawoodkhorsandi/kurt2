import asyncio
from functools import wraps
from src.core.shorten.entities.messages import VisitLogMessage


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
            return cached_result

        result = await func(self, *args, **kwargs)

        if result:
            await cache_storage.set(short_code, result)
        
        return result
    return wrapper


def log_visit(func):
    """
    A decorator that logs a visit to a short URL.
    It assumes the wrapped object has a `message_queue` attribute.
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        message_queue = self.message_queue

        short_code = kwargs.get("short_code")
        ip_address = kwargs.get("ip_address")
        user_agent = kwargs.get("user_agent")

        original_url = await func(self, *args, **kwargs)

        if original_url:
            visit_message = VisitLogMessage(
                short_code=short_code,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            asyncio.create_task(message_queue.publish(visit_message.model_dump_json()))

        return original_url
    return wrapper
