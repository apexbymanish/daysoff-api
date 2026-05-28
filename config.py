"""User preference store.

Designed as an interface so the storage backend can evolve without changing
callers. Today: JSON file. Later: SQLite multi-user, or a REST API.

Usage:
    import config
    budget = config.get("budget")
    config.save({"budget": 15, "country": "KR"})

The backend is selected by the DAYSOFF_BACKEND environment variable
(default: "json"). user_id is accepted everywhere — defaults to "default"
in single-user mode; will be real when we add auth.

Stable keys (documented schema — don't invent new ones casually):
    budget       int     — number of PTO days available
    country      str     — ISO 2-letter country code (KR, NP, JP, ...)
    workweeks    dict    — {country_code: workweek_spec}, e.g. {"KR": "wed,thu"}
    visit        str     — default destination country for --visit overlay
"""
import json
import os
import stat
from pathlib import Path
from typing import Any, Optional


DEFAULT_USER = "default"
CONFIG_DIR = Path.home() / ".daysoff"
JSON_PATH = CONFIG_DIR / "config.json"
# One-time migration from the old project name
_LEGACY_DIR = Path.home() / ".holidaySandwicher"


# ─────────────────────────────────────────────────────────────────────────
# Backend interface
# ─────────────────────────────────────────────────────────────────────────

class ConfigBackend:
    """All backends implement this interface."""
    def load(self, user_id: str) -> dict:
        raise NotImplementedError

    def save(self, updates: dict, user_id: str) -> None:
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────────────────
# JSON backend (Stage 1 — today)
# ─────────────────────────────────────────────────────────────────────────

class JsonBackend(ConfigBackend):
    """Plain JSON file at ~/.daysoff/config.json.

    Multi-user is faked: each user_id gets its own top-level object. For
    single-user CLI use, everyone reads/writes under DEFAULT_USER.
    """
    def __init__(self, path: Path = JSON_PATH):
        self.path = path

    def _read_all(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_all(self, data: dict) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2))
        # chmod 600 — readable only by owner
        try:
            os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass  # non-POSIX filesystems can ignore this

    def load(self, user_id: str) -> dict:
        return self._read_all().get(user_id, {})

    def save(self, updates: dict, user_id: str) -> None:
        all_data = self._read_all()
        current = all_data.get(user_id, {})
        # Merge nested dicts (e.g. "workweeks") instead of overwriting wholesale
        for k, v in updates.items():
            if v is None:
                continue
            if isinstance(v, dict) and isinstance(current.get(k), dict):
                current[k] = {**current[k], **v}
            else:
                current[k] = v
        all_data[user_id] = current
        self._write_all(all_data)


# ─────────────────────────────────────────────────────────────────────────
# SQLite backend (Stage 2 — when we go multi-user on one machine)
# ─────────────────────────────────────────────────────────────────────────

class SqliteBackend(ConfigBackend):
    """Reads/writes the user_preferences table in storage.py's DB.

    Stub for now — implement when Stage 2 is needed.
    """
    def load(self, user_id: str) -> dict:
        raise NotImplementedError("SqliteBackend not yet implemented")

    def save(self, updates: dict, user_id: str) -> None:
        raise NotImplementedError("SqliteBackend not yet implemented")


# ─────────────────────────────────────────────────────────────────────────
# API backend (Stage 3 — when there's a server)
# ─────────────────────────────────────────────────────────────────────────

class ApiBackend(ConfigBackend):
    """Talks to a REST API. Auth token comes from ~/.daysoff/auth.json.

    Stub for now — implement when Stage 3 is needed.
    """
    def load(self, user_id: str) -> dict:
        raise NotImplementedError("ApiBackend not yet implemented")

    def save(self, updates: dict, user_id: str) -> None:
        raise NotImplementedError("ApiBackend not yet implemented")


# ─────────────────────────────────────────────────────────────────────────
# Module-level facade — what callers use
# ─────────────────────────────────────────────────────────────────────────

def _migrate_legacy_config() -> None:
    """One-time migration from ~/.holidaySandwicher → ~/.daysoff."""
    if JSON_PATH.exists() or not _LEGACY_DIR.exists():
        return
    legacy_file = _LEGACY_DIR / "config.json"
    if not legacy_file.exists():
        return
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(legacy_file.read_text())
    try:
        os.chmod(JSON_PATH, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def _make_backend() -> ConfigBackend:
    # Accept the legacy env var for one release as a courtesy
    name = os.environ.get("DAYSOFF_BACKEND",
                          os.environ.get("HOLIDAY_BACKEND", "json")).lower()
    if name == "json":
        _migrate_legacy_config()
        return JsonBackend()
    if name == "sqlite":
        return SqliteBackend()
    if name == "api":
        return ApiBackend()
    raise ValueError(f"Unknown DAYSOFF_BACKEND: {name}")


_backend: ConfigBackend = _make_backend()


def load(user_id: str = DEFAULT_USER) -> dict:
    """Return all preferences for the user."""
    return _backend.load(user_id)


def get(key: str, default: Any = None, user_id: str = DEFAULT_USER) -> Any:
    """Return a single preference value, or `default` if not set."""
    return _backend.load(user_id).get(key, default)


def save(updates: dict, user_id: str = DEFAULT_USER) -> None:
    """Merge `updates` into the user's preferences and persist."""
    _backend.save(updates, user_id)


def reset_backend(backend: Optional[ConfigBackend] = None) -> None:
    """Swap the backend (useful for tests). If None, re-reads env var."""
    global _backend
    _backend = backend or _make_backend()
