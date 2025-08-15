from pydantic import BaseModel


class VisitLogMessage(BaseModel):
    original_url: str
    url_id: int
    short_code: str
    ip_address: str | None = None
    user_agent: str | None = None
