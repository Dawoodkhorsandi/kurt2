import asyncio
from typing import Set

import pytest
from src.core.common.exceptions import NotFoundException
from src.core.shorten.entities.urls import URL
from src.core.shorten.repositories.url_repository import UrlRepository
from src.core.shorten.services.url_shorten_service import UrlShortenService
from src.core.shorten.services.url_visits_service import UrlVisitsService
from src.core.infrastructures.message_queue.in_memory import InMemoryMessageQueue

pytestmark = pytest.mark.asyncio


async def await_on_remaining_tasks(exclude_tasks: Set):
    tasks = asyncio.all_tasks() - exclude_tasks
    await asyncio.gather(*tasks)


class TestUrlShortenService:
    async def test_create_short_url_for_new_url(
        self, url_shorten_service: UrlShortenService, url_repo: UrlRepository
    ):
        long_url = "https://www.google.com/a/very/long/path"

        created_url = await url_shorten_service.create_short_url(long_url)

        assert created_url.original_url == long_url
        assert created_url.short_code is not None
        assert created_url.short_code != "placeholder"

        db_url = await url_repo.get_by_original_url(long_url)
        assert db_url is not None
        assert db_url.id == created_url.id
        assert db_url.short_code == created_url.short_code

    async def test_create_short_url_for_existing_url(
        self, url_shorten_service: UrlShortenService, url_repo: UrlRepository
    ):
        long_url = "https://www.github.com/Dawoodkhorsandi/kurt2"
        initial_url = await url_repo.create(
            obj_in=URL(original_url=long_url, short_code="existing")
        )

        retrieved_url = await url_shorten_service.create_short_url(long_url)

        assert retrieved_url.id == initial_url.id
        assert retrieved_url.short_code == "existing"


class TestUrlVisitsService:
    async def test_get_original_url_and_logs_visit(
        self,
        url_visits_service: UrlVisitsService,
        url_repo: UrlRepository,
        message_queue: InMemoryMessageQueue,
    ):
        long_url = "https://fastapi.tiangolo.com/"
        short_code = "fastapi"
        await url_repo.create(obj_in=URL(original_url=long_url, short_code=short_code))

        result_url = await url_visits_service.get_original_url(
            short_code=short_code,
            ip_address="127.0.0.1",
            user_agent="pytest",
        )

        assert result_url == long_url

        await await_on_remaining_tasks(exclude_tasks={asyncio.current_task()})
        messages = await message_queue.get_batch(1)
        assert len(messages) == 1

        assert f'"short_code":"{short_code}"' in messages[0]
        assert '"ip_address":"127.0.0.1"' in messages[0]

    async def test_get_original_url_not_found(
        self, url_visits_service: UrlVisitsService
    ):
        with pytest.raises(NotFoundException, match="Short code not found."):
            await url_visits_service.get_original_url(short_code="nonexistent")

    async def test_get_url_stats(
        self, url_visits_service: UrlVisitsService, url_repo: UrlRepository
    ):
        await url_repo.create(
            obj_in=URL(
                original_url="https://www.python.org/",
                short_code="python",
                visit_count=42,
            )
        )

        visit_count = await url_visits_service.get_url_stats(short_code="python")

        assert visit_count == 42
