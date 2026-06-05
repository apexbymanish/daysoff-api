"""Baseline holidays from the `holidays` PyPI package (offline, rule-based)."""
from datetime import date
import holidays


def _localized_names(country: str, year: int) -> dict[date, str]:
    """Map date→native-language name when the country has a non-English
    default language; otherwise an empty map (callers fall back to English)."""
    inst = holidays.country_holidays(country, years=year)
    lang = getattr(inst, "default_language", None)
    if not lang or lang.split("_")[0] == "en":
        return {}
    try:
        localized = holidays.country_holidays(country, years=year, language=lang)
        return dict(localized.items())
    except (NotImplementedError, KeyError, ValueError):
        return {}


def fetch(year: int, country: str = "KR") -> list[dict]:
    py_holidays = holidays.country_holidays(country, years=year)
    local = _localized_names(country, year)
    return [
        {
            "date": d,
            "name": name,
            "name_local": local.get(d),
            "country": country,
            "source": "library",
        }
        for d, name in sorted(py_holidays.items())
    ]
