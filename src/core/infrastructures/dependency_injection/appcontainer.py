from dependency_injector import containers, providers

from src.core.common.settings import Settings
from src.core.infrastructures.cache.abstract_cache_storage import AbstractCacheStorage
from src.core.infrastructures.cache.inmemory_cache import InMemoryCacheStorage
from src.core.infrastructures.cache.redis_cache import RedisCacheStorage
from src.core.infrastructures.database.database import Database, AsyncSession
from src.core.infrastructures.message_queue.abstract_message_queue import (
    AbstractMessageQueue,
)
from src.core.infrastructures.message_queue.in_memory import InMemoryMessageQueue
from src.core.infrastructures.message_queue.redis import RedisMessageQueue
from src.core.shorten.entities.urls import URL
from src.core.shorten.entities.visits import Visit
from src.core.shorten.repositories.url_repository import UrlRepository
from src.core.shorten.repositories.visits_repository import VisitsRepository
from src.core.shorten.utils.shorten_strategy.abstract_shorten_strategy import ShortCodeStrategy
from src.core.shorten.utils.shorten_strategy.base_62_shorten_stategy import Base62ShortCodeStrategy
from src.core.shorten.services.url_shorten_service import UrlShortenService
from src.core.shorten.services.url_visits_service import UrlVisitsService


class AppContainer(containers.DeclarativeContainer):
    settings: providers.Singleton[Settings] = providers.Singleton(Settings)
    db_url_provider: providers.Provider[str] = providers.Factory(
        lambda s: str(s.postgres_dsn),
        s=settings,
    )
    database: providers.Singleton[Database] = providers.Singleton(
        Database,
        db_url=db_url_provider,
    )
    db_session: providers.Factory[AsyncSession] = providers.Factory(
        lambda db: db.get_session(),
        db=database,
    )

    redis_cache = providers.Singleton(
        RedisCacheStorage, redis_url=settings.provided.redis_dsn
    )
    in_memory_cache = providers.Singleton(InMemoryCacheStorage)

    cache_storage: providers.Selector[AbstractCacheStorage] = providers.Selector(
        settings.provided.cache_type,
        redis=redis_cache,
        **{"in-memory": in_memory_cache}
    )

    redis_message_queue = providers.Singleton(
        RedisMessageQueue, dsn=settings.provided.redis_dsn
    )
    in_memory_message_queue = providers.Singleton(InMemoryMessageQueue)
    message_queue: providers.Selector[AbstractMessageQueue] = providers.Selector(
        settings.provided.message_queue_type,
        redis=redis_message_queue,
        **{"in-memory": in_memory_message_queue}
    )

    url_repository = providers.Factory(UrlRepository, model=URL, session=db_session)
    visits_repository = providers.Factory(
        VisitsRepository, model=Visit, session=db_session
    )

    short_code_strategy: providers.Factory[ShortCodeStrategy] = providers.Factory(
        Base62ShortCodeStrategy,
    )

    url_shorten_service = providers.Factory(
        UrlShortenService,
        url_repository=url_repository,
        short_code_strategy=short_code_strategy,
    )

    url_visits_service = providers.Factory(
        UrlVisitsService,
        url_repository=url_repository,
        message_queue=message_queue,
        cache_storage=cache_storage,
    )


container = AppContainer()
