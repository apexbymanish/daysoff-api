"""Google ID-token verification.

Isolated in its own module so tests can monkeypatch `verify_google_id_token`
without touching Google's servers.
"""
from __future__ import annotations

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token


def verify_google_id_token(token: str) -> dict:
    """Verify a Google-issued ID token against Google's public keys.

    Returns the decoded claims (sub, email, email_verified, aud, name, …).
    Raises ValueError if the token is invalid/expired or not from Google.
    Audience is checked by the caller against the configured client IDs.
    """
    request = google_requests.Request()
    return google_id_token.verify_oauth2_token(token, request)
