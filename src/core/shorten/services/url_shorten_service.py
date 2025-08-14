from src.core.shorten.entities.urls import URL
from src.core.shorten.repositories.url_repository import UrlRepository
from src.core.shorten.utils.shorten_strategy.abstract_shorten_strategy import ShortCodeStrategy



class UrlShortenService:
    def __init__(
        self,
        url_repository: UrlRepository,
        short_code_strategy: ShortCodeStrategy,
    ) -> None:
        self.url_repository = url_repository
        self.short_code_strategy = short_code_strategy

    async def create_short_url(self, original_url: str) -> URL:
        if existing_url := await self.url_repository.get_by_original_url(
            original_url=original_url
        ):
            return existing_url

        new_url = URL(original_url=original_url)
        created_url = await self.url_repository.create(new_url)

        short_code = self.short_code_strategy.generate(created_url.id)

        updated_url = await self.url_repository.update(
            created_url, {"short_code": short_code}
        )

        return updated_url
