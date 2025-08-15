import asyncio
import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class Database:
    def __init__(self, db_url: str, pool_size: int = 5, max_overflow: int = 10):
        self._engine = create_async_engine(
            db_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=False,
            connect_args={"statement_cache_size": 0},
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
