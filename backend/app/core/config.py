from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    database_url: str
    redis_url: str
    log_level: str
    cache_default_ttl_seconds: int
    secret_key: str
    access_token_expire_minutes: int
    jwt_algorithm: str
    back_end_allowed_origins: list[str]


    def validate(self) -> None:
        if not self.database_url:
            raise ValueError("DATABASE_URL is required. Set it in the .env file.")
        if self.cache_default_ttl_seconds <= 0:
            raise ValueError("CACHE_DEFAULT_TTL_SECONDS must be greater than 0.")
        if not self.secret_key:
            raise ValueError("SECRET_KEY is required. Set it in the .env file.")
        if self.access_token_expire_minutes <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0.")


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


@lru_cache
def get_settings() -> Settings:
    resolved_settings = Settings(
        app_name=os.getenv("APP_NAME", "Student Management API"),
        database_url=_normalize_database_url(os.getenv("DATABASE_URL", "")),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        cache_default_ttl_seconds=int(os.getenv("CACHE_DEFAULT_TTL_SECONDS", "60")),
        secret_key=os.getenv("SECRET_KEY", ""),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        back_end_allowed_origins=os.getenv("BACK_END_ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    )
    resolved_settings.validate()

    return resolved_settings


settings = get_settings()
