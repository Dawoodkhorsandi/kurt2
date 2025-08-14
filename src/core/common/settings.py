from os import path

from pydantic import PostgresDsn, Field, root_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_dsn: PostgresDsn
    cache_type: str = Field("in-memory", description="Cache type can be 'in-memory' or 'redis'")
    message_queue_type: str = Field("in-memory", description="Message queue type can be 'in-memory' or 'redis'")
    redis_queue_name: str | None = Field(None, description="Redis queue name if message_queue_type is 'redis'")
    redis_dsn: str | None = Field(None, description="Redis DSN if cache_type is 'redis'")

    @root_validator(skip_on_failure=True)
    def check_redis_dsn(cls, values):
        if (values.get("cache_type") == "redis" or values.get("message_queue_type") == "redis") and not values.get("redis_dsn"):
            raise ValueError("REDIS_DSN must be set if cache_type or message_queue_type is 'redis'")
        return values

    model_config = SettingsConfigDict(
        extra='allow',
        env_prefix="SHORTEN_APP_",
        case_sensitive=False,
        env_file=path.join(path.dirname(path.abspath(__file__)), "..", "..", "..", ".env"),
    )
