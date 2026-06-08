"""Tests for Google sign-in (/v1/auth/google) with a monkeypatched verifier."""
import uuid

import pytest
from fastapi.testclient import TestClient

import api.google_auth as google_auth
from api.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _payload(sub, email, *, verified=True, aud="test-client-id", name="G User"):
    return {
        "sub": sub, "email": email, "email_verified": verified,
        "aud": aud, "iss": "https://accounts.google.com", "name": name,
    }


def _patch(monkeypatch, payload):
    monkeypatch.setattr(google_auth, "verify_google_id_token",
                        lambda token: payload)


def _auth(tok):
    return {"Authorization": f"Bearer {tok}"}


def test_google_signin_creates_user(client, monkeypatch):
    sub = uuid.uuid4().hex
    email = f"g{sub[:8]}@example.com"
    _patch(monkeypatch, _payload(sub, email))
    r = client.post("/v1/auth/google", json={"id_token": "x"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["user"]["email"] == email
    # the minted access token works
    me = client.get("/v1/me", headers=_auth(body["access_token"]))
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_google_signin_is_idempotent(client, monkeypatch):
    sub = uuid.uuid4().hex
    email = f"g{sub[:8]}@example.com"
    _patch(monkeypatch, _payload(sub, email))
    a = client.post("/v1/auth/google", json={"id_token": "x"}).json()
    b = client.post("/v1/auth/google", json={"id_token": "x"}).json()
    assert a["user"]["id"] == b["user"]["id"]


def test_google_links_to_existing_email_account(client, monkeypatch):
    sub = uuid.uuid4().hex
    email = f"g{sub[:8]}@example.com"
    reg = client.post("/v1/auth/register",
                      json={"email": email, "password": "hunter2pw"})
    assert reg.status_code == 201
    existing_id = reg.json()["user"]["id"]

    _patch(monkeypatch, _payload(sub, email))
    g = client.post("/v1/auth/google", json={"id_token": "x"})
    assert g.status_code == 200
    assert g.json()["user"]["id"] == existing_id  # linked, not duplicated


def test_wrong_audience_rejected(client, monkeypatch):
    _patch(monkeypatch, _payload(uuid.uuid4().hex, "x@example.com",
                                 aud="some-other-client"))
    r = client.post("/v1/auth/google", json={"id_token": "x"})
    assert r.status_code == 401
    assert "audience" in r.json()["detail"].lower()


def test_unverified_email_rejected(client, monkeypatch):
    _patch(monkeypatch, _payload(uuid.uuid4().hex, "x@example.com",
                                 verified=False))
    r = client.post("/v1/auth/google", json={"id_token": "x"})
    assert r.status_code == 401


def test_invalid_token_rejected(client, monkeypatch):
    def boom(token):
        raise ValueError("bad token")
    monkeypatch.setattr(google_auth, "verify_google_id_token", boom)
    r = client.post("/v1/auth/google", json={"id_token": "x"})
    assert r.status_code == 401
