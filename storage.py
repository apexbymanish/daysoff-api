"""SQLite persistence.

Two tables:
  - holidays: detected holiday dates from any source (library/news/gov_api)
  - workweek_policies: policy changes that affect the off-day calendar
    (e.g., Nepal moved to Sat+Sun weekend on 2026-04-05)
"""
import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "holidays.db"


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("""
        CREATE TABLE IF NOT EXISTS holidays (
            date TEXT NOT NULL,
            country TEXT NOT NULL,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            PRIMARY KEY (date, country, source)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS workweek_policies (
            country TEXT NOT NULL,
            effective_date TEXT NOT NULL,
            weekend_spec TEXT NOT NULL,
            source TEXT NOT NULL,
            confidence TEXT NOT NULL,
            headline TEXT,
            link TEXT,
            first_seen TEXT NOT NULL,
            PRIMARY KEY (country, effective_date, weekend_spec)
        )
    """)
    return c


def upsert(records: list[dict]) -> list[dict]:
    """Insert holiday records, returning the ones that were newly seen."""
    today = date.today().isoformat()
    new_records = []
    with _conn() as c:
        for r in records:
            cur = c.execute(
                "SELECT 1 FROM holidays WHERE date=? AND country=? AND source=?",
                (r["date"].isoformat(), r["country"], r["source"]),
            )
            if cur.fetchone() is None:
                new_records.append(r)
            c.execute(
                """INSERT OR REPLACE INTO holidays
                   (date, country, name, source, first_seen)
                   VALUES (?, ?, ?, ?,
                       COALESCE((SELECT first_seen FROM holidays
                                 WHERE date=? AND country=? AND source=?), ?))""",
                (
                    r["date"].isoformat(), r["country"], r["name"], r["source"],
                    r["date"].isoformat(), r["country"], r["source"], today,
                ),
            )
    return new_records


def upsert_workweek_policies(records: list[dict]) -> list[dict]:
    """Insert detected workweek policy records."""
    today = date.today().isoformat()
    new_records = []
    with _conn() as c:
        for r in records:
            eff = r["effective_date"].isoformat()
            cur = c.execute(
                "SELECT 1 FROM workweek_policies WHERE country=? "
                "AND effective_date=? AND weekend_spec=?",
                (r["country"], eff, r["weekend_spec"]),
            )
            if cur.fetchone() is None:
                new_records.append(r)
            c.execute(
                """INSERT OR REPLACE INTO workweek_policies
                   (country, effective_date, weekend_spec, source, confidence,
                    headline, link, first_seen)
                   VALUES (?, ?, ?, ?, ?, ?, ?,
                       COALESCE((SELECT first_seen FROM workweek_policies
                                 WHERE country=? AND effective_date=?
                                 AND weekend_spec=?), ?))""",
                (
                    r["country"], eff, r["weekend_spec"], r["source"],
                    r["confidence"], r.get("headline"), r.get("link"),
                    r["country"], eff, r["weekend_spec"], today,
                ),
            )
    return new_records


def latest_policy_age_days(country: str) -> Optional[int]:
    """Days since the most recent workweek policy for `country` was first seen.
    Returns None if no policies are on record for that country.
    """
    with _conn() as c:
        cur = c.execute(
            "SELECT MAX(first_seen) FROM workweek_policies WHERE country=?",
            (country,),
        )
        row = cur.fetchone()
    if not row or not row[0]:
        return None
    return (date.today() - date.fromisoformat(row[0])).days


def resolve_workweek(country: str, target: date) -> Optional[dict]:
    """Find the workweek policy in effect for `country` on `target`.

    Returns the most recent policy with effective_date <= target.
    Returns None if no policy is on record.
    """
    with _conn() as c:
        cur = c.execute(
            """SELECT effective_date, weekend_spec, source, confidence,
                      headline, link, first_seen
               FROM workweek_policies
               WHERE country=? AND effective_date <= ?
               ORDER BY effective_date DESC LIMIT 1""",
            (country, target.isoformat()),
        )
        row = cur.fetchone()
    if row is None:
        return None
    eff_str, weekend_spec, source, conf, headline, link, first_seen = row
    eff = date.fromisoformat(eff_str)
    return {
        "country": country,
        "effective_date": eff,
        "weekend_spec": weekend_spec,
        "source": source,
        "confidence": conf,
        "headline": headline,
        "link": link,
        "first_seen": first_seen,
    }
