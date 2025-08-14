from sqlalchemy import func, select

from src.core.common.base_repository import BaseRepository
from src.core.shorten.entities.visits import Visit


class VisitsRepository(BaseRepository[Visit]):
    async def count_by_url_id(self, url_id: int) -> int:
        query = select(func.count()).select_from(self.model).filter_by(url_id=url_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def add_all(self, visits: list[Visit]) -> None:
        """Adds a batch of visit records to the database."""
        self.session.add_all(visits)
