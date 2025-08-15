import asyncio
import logging
import uuid

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from src.core.common.settings import Settings

logger = logging.getLogger(__name__)
Base = declarative_base()


class Database:
    def __init__(self, db_url: str, pool_size: int = 5, max_overflow: int = 10):
        settings = Settings()
        engine_kwargs = {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "echo": False,
        }

        if settings.use_pgbouncer:
            logger.info("Using NullPool for database connections (PgBouncer mode).")
            engine_kwargs["connect_args"] = (
                {
                    "prepared_statement_name_func": lambda: f"__a\
                    syncpg_{uuid.uuid4()}__",
                    "statement_cache_size": 0,
                    "prepared_statement_cache_size": 0,
                },
            )
            engine_kwargs["poolclass"] = NullPool
            # NullPool does not use these arguments, so we remove them.
            del engine_kwargs["pool_size"]
            del engine_kwargs["max_overflow"]
        else:
            logger.info(
                f"Using default QueuePool with pool_size={pool_size} "
                f"and max_overflow={max_overflow}."
            )
        self._engine = create_async_engine(
            db_url,
            **engine_kwargs,
        )
        session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self._session_factory = async_scoped_session(
            session_factory,
            scopefunc=asyncio.current_task,
        )

    def get_session(self) -> AsyncSession:
        """Returns the session."""
        return self._session_factory()

    async def close_session(self):
        """Closes and removes the session."""
        await self._session_factory.remove()
