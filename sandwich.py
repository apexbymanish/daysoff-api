"""Sandwich-day detection.

A 'sandwich day' is a workday (Mon-Fri) that sits between two non-working days
(holidays or weekends). Taking that single day off yields a long break.
"""
from datetime import date, timedelta


def detect(holiday_dates: set[date], year: int) -> list[dict]:
    sandwiches = []
    d = date(year, 1, 1)
    end = date(year, 12, 31)
    one = timedelta(days=1)

    def is_off(day: date) -> bool:
        return day.weekday() >= 5 or day in holiday_dates

    while d <= end:
        if d.weekday() < 5 and d not in holiday_dates:
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
