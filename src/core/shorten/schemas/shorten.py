from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = None


class ShortenResponse(BaseModel):
    short_code: str
    original_url: str


class StatsResponse(BaseModel):
    visits: int
