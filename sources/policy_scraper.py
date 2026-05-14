"""Detects workweek policy changes from news.

This solves the problem of hardcoded workweek defaults going stale.
Countries change their official workweek occasionally (Nepal 2026, UAE 2022,
Saudi Arabia 2013, etc.) — this scraper watches for those announcements,
extracts (country, effective_date, new_workweek), and persists them so the
planner can resolve the correct workweek for any given date.

Outputs records of the form:
    {
        "country": "NP",
        "effective_date": date(2026, 4, 5),
        "weekend_spec": "sat,sun",
        "source": "news",
        "headline": "Nepal Government Reintroduces Two-Day Weekly Holiday...",
        "link": "https://...",
        "confidence": "high|medium|low",
    }
"""
import re
from datetime import date
from typing import Optional
import feedparser

from ._news_utils import entry_pub_date


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=en&gl={gl}&ceid={gl}:en"
)
USER_AGENT = "Mozilla/5.0 (compatible; HolidaySandwicher/0.1)"


# Per-country queries that surface workweek policy changes
COUNTRY_QUERIES = {
    "NP": ["Nepal+weekly+holiday", "Nepal+workweek+change",
           "Nepal+two-day+weekend"],
    "JP": ["Japan+workweek+change", "Japan+four-day+workweek",
           "Japan+weekend+policy", "Japan+working+hours+reform"],
    "KR": ["Korea+four-day+workweek", "Korea+workweek+reform",
           "Korea+52-hour+workweek"],
    "SA": ["Saudi+Arabia+workweek", "Saudi+weekend+change"],
    "AE": ["UAE+workweek+change", "UAE+weekend+four-and-a-half-day"],
    "BD": ["Bangladesh+workweek", "Bangladesh+weekend+change"],
    "IL": ["Israel+workweek+change"],
}


# Phrase patterns that imply a specific new workweek.
# Each tuple: (regex, weekend_spec, confidence).
# The regexes allow up to 30 chars between the day-pair and the qualifier word
# so they catch "Saturday and Sunday as the weekly holiday", "Saturday and
# Sunday declared a weekend", etc.
PATTERNS = [
    (re.compile(
        r"saturday\s+and\s+sunday.{0,30}?(?:holiday|off|weekend|rest|leave)",
        re.IGNORECASE | re.DOTALL,
    ), "sat,sun", "high"),
    (re.compile(r"two[-\s]day\s+(?:weekly\s+)?(?:weekend|holiday)", re.IGNORECASE),
     "sat,sun", "medium"),
    (re.compile(r"five[-\s]day\s+(?:work)?week", re.IGNORECASE),
     "sat,sun", "medium"),
    (re.compile(
        r"friday\s+and\s+saturday.{0,30}?(?:holiday|off|weekend|rest|leave)",
        re.IGNORECASE | re.DOTALL,
    ), "fri,sat", "high"),
    (re.compile(
        r"saturday[-\s]only.{0,30}?(?:weekly\s+)?(?:holiday|weekend)",
        re.IGNORECASE,
    ), "sat", "high"),
    (re.compile(r"six[-\s]day\s+(?:work)?week", re.IGNORECASE), "sat", "medium"),
    (re.compile(r"sunday\s+(?:to|through)\s+thursday", re.IGNORECASE),
     "fri,sat", "high"),
]

# Effective-date phrases: "effective from X", "starting X", "from MONTH DD"
EFFECTIVE_DATE_PATTERNS = [
    re.compile(
        r"effective\s+(?:from\s+)?"
        r"([A-Z][a-z]+\s+\d{1,2}(?:,?\s+\d{4})?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:starting|from|with effect from)\s+"
        r"([A-Z][a-z]+\s+\d{1,2}(?:,?\s+\d{4})?)",
        re.IGNORECASE,
    ),
]

# Negation — proposals, debates, rejections shouldn't count
NEGATE_RE = re.compile(
    r"(propose|proposal|considering|debate|reject|withdrawn|cancel|reverse|"
    r"opposition|critic|may\s+|might\s+|could\s+)",
    re.IGNORECASE,
)

# Confirmation — actual decisions
CONFIRM_RE = re.compile(
    r"(announce|declared|approved|cabinet decision|implement|introduce|"
    r"reintroduce|adopt|gazette)",
    re.IGNORECASE,
)


def _detect_workweek(text: str) -> Optional[tuple[str, str]]:
    """Return (weekend_spec, confidence) if a workweek pattern is matched."""
    for pat, spec, conf in PATTERNS:
        if pat.search(text):
            return spec, conf
    return None


def _detect_effective_date(text: str, pub_date: Optional[date]) -> Optional[date]:
    """Try to extract an effective date; fall back to publish date."""
    # Future: parse the "effective from X" capture group properly.
    # For now we just use publish date — policy news typically reports
    # cabinet decisions on or after enactment.
    return pub_date


def fetch(country: str) -> list[dict]:
    """Scan recent news for workweek policy changes in the given country."""
    queries = COUNTRY_QUERIES.get(country, [])
    if not queries:
        return []

    results = []
    seen = set()
    for q in queries:
        url = GOOGLE_NEWS_RSS.format(query=q, gl=country)
        feed = feedparser.parse(url, agent=USER_AGENT)
        for entry in feed.entries[:30]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            blob = f"{title} {summary}"

            if NEGATE_RE.search(blob) and not CONFIRM_RE.search(blob):
                continue
            if not CONFIRM_RE.search(blob):
                continue

            detected = _detect_workweek(blob)
            if detected is None:
                continue
            weekend_spec, confidence = detected

            pub_date = entry_pub_date(entry)
            eff_date = _detect_effective_date(blob, pub_date)
            if eff_date is None:
                continue

            key = (country, eff_date.isoformat(), weekend_spec)
            if key in seen:
                continue
            seen.add(key)

            results.append({
                "country": country,
                "effective_date": eff_date,
                "weekend_spec": weekend_spec,
                "source": "news",
                "headline": title,
                "link": entry.get("link"),
                "confidence": confidence,
            })
    return results
