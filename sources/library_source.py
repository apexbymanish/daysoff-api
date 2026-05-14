"""Baseline holidays from the `holidays` PyPI package (offline, rule-based)."""
from datetime import date
import holidays


def fetch(year: int, country: str = "KR") -> list[dict]:
    py_holidays = holidays.country_holidays(country, years=year)
    return [
        {"date": d, "name": name, "country": country, "source": "library"}
        for d, name in sorted(py_holidays.items())
    ]
