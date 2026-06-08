"""Sandwich-day detection.

A 'sandwich day' is a workday that sits between two non-working days
(holidays or weekends). Taking that single day off yields a long break.

More generally, a *bridge* is a short run of consecutive workdays (1..max_pto)
flanked by days off on both sides: taking the whole run merges the two
surrounding off-blocks into one long break. A single-day sandwich is the
max_pto == 1 case.
"""
from __future__ import annotations

from datetime import date, timedelta


def detect(holiday_dates: set[date], year: int,
           weekend_days: set[int] | None = None,
           max_pto: int = 1) -> list[dict]:
    """Find sandwich days / bridges in `year`.

    weekend_days: set of weekday() integers that are OFF. Defaults to
    {5, 6} (Sat, Sun) — preserves legacy callers (CLI).
    max_pto: the widest workday gap to bridge. 1 (default) finds only
    single-day sandwiches; higher values also find multi-day bridges (e.g.
    take Mon+Tue before a Wednesday holiday). Only bridges whose merged break
    contains a real holiday are returned, so pure weekend-to-weekend
    extensions are skipped.

    Each result: {sandwich_date (first PTO day, for back-compat), pto_dates,
    pto_count, break_start, break_end, break_length_days}.
    """
    if weekend_days is None:
        weekend_days = {5, 6}

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    one = timedelta(days=1)

    def is_off(day: date) -> bool:
        # Days outside the year act as workdays: a break cannot extend past
        # the year boundary, so a run touching the edge isn't a sandwich.
        if day < year_start or day > year_end:
            return False
        return day.weekday() in weekend_days or day in holiday_dates

    sandwiches: list[dict] = []
    d = year_start
    while d <= year_end:
        if is_off(d):
            d += one
            continue

        # Collect the maximal run of consecutive workdays starting at d.
        run: list[date] = []
        while d <= year_end and not is_off(d):
            run.append(d)
            d += one

        run_len = len(run)
        if not (1 <= run_len <= max_pto):
            continue

        prev_day = run[0] - one
        next_day = run[-1] + one
        # Both flanks must be off, otherwise taking the run doesn't merge two
        # off-blocks (it would leave a workday adjacent).
        if not (is_off(prev_day) and is_off(next_day)):
            continue

        # Walk out over the flanking off-blocks to size the merged break.
        bstart = prev_day
        while is_off(bstart - one):
            bstart -= one
        bend = next_day
        while is_off(bend + one):
            bend += one

        # Holiday-anchored: the merged break must contain a real holiday.
        if not any(bstart <= h <= bend for h in holiday_dates):
            continue

        sandwiches.append({
            "sandwich_date": run[0],
            "pto_dates": list(run),
            "pto_count": run_len,
            "break_start": bstart,
            "break_end": bend,
            "break_length_days": (bend - bstart).days + 1,
        })

    return sandwiches
