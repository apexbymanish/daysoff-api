"""Auth endpoints: register, login, refresh, logout, /me."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import (
    create_access_token,
    get_current_user,
    hash_password,
    hash_token,
    new_refresh_token,
    refresh_expiry,
    verify_password,
)
from .. import google_auth
from ..db import get_db
from ..models_db import OAuthIdentity, RefreshToken, User
from ..schemas_auth import (
    GoogleIn,
    LoginIn,
    LogoutIn,
    RefreshIn,
    RegisterIn,
    TokenOut,
    UserOut,
)
from ..settings import settings

router = APIRouter(tags=["auth"])


async def _issue_tokens(db: AsyncSession, user: User) -> TokenOut:
    raw_refresh, refresh_hash = new_refresh_token()
    db.add(RefreshToken(
        user_id=user.id, token_hash=refresh_hash, expires_at=refresh_expiry()
    ))
    await db.commit()
    return TokenOut(
        access_token=create_access_token(user.id),
        refresh_token=raw_refresh,
        expires_in=settings.access_ttl_min * 60,
        user=UserOut.model_validate(user, from_attributes=True),
    )


@router.post("/v1/auth/register", status_code=status.HTTP_201_CREATED,
             response_model=TokenOut)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    existing = await db.scalar(select(User).where(User.email == body.email))
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
    )
    db.add(user)
    await db.flush()  # populate user.id
    return await _issue_tokens(db, user)


@router.post("/v1/auth/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await db.scalar(select(User).where(User.email == body.email))
    if user is None or not user.password_hash \
            or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    return await _issue_tokens(db, user)


@router.post("/v1/auth/google", response_model=TokenOut)
async def google_signin(body: GoogleIn,
                        db: AsyncSession = Depends(get_db)) -> TokenOut:
    try:
        info = google_auth.verify_google_id_token(body.id_token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid Google token")

    allowed = settings.google_client_id_set
    if allowed and info.get("aud") not in allowed:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Google token audience not allowed")
    email = (info.get("email") or "").lower()
    if not email or not info.get("email_verified", False):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Google account email not verified")
    sub = info.get("sub")
    if not sub:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "malformed Google token")

    # Find by Google identity, else link to an existing email account, else
    # create a new user.
    identity = await db.scalar(
        select(OAuthIdentity).where(
            OAuthIdentity.provider == "google",
            OAuthIdentity.provider_sub == sub,
        )
    )
    if identity is not None:
        user = await db.scalar(select(User).where(User.id == identity.user_id))
    else:
        user = await db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, password_hash=None,
                        display_name=info.get("name"))
            db.add(user)
            await db.flush()
        db.add(OAuthIdentity(user_id=user.id, provider="google",
                             provider_sub=sub))
        await db.flush()
    return await _issue_tokens(db, user)


@router.post("/v1/auth/refresh", response_model=TokenOut)
async def refresh(body: RefreshIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    row = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(body.refresh_token))
    )
    if row is None or row.revoked or row.expires_at < datetime.utcnow():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    row.revoked = True  # rotate: the presented token is single-use
    user = await db.scalar(select(User).where(User.id == row.user_id))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return await _issue_tokens(db, user)


@router.post("/v1/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutIn, db: AsyncSession = Depends(get_db)) -> None:
    row = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(body.refresh_token))
    )
    if row is not None:
        row.revoked = True
        await db.commit()


@router.get("/v1/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user, from_attributes=True)


@router.delete("/v1/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    await db.delete(user)  # cascades to breaks, refresh tokens, identities
    await db.commit()
