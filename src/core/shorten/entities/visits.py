from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy import BigInteger


class Visit(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, autoincrement=True, primary_key=True),
    )
    visitor_ip: str = Field(max_length=45)

    url_id: int = Field(foreign_key="url.id")

    visited_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    url: Optional["URL"] = Relationship(back_populates="visits")
