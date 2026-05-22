"""Service layer — adapts existing modules to API response shapes.

This file contains no holiday logic of its own. It must only call into
sources/, sandwich, storage, and planner. If a needed function is missing
in those modules, add it there — not here.
"""
import holidays
from datetime import date as _date

from sources import library_source, news_source


# Hand-curated names for the codes we actively support. Codes outside this
# map fall back to the ISO-2 code itself in responses. Future: swap for
# `pycountry` when its 3 MB footprint is justified.
COUNTRY_NAMES: dict[str, str] = {
    "KR": "South Korea",
    "NP": "Nepal",
    "JP": "Japan",
    "US": "United States",
    "GB": "United Kingdom",
    "IN": "India",
    "PH": "Philippines",
    "ID": "Indonesia",
    "VN": "Vietnam",
    "TH": "Thailand",
    "MY": "Malaysia",
    "SG": "Singapore",
    "CN": "China",
    "DE": "Germany",
    "FR": "France",
    "BR": "Brazil",
    "AU": "Australia",
    "CA": "Canada",
    "SA": "Saudi Arabia",
    "AE": "United Arab Emirates",
    "BD": "Bangladesh",
    "IL": "Israel",
}


def supported_country_codes() -> list[str]:
    """ISO-2 codes the `holidays` library can serve, sorted."""
    return sorted(c for c in holidays.list_supported_countries().keys() if len(c) == 2)


def list_countries() -> list[dict]:
    """Return the country-info records used by GET /v1/countries."""
    news_set = news_source.supported_countries()
    return [
        {
            "code": code,
            "name": COUNTRY_NAMES.get(code, code),
            "news_enriched": code in news_set,
        }
        for code in supported_country_codes()
    ]


YEAR_MIN = 1900
YEAR_MAX = 2100


class ApiInputError(ValueError):
    """Raised by the service layer when the caller passes bad input.

    Mapped to HTTP 400 by api/main.py.
    """


def _validate_country(code: str) -> str:
    cc = code.upper()
    if cc not in supported_country_codes():
        raise ApiInputError(f"country '{cc}' not supported by holidays library")
    return cc


def _validate_year(year: int) -> int:
    if year < YEAR_MIN or year > YEAR_MAX:
        raise ApiInputError(f"year {year} out of range [{YEAR_MIN}, {YEAR_MAX}]")
    return year


def get_holidays(country: str, year: int, from_today: bool = False) -> list[dict]:
    """Library + news union for one country/year, deduped on (date, name)."""
    cc = _validate_country(country)
    _validate_year(year)

    lib_records = library_source.fetch(year, cc)
    news_records = news_source.fetch(year, cc) if cc in news_source.supported_countries() else []

    seen: set[tuple] = set()
    merged: list[dict] = []
    for r in lib_records + news_records:
        key = (r["date"], r["name"])
        if key in seen:
            continue
        seen.add(key)
        merged.append({
            "date": r["date"],
            "name": r["name"],
            "source": r["source"],
        })
    merged.sort(key=lambda r: r["date"])

    if from_today:
        today = _date.today()
        merged = [r for r in merged if r["date"] >= today]
    return merged


def compare_countries(countries_csv: str, year: int) -> dict:
    """Return shared dates + per-country uniques for the listed countries."""
    raw_codes = [c.strip() for c in countries_csv.split(",") if c.strip()]
    if len(raw_codes) < 2:
        raise ApiInputError("compare needs at least 2 countries")
    codes = [_validate_country(c) for c in raw_codes]
    _validate_year(year)

    # Build (date -> name) maps per country. Use the FIRST country's name
    # when a date is shared across all of them.
    per_country: dict[str, dict] = {}
    for cc in codes:
        recs = library_source.fetch(year, cc)
        per_country[cc] = {r["date"]: r["name"] for r in recs}

    # Shared = strict N-way intersection.
    intersect = set(per_country[codes[0]].keys())
    for cc in codes[1:]:
        intersect &= set(per_country[cc].keys())
    shared = [
        {"date": d, "name": per_country[codes[0]][d]}
        for d in sorted(intersect)
    ]

    # only[CC] = dates in CC but no other listed country.
    only: dict[str, list[dict]] = {}
    for cc in codes:
        other_union: set = set()
        for other_cc in codes:
            if other_cc == cc:
                continue
            other_union |= set(per_country[other_cc].keys())
        unique_dates = sorted(set(per_country[cc].keys()) - other_union)
        only[cc] = [{"date": d, "name": per_country[cc][d]} for d in unique_dates]

    return {"year": year, "countries": codes, "shared": shared, "only": only}
