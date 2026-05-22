"""Service layer — adapts existing modules to API response shapes.

This file contains no holiday logic of its own. It must only call into
sources/, sandwich, storage, and planner. If a needed function is missing
in those modules, add it there — not here.
"""
import holidays

from sources import news_source


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
