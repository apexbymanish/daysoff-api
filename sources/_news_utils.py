"""Shared helpers for news-based scrapers."""
from datetime import date, datetime
from time import struct_time
from typing import Optional


def entry_pub_date(entry) -> Optional[date]:
    """Extract publish date from a feedparser entry, if available."""
    parsed: Optional[struct_time] = entry.get("published_parsed") \
        or entry.get("updated_parsed")
    if parsed is None:
        return None
    try:
        return date(parsed.tm_year, parsed.tm_mon, parsed.tm_mday)
    except (ValueError, AttributeError):
        return None


def resolve_year_for_bare_date(month: int, day: int,
                               pub_date: Optional[date],
                               fallback_year: int) -> int:
    """Given a 'month-day' with no year, pick the most plausible year.

    Heuristic:
      - If we know the article's publish date, the holiday is almost always
        within ±200 days of publish (~6 months). Pick the year that makes the
        resolved date closest to publish date.
      - If publish date unknown, use fallback_year.
    """
    if pub_date is None:
        return fallback_year

    candidates = []
    for yr in (pub_date.year - 1, pub_date.year, pub_date.year + 1):
        try:
            d = date(yr, month, day)
        except ValueError:
            continue
        candidates.append((abs((d - pub_date).days), yr))
    if not candidates:
        return fallback_year
    candidates.sort()
    return candidates[0][1]
