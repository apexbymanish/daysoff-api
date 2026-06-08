"""Security utilities: password hashing, JWT access tokens, refresh tokens,
and the current-user dependency."""
from __future__ import annotations

import hashlib
from typing import Optional
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .models_db import User
from .settings import settings

ALGO = "HS256"


# ── passwords ────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


# ── access token (JWT) ─────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_ttl_min),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGO)


def decode_access_token(token: str) -> str:
    """Return the user id from a valid access token, else raise 401."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGO])
    except jwt.PyJWTError:
        raise _unauthorized("invalid or expired token")
    if payload.get("type") != "access":
        raise _unauthorized("wrong token type")
    sub = payload.get("sub")
    if not sub:
        raise _unauthorized("malformed token")
    return sub


# ── refresh token (opaque, stored hashed) ──────────────────────────────────────

def new_refresh_token() -> tuple[str, str]:
    """Return (raw_token, sha256_hash). Only the hash is persisted."""
    raw = secrets.token_urlsafe(32)
    return raw, hash_token(raw)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def refresh_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=settings.refresh_ttl_days)


# ── current-user dependency ─────────────────────────────────────────────────────

def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    user_id = decode_access_token(token)
    user = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise _unauthorized("user not found")
    return user
