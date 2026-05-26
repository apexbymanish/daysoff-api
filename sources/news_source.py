"""News-source dispatcher.

Picks the right country-specific scraper based on the requested country.
Currently supports KR and NP. Adding a new country = add a `news_<cc>.py`
module with a `fetch(year)` function and register it below.
"""
from . import news_kr, news_np


_DISPATCHERS = {
    "KR": news_kr.fetch,
    "NP": news_np.fetch,
}


def supported_countries() -> set[str]:
    """Return the ISO-2 codes that have a registered news scraper."""
    return set(_DISPATCHERS)


def fetch(year: int, country: str = "KR") -> list[dict]:
    fn = _DISPATCHERS.get(country)
    if fn is None:
        return []
    try:
        return fn(year)
    except Exception as e:
        print(f"[warn] news scraper for {country} failed: {e}")
        return []
