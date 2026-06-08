"""Pydantic schemas for accounts + saved-breaks sync."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class RegisterIn(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("invalid email")
        return v

    @field_validator("password")
    @classmethod
    def _password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.strip().lower()


class GoogleIn(BaseModel):
    id_token: str


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # access token TTL in seconds
    user: UserOut


# ── saved breaks ────────────────────────────────────────────────────────────

class SavedBreakDTO(BaseModel):
    id: str
    label: str
    start: date
    end: date
    pto_cost: int
    kind: str
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class SyncIn(BaseModel):
    breaks: list[SavedBreakDTO] = []


class SavedBreaksOut(BaseModel):
    breaks: list[SavedBreakDTO]
    server_time: datetime
