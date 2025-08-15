import asyncio
import logging
from functools import wraps

from src.core.shorten.schemas.messages import VisitLogMessage

logger = logging.getLogger(__name__)


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

        url = await func(self, *args, **kwargs)
        if url:
            visit_message = VisitLogMessage(
                url_id=url.id,
                original_url=url.original_url,
                short_code=short_code,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            log_data = visit_message.model_dump()
            logger.debug("Push task on queue", extra=log_data)
            asyncio.create_task(message_queue.publish(log_data))

        return url

    return wrapper
