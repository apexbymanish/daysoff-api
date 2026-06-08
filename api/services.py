"""Service layer — adapts existing modules to API response shapes.

This file contains no holiday logic of its own. It must only call into
sources/, sandwich, storage, and planner. If a needed function is missing
in those modules, add it there — not here.
"""
from __future__ import annotations

from datetime import date as _date

import holidays

import sandwich
from planner import (
    WEEKDAY_MAP, WORKWEEK_FALLBACKS, candidate_breaks, compute_calendar,
    daterange, parse_workweek,
)
from sources import library_source, news_source
from storage import resolve_workweek


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
            "name_local": r.get("name_local"),
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
    # Dedupe while preserving order. KR,KR would otherwise pass validation
    # and produce a misleading "intersection" against itself.
    codes = list(dict.fromkeys(_validate_country(c) for c in raw_codes))
    if len(codes) < 2:
        raise ApiInputError("compare needs at least 2 distinct countries")
    _validate_year(year)

    # Build (date -> name) maps per country. Use the FIRST country's name
    # when a date is shared across all of them.
    per_country: dict[str, dict] = {}
    for cc in codes:
        recs = library_source.fetch(year, cc)
        per_country[cc] = {r["date"]: r["name"] for r in recs}

    # Shared = strict N-way intersection.
    intersect = set(per_country[codes[0]])
    for cc in codes[1:]:
        intersect &= per_country[cc].keys()
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
            other_union |= per_country[other_cc].keys()
        unique_dates = sorted(set(per_country[cc]) - other_union)
        only[cc] = [{"date": d, "name": per_country[cc][d]} for d in unique_dates]

    return {"year": year, "countries": codes, "shared": shared, "only": only}


def _set_to_day_names(weekend_days: set[int]) -> list[str]:
    """{5, 6} -> ['sat', 'sun'] (sorted)."""
    inverse = {v: k for k, v in WEEKDAY_MAP.items()}
    return [inverse[i] for i in sorted(weekend_days)]


def _resolve_workweek(country: str, workweek: str | None
                      ) -> tuple[set[int], list[str], str]:
    """Return (weekend_days_int_set, weekend_days_str_list, source_string).

    Cascade: explicit param → most recent policy → hardcoded fallback → 400.
    Shared between /v1/sandwiches and /v1/plan.
    """
    if workweek:
        try:
            wk_set = parse_workweek(workweek)
        except KeyError as e:
            raise ApiInputError(f"invalid workweek token: {e}")
        return wk_set, _set_to_day_names(wk_set), "user"

    policy = resolve_workweek(country, _date.today())
    if policy:
        wk_set = parse_workweek(policy["weekend_spec"])
        src = (f"saved-policy:{policy['effective_date']}:"
               f"{policy['confidence']}")
        return wk_set, _set_to_day_names(wk_set), src

    if country in WORKWEEK_FALLBACKS:
        wk_set = parse_workweek(WORKWEEK_FALLBACKS[country])
        return wk_set, _set_to_day_names(wk_set), "hardcoded-fallback"

    raise ApiInputError(
        f"no workweek on record for {country}; pass ?workweek=sat,sun"
    )


_WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_sandwiches(country: str, year: int, workweek: str | None = None,
                   from_today: bool = False, max_pto: int = 3,
                   budget: int | None = None,
                   min_length: int | None = None,
                   max_length: int | None = None) -> dict:
    """Return the /v1/sandwiches response body as a plain dict.

    max_pto bounds how many PTO days a bridge may cost: 1 = classic single-day
    sandwiches only; higher also surfaces multi-day bridges (e.g. take Mon+Tue
    before a Wednesday holiday). Items are sorted by efficiency (days off per
    PTO day) so the cheapest tricks rank first.

    Optional preference filters (each ignored when None):
      - budget: drop bridges that cost more PTO than this (also caps max_pto).
      - min_length / max_length: keep only bridges whose resulting break length
        falls in this inclusive range.
    """
    cc = _validate_country(country)
    _validate_year(year)
    if not (1 <= max_pto <= 7):
        raise ApiInputError(f"max_pto must be in [1, 7], got {max_pto}")
    if budget is not None and budget < 0:
        raise ApiInputError(f"budget must be >= 0, got {budget}")
    weekend_set, weekend_names, source = _resolve_workweek(cc, workweek)

    lib_records = library_source.fetch(year, cc)
    holiday_name_map = {r["date"]: r["name"] for r in lib_records}
    holiday_dates = set(holiday_name_map.keys())

    # No point generating bridges that already exceed the PTO budget.
    effective_max_pto = max_pto if budget is None else min(max_pto, budget)
    if effective_max_pto < 1:
        return {
            "country": cc, "year": year, "workweek": weekend_names,
            "workweek_source": source, "count": 0, "sandwiches": [],
        }

    raw = sandwich.detect(holiday_dates, year, weekend_days=weekend_set,
                          max_pto=effective_max_pto)
    today = _date.today()
    items = []
    for s in raw:
        if from_today and s["sandwich_date"] < today:
            continue
        if budget is not None and s["pto_count"] > budget:
            continue
        length = s["break_length_days"]
        if min_length is not None and length < min_length:
            continue
        if max_length is not None and length > max_length:
            continue
        anchors = [
            holiday_name_map[d]
            for d in daterange(s["break_start"], s["break_end"])
            if d in holiday_name_map
        ]
        items.append({
            "pto_date": s["sandwich_date"],
            "pto_dates": list(s["pto_dates"]),
            "weekday": _WEEKDAY_LABELS[s["sandwich_date"].weekday()],
            "break_start": s["break_start"],
            "break_end": s["break_end"],
            "break_length": s["break_length_days"],
            "pto_cost": s["pto_count"],
            "context": " + ".join(anchors[:2]),
        })

    # Most efficient first (days off per PTO day), then soonest.
    items.sort(key=lambda i: (-(i["break_length"] / i["pto_cost"]), i["pto_date"]))
    return {
        "country": cc,
        "year": year,
        "workweek": weekend_names,
        "workweek_source": source,
        "count": len(items),
        "sandwiches": items,
    }


