from pydantic import BaseModel


class VisitLogMessage(BaseModel):
    short_code: str
    ip_address: str | None = None
    user_agent: str | None = None
