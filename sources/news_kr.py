"""News scraper for Korea — surfaces newly-announced temporary holidays (임시공휴일).

Korean governments sometimes designate a one-off red day weeks in advance,
before the `holidays` library or gov API is updated. We watch Google News RSS
for the Korean keyword and try to extract a date.
"""
import re
from datetime import date
import feedparser

from ._news_utils import entry_pub_date, resolve_year_for_bare_date

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=ko&gl=KR&ceid=KR:ko"
)
USER_AGENT = "Mozilla/5.0 (compatible; HolidaySandwicher/0.1)"

DATE_PATTERNS = [
    re.compile(r"(20\d{2})[년\-/.]\s*(\d{1,2})[월\-/.]\s*(\d{1,2})[일]?"),
    re.compile(r"(\d{1,2})[월]\s*(\d{1,2})[일]"),  # year inferred
]

CONFIRM_RE = re.compile(r"(지정|확정|결정|발표)")
NEGATE_RE = re.compile(r"(무산|검토|취소|불발|반대)")


def _parse_dates(text: str, pub_date, fallback_year: int) -> list[date]:
    """Extract dates. For bare month-day patterns, anchor year using pub_date."""
    found = []
    for idx, pat in enumerate(DATE_PATTERNS):
        for m in pat.finditer(text):
            try:
                if len(m.groups()) == 3:
                    y, mo, d = (int(x) for x in m.groups())
                else:
                    mo, d = (int(x) for x in m.groups())
                    y = resolve_year_for_bare_date(mo, d, pub_date, fallback_year)
                found.append(date(y, mo, d))
            except ValueError:
                continue
    return found


def fetch(year: int) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(query=f"임시공휴일+{year}")
    feed = feedparser.parse(url, agent=USER_AGENT)

    today = date.today()
    results = []
    seen = set()
    for entry in feed.entries[:30]:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        blob = f"{title} {summary}"
        if NEGATE_RE.search(blob):
            continue
        pub_date = entry_pub_date(entry)
        for d in _parse_dates(blob, pub_date, year):
            if d.year != year or d < today or d in seen:
                continue
            seen.add(d)
            results.append({
                "date": d,
                "name": "임시공휴일 (news-detected)",
                "country": "KR",
                "source": "news",
                "headline": title,
                "link": entry.get("link"),
                "article_published": pub_date.isoformat() if pub_date else None,
            })
    return results
