import asyncio
import logging
from collections import Counter
from typing import List

from pydantic import ValidationError

from src.core.infrastructures.dependency_injection.app_container import AppContainer
from src.core.infrastructures.message_queue.abstract_message_queue import (
    AbstractMessageQueue,
)
from src.core.shorten.entities.messages import VisitLogMessage
from src.core.shorten.entities.visits import Visit
from src.core.shorten.repositories.url_repository import UrlRepository
from src.core.shorten.repositories.visits_repository import VisitsRepository
from src.core.infrastructures.logging import setup_logging

BATCH_SIZE = 100
SLEEP_INTERVAL = 1  # In seconds

logger = logging.getLogger(__name__)


class LogWorker:
    def __init__(
        self,
        message_queue: AbstractMessageQueue,
        url_repository: UrlRepository,
        visits_repository: VisitsRepository,
    ):
        self.message_queue = message_queue
        self.url_repository = url_repository
        self.visits_repository = visits_repository

    async def process_messages(self, messages: List[VisitLogMessage]):
        if not messages:
            return

        logger.info(f"Processing a batch of {len(messages)} messages.")

        visits_to_add = [Visit(**message.model_dump()) for message in messages]

        await self.visits_repository.add_all(visits_to_add)

        visit_counts = Counter(msg.short_code for msg in messages)

        await self.url_repository.bulk_increment_visit_counts(visit_counts)

        await self.visits_repository.session.commit()

    async def run(self):
        logger.info("Log worker started.")
        logger.info(
            f"Using message queue type: {self.message_queue.__class__.__name__}"
        )

        while True:
            try:
                raw_messages = await self.message_queue.get_batch(BATCH_SIZE)

                if not raw_messages:
                    logger.debug("Queue is empty, sleeping...")
                    await asyncio.sleep(SLEEP_INTERVAL)
                    continue

                valid_messages: List[VisitLogMessage] = []

                for msg_data in raw_messages:
                    try:
                        valid_messages.append(VisitLogMessage.model_validate(msg_data))
                    except ValidationError as e:
                        logger.warning(
                            f"Skipping malformed message. Data: {msg_data}. Error: {e}"
                        )

                if valid_messages:
                    await self.process_messages(valid_messages)

            except ConnectionError as e:
                logger.error(f"Message queue connection error: {e}. Retrying...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}", exc_info=True)
                await asyncio.sleep(SLEEP_INTERVAL)


async def main():
    setup_logging()
    container = AppContainer()

    message_queue = container.message_queue()
    url_repository = container.url_repository()
    visits_repository = container.visits_repository()

    worker = LogWorker(message_queue, url_repository, visits_repository)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
