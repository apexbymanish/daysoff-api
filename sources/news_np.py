"""News scraper for Nepal — surfaces newly-announced public holidays.

Nepal frequently declares ad-hoc holidays:
- Election days (federal/provincial/local)
- Mourning days (deaths of officials)
- Local festivals (Indra Jatra in Kathmandu valley, Yenya, etc.)
- Strikes and bandhs that close offices

We watch Google News (Nepali locale) for relevant keywords and extract Gregorian
dates from headlines. Nepali news typically cites both BS and AD dates.
"""
import re
from datetime import date
import feedparser

from ._news_utils import entry_pub_date, resolve_year_for_bare_date

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=ne&gl=NP&ceid=NP:ne"
)
USER_AGENT = "Mozilla/5.0 (compatible; HolidaySandwicher/0.1)"

# Multiple queries cover Devanagari + English-language Nepali press
QUERIES = [
    "सार्वजनिक+बिदा+घोषणा",
    "अतिरिक्त+बिदा",
    "Nepal+government+public+holiday+declared",
]

# Confirmation vs negation patterns
CONFIRM_RE = re.compile(
    r"(घोषणा|तोकिएको|declared|announces|announced|gazetted)",
    re.IGNORECASE,
)
NEGATE_RE = re.compile(
    r"(छैन|रद्द|cancelled|rejected|denied|withdrawn)",
    re.IGNORECASE,
)

# Require Nepal context to avoid Indian-state false positives
NEPAL_CONTEXT_RE = re.compile(
    r"(Nepal|Kathmandu|Pokhara|Lalitpur|Bhaktapur|Biratnagar|Birgunj|"
    r"Janakpur|Dharan|Butwal|Hetauda|Nepalgunj|"
    r"Madhes|Bagmati|Gandaki|Lumbini|Karnali|Sudurpaschim|Koshi|"
    r"नेपाल|काठमाडौं|पोखरा|"
    r"\.np/)",
    re.IGNORECASE,
)
# Strong negative signal — Indian state names that often appear in similar articles
NON_NEPAL_RE = re.compile(
    r"\b(Uttar Pradesh|Bihar|Maharashtra|Tamil Nadu|Karnataka|"
    r"Gujarat|Rajasthan|Punjab|Haryana|West Bengal|Kerala|"
    r"Indian state|India announced|UP government|"
    r"Pakistan|Bangladesh|Bhutan|Sri Lanka)\b",
    re.IGNORECASE,
)

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

MONTH_NAMES = (
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
)

DATE_PATTERNS = [
    # ISO 2026-10-05
    re.compile(r"(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})"),
    # "5 October 2026" / "5 October" (year optional)
    re.compile(
        rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_NAMES})(?:[,\s]+(20\d{{2}}))?",
        re.IGNORECASE,
    ),
    # "October 5, 2026" / "October 5" (year optional)
    re.compile(
        rf"({MONTH_NAMES})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:[,\s]+(20\d{{2}}))?",
        re.IGNORECASE,
    ),
]


def _parse_dates(text: str, pub_date, fallback_year: int) -> list[date]:
    """Extract dates from text. For bare month-day matches, anchor the year
    to the article's publish date.
    """
    found = []
    # ISO 2026-10-05
    for m in DATE_PATTERNS[0].finditer(text):
        try:
            found.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        except ValueError:
            pass
    # day-month-year (year optional)
    for m in DATE_PATTERNS[1].finditer(text):
        try:
            d = int(m.group(1))
            mo = MONTHS[m.group(2).lower()]
            if m.group(3):
                y = int(m.group(3))
            else:
                y = resolve_year_for_bare_date(mo, d, pub_date, fallback_year)
            found.append(date(y, mo, d))
        except (ValueError, KeyError):
            pass
    # month-day-year (year optional)
    for m in DATE_PATTERNS[2].finditer(text):
        try:
            mo = MONTHS[m.group(1).lower()]
            d = int(m.group(2))
            if m.group(3):
                y = int(m.group(3))
            else:
                y = resolve_year_for_bare_date(mo, d, pub_date, fallback_year)
            found.append(date(y, mo, d))
        except (ValueError, KeyError):
            pass
    return found


def fetch(year: int) -> list[dict]:
    today = date.today()
    results = []
    seen = set()
    for query in QUERIES:
        url = GOOGLE_NEWS_RSS.format(query=query)
        feed = feedparser.parse(url, agent=USER_AGENT)
        for entry in feed.entries[:25]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            blob = f"{title} {summary}"
            link = entry.get("link", "")
            full_blob = f"{blob} {link}"
            if NEGATE_RE.search(blob):
                continue
            if NON_NEPAL_RE.search(blob):
                continue
            if not NEPAL_CONTEXT_RE.search(full_blob):
                continue
            if not CONFIRM_RE.search(blob):
                continue
            pub_date = entry_pub_date(entry)
            for d in _parse_dates(blob, pub_date, year):
                if d.year != year or d < today or d in seen:
                    continue
                seen.add(d)
                results.append({
                    "date": d,
                    "name": "Government-declared holiday (news-detected)",
                    "country": "NP",
                    "source": "news",
                    "headline": title,
                    "link": entry.get("link"),
                    "article_published": pub_date.isoformat() if pub_date else None,
                })
    return results