def _trip_to_payload(trip: dict, red_days: dict) -> dict:
    """Shape one candidate_breaks output into the API trip dict.

    `trip` keys (from planner.candidate_breaks): start, end, pto, cost, length.
    `red_days`: {date: name} from planner.compute_calendar.
    """
    anchor_names: list[str] = []
    seen_names: set[str] = set()
    for d in daterange(trip["start"], trip["end"]):
        name = red_days.get(d)
        if name and name not in seen_names:
            seen_names.add(name)
            anchor_names.append(name)
    return {
        "break_start": trip["start"],
        "break_end": trip["end"],
        "break_length": trip["length"],
        "pto_dates": list(trip["pto"]),
        "pto_cost": trip["cost"],
        "anchors": anchor_names,
    }


def get_plans(country: str, year: int, budget: int,
              length: int | None = None,
              min_length: int = 3, max_length: int = 10,
              top: int = 1,
              month: int | None = None,
              workweek: str | None = None,
              from_today: bool = False) -> dict:
    """Return the /v1/plan response body as a plain dict.

    Two modes:
      - length set: returns only that length, up to `top` entries.
      - length unset: returns each length in [min_length, max_length],
        up to `top` entries each.

    When `month` (1..12) is set, results are anchored to that month: only
    breaks that START in that month are considered, so the per-length top-N
    surfaces that month's own bridges (e.g. extending a holiday into the
    following work-week) instead of the globally cheapest break of each length.
    """
    cc = _validate_country(country)
    _validate_year(year)
    if budget < 0:
        raise ApiInputError(f"budget must be >= 0, got {budget}")
    if top < 1:
        raise ApiInputError(f"top must be >= 1, got {top}")
    if month is not None and not (1 <= month <= 12):
        raise ApiInputError(f"month must be in [1, 12], got {month}")

    if length is not None:
        if length < 1 or length > 31:
            raise ApiInputError(
                f"length must be in [1, 31], got {length}"
            )
        wanted_lengths = [length]
    else:
        if min_length < 1 or max_length > 31:
            raise ApiInputError(
                f"min_length/max_length must be in [1, 31], "
                f"got [{min_length}, {max_length}]"
            )
        if min_length > max_length:
            raise ApiInputError(
                f"min_length ({min_length}) > max_length ({max_length})"
            )
        wanted_lengths = list(range(min_length, max_length + 1))

    weekend_set, weekend_names, source = _resolve_workweek(cc, workweek)

    off_days, red_days, _festivals = compute_calendar(year, cc, weekend_set)
    cap = max(wanted_lengths)
    candidates = candidate_breaks(year, off_days, budget, max_break_len=cap)

    if from_today:
        today = _date.today()
        candidates = [c for c in candidates if c["start"] >= today]

    if month is not None:
        candidates = [c for c in candidates if c["start"].month == month]

    wanted_set = set(wanted_lengths)
    results_by_length: dict[str, list[dict]] = {str(L): [] for L in wanted_lengths}
    grouped: dict[int, list[dict]] = {L: [] for L in wanted_lengths}
    for c in candidates:
        if c["length"] in wanted_set:
            grouped[c["length"]].append(c)

    for L, trips in grouped.items():
        trips.sort(key=lambda t: (t["cost"], t["start"]))
        results_by_length[str(L)] = [
            _trip_to_payload(t, red_days) for t in trips[:top]
        ]

    return {
        "country": cc,
        "year": year,
        "budget": budget,
        "workweek": weekend_names,
        "workweek_source": source,
        "results_by_length": results_by_length,
    }
