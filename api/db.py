"""Async database layer (SQLAlchemy 2.0).

Runs on SQLite (aiosqlite) for local/dev/test and Postgres (asyncpg) in prod —
selected entirely by DATABASE_URL. Engine pooling is applied for Postgres.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .settings import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def make_engine(url: Optional[str] = None):
    url = url or settings.database_url
    if url.startswith("sqlite"):
        return create_async_engine(
            url, connect_args={"check_same_thread": False}, future=True
        )
    # Postgres (or any networked DB): bounded pool + liveness checks so the app
    # scales horizontally without exhausting the server's connection budget.
    return create_async_engine(
        url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        future=True,
    )


engine = make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding an async session per request."""
    async with SessionLocal() as session:
        yield session


async def create_all() -> None:
    """Create all tables (dev/test convenience; prod uses Alembic migrations)."""
    # Import models so they register on Base.metadata before create_all.
    from . import models_db  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
