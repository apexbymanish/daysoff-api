"""Saved-breaks sync endpoints (per-user, last-write-wins merge)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..db import get_db
from ..models_db import SavedBreakRow, User
from ..schemas_auth import SavedBreakDTO, SavedBreaksOut, SyncIn

router = APIRouter(tags=["saved-breaks"])


def _to_dto(row: SavedBreakRow) -> SavedBreakDTO:
    return SavedBreakDTO(
        id=row.id, label=row.label, start=row.start, end=row.end,
        pto_cost=row.pto_cost, kind=row.kind,
        updated_at=row.updated_at, deleted_at=row.deleted_at,
    )


async def _current(db: AsyncSession, user_id: str) -> SavedBreaksOut:
    rows = (await db.scalars(
        select(SavedBreakRow).where(
            SavedBreakRow.user_id == user_id,
            SavedBreakRow.deleted_at.is_(None),
        )
    )).all()
    return SavedBreaksOut(
        breaks=[_to_dto(r) for r in rows], server_time=datetime.utcnow()
    )


@router.get("/v1/saved-breaks", response_model=SavedBreaksOut)
async def list_breaks(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> SavedBreaksOut:
    return await _current(db, user.id)


@router.post("/v1/saved-breaks/sync", response_model=SavedBreaksOut)
async def sync_breaks(
    body: SyncIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SavedBreaksOut:
    existing = {
        r.id: r for r in (await db.scalars(
            select(SavedBreakRow).where(SavedBreakRow.user_id == user.id)
        )).all()
    }
    for inc in body.breaks:
        row = existing.get(inc.id)
        if row is None:
            db.add(SavedBreakRow(
                user_id=user.id, id=inc.id, label=inc.label,
                start=inc.start, end=inc.end, pto_cost=inc.pto_cost,
                kind=inc.kind, updated_at=inc.updated_at, deleted_at=inc.deleted_at,
            ))
        elif inc.updated_at >= row.updated_at:
            # Last-write-wins: newer timestamp overwrites (tombstone included).
            row.label = inc.label
            row.start = inc.start
            row.end = inc.end
            row.pto_cost = inc.pto_cost
            row.kind = inc.kind
            row.updated_at = inc.updated_at
            row.deleted_at = inc.deleted_at
    await db.commit()
    return await _current(db, user.id)
