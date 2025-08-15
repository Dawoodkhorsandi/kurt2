import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dependency_injector import providers
from sqlmodel import SQLModel

from src.api_server.app import create_app, AppContainer
from src.core.common.settings import Settings
from src.core.shorten.repositories.url_repository import UrlRepository
from src.core.shorten.repositories.visits_repository import VisitsRepository
from src.core.shorten.services.url_shorten_service import UrlShortenService
from src.core.shorten.services.url_visits_service import UrlVisitsService
from src.core.infrastructures.message_queue.in_memory import InMemoryMessageQueue


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        _env_file=".env.test",
        cache_type="in-memory",
        message_queue_type="in-memory",
    )


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database(test_settings: Settings) -> AsyncGenerator[None, None]:
    engine = create_async_engine(str(test_settings.postgres_dsn))

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(str(test_settings.postgres_dsn))
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="function")
def test_container(db_session: AsyncSession, test_settings: Settings) -> AppContainer:
    container = AppContainer()
    container.settings.override(providers.Object(test_settings))
    container.db_session.override(providers.Object(db_session))

    return container


@pytest_asyncio.fixture(scope="function")
async def client(test_container: AppContainer) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    app.container = test_container

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def url_repo(test_container: AppContainer) -> UrlRepository:
    return test_container.url_repository()


@pytest.fixture
def visit_repo(test_container: AppContainer) -> VisitsRepository:
    return test_container.visits_repository()


@pytest.fixture
def url_shorten_service(test_container: AppContainer) -> UrlShortenService:
    return test_container.url_shorten_service()


@pytest.fixture
def url_visits_service(test_container: AppContainer) -> UrlVisitsService:
    return test_container.url_visits_service()


@pytest.fixture
def message_queue(test_container: AppContainer) -> InMemoryMessageQueue:
    return test_container.message_queue()
