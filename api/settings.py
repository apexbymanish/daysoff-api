"""Runtime configuration for accounts + sync (Phase 1).

Values come from environment variables (see field names). Defaults are safe for
local development on SQLite; production overrides DATABASE_URL to Postgres and
MUST override JWT_SECRET.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # sqlite+aiosqlite for local/dev/test; postgresql+asyncpg://… in prod.
    database_url: str = "sqlite+aiosqlite:///./daysoff.db"

    # HS256 signing key for our JWTs. Override in prod (set DAYSOFF_JWT_SECRET).
    jwt_secret: str = "dev-insecure-change-me-0123456789abcdef"

    access_ttl_min: int = 30
    refresh_ttl_days: int = 30

    # Applied to Postgres engines only (SQLite ignores them).
    db_pool_size: int = 10
    db_max_overflow: int = 20


# Read once at import. DATABASE_URL / JWT_SECRET (or DAYSOFF_JWT_SECRET via the
# alias below) are picked up from the environment.
import os  # noqa: E402

settings = Settings(
    jwt_secret=os.environ.get(
        "DAYSOFF_JWT_SECRET", os.environ.get("JWT_SECRET", "dev-insecure-change-me-0123456789abcdef")
    ),
)
