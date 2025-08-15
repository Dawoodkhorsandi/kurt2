from sqlalchemy import select, update, case
from sqlalchemy.orm import joinedload
from typing import Dict

from src.core.common.base_repository import BaseRepository
from src.core.shorten.entities.urls import URL


class UrlRepository(BaseRepository[URL]):
    async def get_by_short_code(self, short_code: str) -> URL | None:
        return await self.get_one_or_none(short_code=short_code)

    async def get_by_original_url(self, original_url: str) -> URL | None:
        return await self.get_one_or_none(original_url=original_url)

    async def get_one_or_none(self, **filter_by) -> URL | None:
        statement = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_with_visits_by_short_code(self, short_code: str) -> URL | None:
        query = (
            select(self.model)
            .options(joinedload(self.model.visits))
            .filter_by(short_code=short_code)
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def increment_visit_count(self, short_code: str) -> None:
        query = (
            update(self.model)
            .where(self.model.short_code == short_code)
            .values(visit_count=self.model.visit_count + 1)
        )
        await self.session.execute(query)

    async def bulk_increment_visit_counts(self, counts: Dict[str, int]) -> None:
        """
        Atomically increments the visit_count for multiple urls.
        `counts` is a dictionary mapping short_code to the increment value.
        """
        if not counts:
            return

        await self.session.execute(
            update(self.model)
            .where(self.model.short_code.in_(counts.keys()))
            .values(
                visit_count=self.model.visit_count
                + case(
                    counts,
                    value=self.model.short_code,
                )
            )
        )
