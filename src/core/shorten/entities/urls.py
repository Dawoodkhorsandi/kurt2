from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy import BigInteger


class URL(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, autoincrement=True, primary_key=True, index=True, unique=True),
    )
    original_url: str = Field(index=True)
    short_code: str = Field(unique=True, index=True)
    visit_count: int = Field(default=0)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    visits: List["VisitLogMessage"] = Relationship(back_populates="url", sa_relationship_kwargs={"lazy": "raise_on_sql"})
