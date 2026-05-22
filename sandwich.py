"""Sandwich-day detection.

A 'sandwich day' is a workday that sits between two non-working days
(holidays or weekends). Taking that single day off yields a long break.
"""
from __future__ import annotations

from datetime import date, timedelta


def detect(holiday_dates: set[date], year: int,
           weekend_days: set[int] | None = None) -> list[dict]:
    """Find sandwich days in `year` given `holiday_dates` and `weekend_days`.

    weekend_days: set of weekday() integers that are OFF. Defaults to
    {5, 6} (Sat, Sun) — preserves legacy callers (CLI).
    """
    if weekend_days is None:
        weekend_days = {5, 6}

    sandwiches = []
    d = date(year, 1, 1)
    end = date(year, 12, 31)
    one = timedelta(days=1)

    def is_off(day: date) -> bool:
        return day.weekday() in weekend_days or day in holiday_dates

    while d <= end:
        if d.weekday() not in weekend_days and d not in holiday_dates:
            prev_off = is_off(d - one)
            next_off = is_off(d + one)
            if prev_off and next_off:
                # Measure the surrounding break
                start = d - one
                while is_off(start - one):
                    start -= one
                stop = d + one
                while is_off(stop + one):
                    stop += one
                sandwiches.append({
                    "sandwich_date": d,
                    "break_start": start,
                    "break_end": stop,
                    "break_length_days": (stop - start).days + 1,
                })
        d += one
    return sandwiches
