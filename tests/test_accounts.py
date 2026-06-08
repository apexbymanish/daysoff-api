"""Tests for accounts (email/password) + saved-breaks sync."""
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture()
def client():
    # `with` runs the lifespan, which create_all()s the accounts tables.
    with TestClient(app) as c:
        yield c


def _email() -> str:
    return f"u{uuid.uuid4().hex[:12]}@example.com"


def _register(client, email=None, password="hunter2pw"):
    email = email or _email()
    r = client.post("/v1/auth/register",
                    json={"email": email, "password": password})
    return email, password, r


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── auth ──────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_login_me_happy_path(self, client):
        email, password, r = _register(client)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == email
        access = body["access_token"]

        me = client.get("/v1/me", headers=_auth(access))
        assert me.status_code == 200
        assert me.json()["email"] == email

        login = client.post("/v1/auth/login",
                            json={"email": email, "password": password})
        assert login.status_code == 200
        assert login.json()["user"]["id"] == body["user"]["id"]

    def test_duplicate_email_409(self, client):
        email, _, r = _register(client)
        assert r.status_code == 201
        _, _, r2 = _register(client, email=email)
        assert r2.status_code == 409

    def test_short_password_422(self, client):
        r = client.post("/v1/auth/register",
                        json={"email": _email(), "password": "short"})
        assert r.status_code == 422

    def test_wrong_password_401(self, client):
        email, _, _ = _register(client)
        r = client.post("/v1/auth/login",
                        json={"email": email, "password": "wrongpassword"})
        assert r.status_code == 401

    def test_me_requires_token(self, client):
        assert client.get("/v1/me").status_code == 401
        assert client.get("/v1/me", headers=_auth("garbage")).status_code == 401

    def test_refresh_rotates_and_revokes_old(self, client):
        _, _, r = _register(client)
        refresh = r.json()["refresh_token"]
        first = client.post("/v1/auth/refresh", json={"refresh_token": refresh})
        assert first.status_code == 200
        new_refresh = first.json()["refresh_token"]
        assert new_refresh != refresh
        # old refresh now revoked
        assert client.post("/v1/auth/refresh",
                          json={"refresh_token": refresh}).status_code == 401
        # new refresh works
        assert client.post("/v1/auth/refresh",
                          json={"refresh_token": new_refresh}).status_code == 200

    def test_logout_revokes_refresh(self, client):
        _, _, r = _register(client)
        refresh = r.json()["refresh_token"]
        assert client.post("/v1/auth/logout",
                          json={"refresh_token": refresh}).status_code == 204
        assert client.post("/v1/auth/refresh",
                          json={"refresh_token": refresh}).status_code == 401

    def test_delete_me_removes_account(self, client):
        email, password, r = _register(client)
        access = r.json()["access_token"]
        assert client.delete("/v1/me", headers=_auth(access)).status_code == 204
        # can't log in anymore
        assert client.post("/v1/auth/login",
                          json={"email": email, "password": password}).status_code == 401


# ── saved-breaks sync ───────────────────────────────────────────────────────────

def _break(bid, updated_at, deleted_at=None, label="Chuseok", pto=2):
    return {
        "id": bid, "label": label,
        "start": "2026-09-22", "end": "2026-09-28",
        "pto_cost": pto, "kind": "buffet",
        "updated_at": updated_at.isoformat(),
        "deleted_at": deleted_at.isoformat() if deleted_at else None,
    }


class TestSync:
    def test_push_then_list(self, client):
        _, _, r = _register(client)
        h = _auth(r.json()["access_token"])
        now = datetime(2026, 6, 8, 10, 0, 0)
        resp = client.post("/v1/saved-breaks/sync",
                          json={"breaks": [_break("b1", now)]}, headers=h)
        assert resp.status_code == 200
        assert [b["id"] for b in resp.json()["breaks"]] == ["b1"]
        got = client.get("/v1/saved-breaks", headers=h)
        assert [b["id"] for b in got.json()["breaks"]] == ["b1"]

    def test_last_write_wins(self, client):
        _, _, r = _register(client)
        h = _auth(r.json()["access_token"])
        old = datetime(2026, 6, 8, 10, 0, 0)
        new = datetime(2026, 6, 8, 12, 0, 0)
        client.post("/v1/saved-breaks/sync",
                   json={"breaks": [_break("b1", new, label="NEW")]}, headers=h)
        # older incoming must NOT overwrite the newer stored label
        client.post("/v1/saved-breaks/sync",
                   json={"breaks": [_break("b1", old, label="OLD")]}, headers=h)
        got = client.get("/v1/saved-breaks", headers=h).json()["breaks"]
        assert got[0]["label"] == "NEW"

    def test_tombstone_deletes(self, client):
        _, _, r = _register(client)
        h = _auth(r.json()["access_token"])
        t0 = datetime(2026, 6, 8, 10, 0, 0)
        t1 = datetime(2026, 6, 8, 11, 0, 0)
        client.post("/v1/saved-breaks/sync",
                   json={"breaks": [_break("b1", t0)]}, headers=h)
        client.post("/v1/saved-breaks/sync",
                   json={"breaks": [_break("b1", t1, deleted_at=t1)]}, headers=h)
        got = client.get("/v1/saved-breaks", headers=h).json()["breaks"]
        assert got == []

    def test_user_isolation(self, client):
        _, _, ra = _register(client)
        _, _, rb = _register(client)
        ha = _auth(ra.json()["access_token"])
        hb = _auth(rb.json()["access_token"])
        now = datetime(2026, 6, 8, 10, 0, 0)
        client.post("/v1/saved-breaks/sync",
                   json={"breaks": [_break("shared-id", now, label="A's")]}, headers=ha)
        # B has nothing despite the same break id existing for A
        assert client.get("/v1/saved-breaks", headers=hb).json()["breaks"] == []

    def test_sync_requires_auth(self, client):
        assert client.get("/v1/saved-breaks").status_code == 401
        assert client.post("/v1/saved-breaks/sync", json={"breaks": []}).status_code == 401
