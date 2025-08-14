import asyncio
import logging

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_scoped_session,
)
from sqlalchemy.orm import sessionmaker, declarative_base


logger = logging.getLogger(__name__)
Base = declarative_base()


class Database:

    def __init__(self, db_url: str):
        self._engine = create_async_engine(db_url, echo=False)
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
