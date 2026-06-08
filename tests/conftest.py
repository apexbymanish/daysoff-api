"""Test setup: isolate the accounts DB to a throwaway SQLite file and set a
deterministic JWT secret BEFORE any api module imports (so the engine + settings
pick these up)."""
import os
import pathlib
import tempfile

_TMP_DB = pathlib.Path(tempfile.gettempdir()) / "daysoff_test_accounts.db"
if _TMP_DB.exists():
    _TMP_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP_DB}"
os.environ["DAYSOFF_JWT_SECRET"] = "test-secret-not-for-prod-0123456789abcdef"
os.environ["GOOGLE_CLIENT_IDS"] = "test-client-id"
