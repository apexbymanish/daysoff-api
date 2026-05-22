"""Vacation planner — given a PTO budget, find the optimal days to take off.

Classifies every day into:
  🏢 OFFICE HOLIDAY (공휴일/red day) — office closed, no PTO needed
  🏖️ PTO (연차)                       — your annual leave
  🟦 WEEKEND                          — naturally off
  🎎 FESTIVAL (축제/기념일)            — cultural event, office still open
  💼 WORKDAY                          — regular workday

Usage:
    python planner.py --budget 15 --year 2026 --country KR
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
from functools import lru_cache

from sources import library_source, festivals_source, policy_scraper
from storage import (upsert_workweek_policies, resolve_workweek,
                     latest_policy_age_days)
import config as user_config


POLICY_STALE_DAYS = 30


# LAST-RESORT fallback ONLY — used when no automated source has a policy on file.
# These are intentionally minimal: prefer the news-scraped policy table.
# When you see this dict grow, that's a sign the automation has a gap.
WORKWEEK_FALLBACKS = {
    "KR": "sat,sun", "JP": "sat,sun", "US": "sat,sun", "GB": "sat,sun",
    "IN": "sat,sun", "CN": "sat,sun", "DE": "sat,sun",
}

LOCALE_LABELS = {
    "KR": {"pto": "PTO (연차)", "holiday": "OFFICE HOLIDAY (공휴일)",
           "festival": "FESTIVAL (기념일/축제)"},
    "NP": {"pto": "PTO (बिदा)", "holiday": "OFFICE HOLIDAY (सार्वजनिक बिदा)",
           "festival": "FESTIVAL (पर्व/चाड)"},
    "JP": {"pto": "PTO (有給休暇)", "holiday": "OFFICE HOLIDAY (祝日)",
           "festival": "FESTIVAL (記念日)"},
}
DEFAULT_LABELS = {"pto": "PTO", "holiday": "OFFICE HOLIDAY", "festival": "FESTIVAL"}


WEEKDAY_MAP = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def parse_workweek(spec: str) -> set[int]:
    """'sat,sun' -> {5, 6}. Returns set of weekday() integers that are OFF."""
    return {WEEKDAY_MAP[s.strip().lower()] for s in spec.split(",") if s.strip()}


def daterange(start: date, end: date):
    one = timedelta(days=1)
    d = start
    while d <= end:
        yield d
        d += one


def compute_calendar(year: int, country: str, weekend_days: set[int]):
    """Build the day-classification calendar for the year.

    Returns:
        off_days: set of dates that are naturally off (weekend OR red day)
        red_days: dict {date: holiday_name} — office-closed holidays
        festivals: dict {date: festival_record} — cultural events
    """
    holiday_records = library_source.fetch(year, country)
    red_days = {r["date"]: r["name"] for r in holiday_records}

    festival_records = festivals_source.fetch(year, country)
    festivals = {r["date"]: r for r in festival_records}

    off_days = set(red_days.keys())
    for d in daterange(date(year, 1, 1), date(year, 12, 31)):
        if d.weekday() in weekend_days:
            off_days.add(d)
    return off_days, red_days, festivals


def classify_day(d: date, pto_set: set[date], red_days: dict, festivals: dict,
                 weekend_days: set[int], labels: dict,
                 visit_red_days: dict | None = None,
                 visit_country: str | None = None) -> str:
    """Return the day-type label for a given date in a trip.

    visit_red_days/visit_country are an optional ADDITIVE overlay — they do
    not replace the primary tag. A day can be 🏖️ PTO AND 🌏 LOCAL HOLIDAY.
    """
    is_weekend = d.weekday() in weekend_days
    is_red = d in red_days
    is_pto = d in pto_set
    is_festival = d in festivals

    parts = []
    if is_red:
        parts.append(f"🏢 {labels['holiday']} — {red_days[d]}")
    if is_weekend and not is_red:
        parts.append("🟦 weekend")
    if is_pto:
        parts.append(f"🏖️ {labels['pto']}")
    if is_festival:
        f = festivals[d]
        loc = f" ({f.get('name_ko', '')})" if f.get("name_ko") else ""
        parts.append(f"🎎 {f['name_en']}{loc}")
    if not parts:
        parts.append("💼 workday")
    if visit_red_days and d in visit_red_days:
        cc = visit_country or "??"
        parts.append(f"🌏 LOCAL HOLIDAY ({cc}) — {visit_red_days[d]}")
    return " · ".join(parts)


def candidate_breaks(year: int, off_days: set[date], budget: int,
                     max_break_len: int = 31) -> list[dict]:
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    one = timedelta(days=1)
    out = []

    for start in daterange(year_start, year_end):
        prev = start - one
        if prev >= year_start and prev in off_days:
            continue
        for length in range(1, max_break_len + 1):
            end = start + timedelta(days=length - 1)
            if end > year_end:
                break
            pto = [d for d in daterange(start, end) if d not in off_days]
            if len(pto) > budget:
                break
            nxt = end + one
            if nxt <= year_end and nxt in off_days:
                continue
            out.append({
                "start": start, "end": end, "pto": pto,
                "cost": len(pto), "length": length,
            })
    return out


def best_single_break(candidates, budget):
    affordable = [c for c in candidates if c["cost"] <= budget]
    if not affordable:
        return None
    return max(affordable, key=lambda c: (c["length"], -c["cost"]))


def best_portfolio(candidates, budget):
    from bisect import bisect_right
    items = sorted(
        [c for c in candidates if 0 < c["cost"] <= budget],
        key=lambda c: c["end"],
    )
    n = len(items)
    if n == 0:
        return [], 0
    end_ords = [c["end"].toordinal() for c in items]

    def predecessor(i):
        target = items[i]["start"].toordinal()
        j = bisect_right(end_ords, target - 1) - 1
        return j if j < i else -1

    dp = [[0] * (budget + 1) for _ in range(n + 1)]
    take = [[False] * (budget + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        c = items[i - 1]
        cost, value = c["cost"], c["length"]
        pred = predecessor(i - 1)
        pred_state = pred + 1
        for b in range(budget + 1):
            skip_v = dp[i - 1][b]
            take_v = -1
            if cost <= b:
                take_v = value + dp[pred_state][b - cost]
            if take_v > skip_v:
                dp[i][b] = take_v
                take[i][b] = True
            else:
                dp[i][b] = skip_v
                take[i][b] = False

    selected = []
    i, b = n, budget
    while i > 0:
        if take[i][b]:
            c = items[i - 1]
            selected.append(c)
            pred = predecessor(i - 1)
            i = pred + 1
            b -= c["cost"]
        else:
            i -= 1
    selected.reverse()
    return selected, dp[n][budget]


def print_trip(trip, red_days, festivals, weekend_days, labels,
               visit_red_days=None, visit_country=None):
    """Print a single trip with day-by-day classification.

    visit_red_days/visit_country are optional. When supplied, days inside
    the trip that match visit red days get an additive 🌏 tag, and a
    summary line lists the in-country holidays.
    """
    pto_set = set(trip["pto"])
    print(f"\n  ┌─ {trip['start'].strftime('%a')} {trip['start']} "
          f"→ {trip['end'].strftime('%a')} {trip['end']}  "
          f"({trip['length']} days, {trip['cost']} PTO)")
    for d in daterange(trip["start"], trip["end"]):
        label = classify_day(d, pto_set, red_days, festivals, weekend_days,
                             labels, visit_red_days, visit_country)
        print(f"  │  {d.strftime('%a')} {d}  {label}")
    print(f"  └─ Take {trip['cost']} PTO day(s)")
    if visit_red_days:
        overlap = visit_overlap(trip, visit_red_days)
        if overlap:
            joined = ", ".join(f"{d} {name}" for d, name in overlap)
            cc = visit_country or "??"
            print(f"  In-country {cc} holidays during this trip: {joined}")


def visit_overlap(trip: dict, visit_red_days: dict) -> list[tuple[date, str]]:
    """Return [(date, name), ...] for visit-country red days inside the trip.

    Pure helper — testable without I/O. Inclusive at both trip endpoints.
    Result is sorted by date.
    """
    if not visit_red_days:
        return []
    start, end = trip["start"], trip["end"]
    return sorted(
        (d, name) for d, name in visit_red_days.items()
        if start <= d <= end
    )


def print_nearby_festivals(start: date, end: date, festivals: dict, window: int = 7):
    """Print festivals within `window` days before/after a trip."""
    win = timedelta(days=window)
    nearby = []
    for fd, frec in festivals.items():
        if start - win <= fd <= end + win:
            inside = start <= fd <= end
            nearby.append((fd, frec, inside))
    if not nearby:
        return
    print("  Nearby festivals:")
    for fd, frec, inside in sorted(nearby, key=lambda x: x[0]):
        loc = "(during trip)" if inside else "(±7 days)"
        print(f"      {fd} {fd.strftime('%a')}  🎎 {frec['name_en']} "
              f"({frec['name_ko']}) {loc}")


def main():
    cfg = user_config.load()
    saved_country = cfg.get("country", "KR")
    saved_workweek = cfg.get("workweeks", {}).get(saved_country)

    ap = argparse.ArgumentParser(
        epilog=(
            "Examples:\n"
            "  python3 planner.py --budget 15 --country KR\n"
            "  python3 planner.py --budget 10 --country NP --workweek sat,sun\n"
            "  python3 planner.py --budget 12 --workweek wed,thu --save\n"
            "\n"
            "Custom workweek: any subset of mon,tue,wed,thu,fri,sat,sun\n"
            f"Config: ~/.daysoff/config.json\n"
            f"  saved → country={saved_country}, "
            f"budget={cfg.get('budget')}, workweek={saved_workweek}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--budget", type=int, default=cfg.get("budget"),
                    help="Number of PTO/연차 leave days available")
    ap.add_argument("--year", type=int, default=date.today().year)
    ap.add_argument("--country", default=saved_country,
                    help="ISO 2-letter code (KR, JP, NP, ...)")
    ap.add_argument("--visit", default=cfg.get("visit"),
                    help="Destination country (ISO 2-letter). Overlays "
                         "its red days as annotations onto each trip.")
    ap.add_argument("--save", action="store_true",
                    help="Save current --budget, --country, --workweek "
                         "to ~/.daysoff/config.json")
    ap.add_argument("--strategy", choices=["longest", "portfolio", "both"],
                    default="both")
    ap.add_argument("--from-today", action="store_true")
    ap.add_argument("--min-length", type=int, default=1)
    ap.add_argument("--max-length", type=int, default=31)
    ap.add_argument("--show-festivals-near", type=int, default=7,
                    help="Show festivals within N days of each trip (0 to disable)")
    ap.add_argument("--workweek", type=str,
                    default=cfg.get("workweeks", {}).get(saved_country),
                    help="Comma list of OFF days (e.g. 'sat,sun' or 'wed,thu'). "
                         "Auto-resolved if omitted.")
    ap.add_argument("--refresh-policies", action="store_true",
                    help="Force re-fetch policy news (auto-refreshes if stale)")
    ap.add_argument("--no-auto-refresh", action="store_true",
                    help="Disable automatic refresh of stale policies")
    args = ap.parse_args()

    if args.budget is None:
        ap.error("--budget is required (or save a default with --save)")

    # If user supplied --country but no --workweek, check if there's a saved
    # workweek specifically for THAT country.
    workweek_arg = args.workweek
    if workweek_arg is None:
        workweek_arg = cfg.get("workweeks", {}).get(args.country)

    target_date = date(args.year, 6, 30)

    # Auto-refresh policies if stale or never fetched (and we actually need to
    # look one up — skip if user provided --workweek explicitly)
    age = latest_policy_age_days(args.country)
    auto_refresh = (
        not args.no_auto_refresh
        and workweek_arg is None
        and (age is None or age > POLICY_STALE_DAYS)
        and args.country in policy_scraper.COUNTRY_QUERIES
    )
    if args.refresh_policies or auto_refresh:
        reason = ("forced" if args.refresh_policies
                  else "never fetched" if age is None
                  else f"{age}d old")
        print(f"Refreshing {args.country} workweek policies ({reason})...")
        scraped = policy_scraper.fetch(args.country)
        new_policies = upsert_workweek_policies(scraped)
        print(f"  Found {len(scraped)} policies ({len(new_policies)} new)")

    workweek_source = "user-flag"
    if workweek_arg:
        workweek_spec = workweek_arg
        if cfg.get("workweeks", {}).get(args.country) == workweek_arg:
            workweek_source = "saved preference"
    else:
        policy = resolve_workweek(args.country, target_date)
        if policy:
            workweek_spec = policy["weekend_spec"]
            workweek_source = (f"news ({policy['effective_date']}, "
                               f"conf={policy['confidence']})")
        elif args.country in WORKWEEK_FALLBACKS:
            workweek_spec = WORKWEEK_FALLBACKS[args.country]
            workweek_source = "hardcoded fallback"
        else:
            print(f"\n⚠️  No workweek policy on record for {args.country}.")
            print(f"   Pass --workweek sat,sun (or any days) and re-run, "
                  f"optionally with --save.")
            return

    if args.save:
        user_config.save({
            "country": args.country,
            "budget": args.budget,
            "workweeks": {args.country: workweek_spec},
        })
        print(f"✅ Saved to ~/.daysoff/config.json: "
              f"country={args.country}, budget={args.budget}, "
              f"workweek({args.country})={workweek_spec}\n")

    weekend_days = parse_workweek(workweek_spec)
    labels = LOCALE_LABELS.get(args.country, DEFAULT_LABELS)

    off_days, red_days, festivals = compute_calendar(args.year, args.country, weekend_days)

    visit_red_days: dict = {}
    visit_country = None
    if args.visit and args.visit.upper() != args.country.upper():
        visit_country = args.visit.upper()
        try:
            visit_records = library_source.fetch(args.year, visit_country)
            visit_red_days = {r["date"]: r["name"] for r in visit_records}
        except NotImplementedError:
            print(f"\n⚠️  --visit {visit_country}: not supported by the "
                  f"holidays library. Continuing without overlay.\n")
            visit_country = None

    candidates = candidate_breaks(args.year, off_days, args.budget,
                                  max_break_len=args.max_length)
    if args.from_today:
        today = date.today()
        candidates = [c for c in candidates if c["start"] >= today]
    candidates = [c for c in candidates if c["length"] <= args.max_length]
    portfolio_candidates = [c for c in candidates if c["length"] >= args.min_length]

    weekend_names = ", ".join(
        k.capitalize() for k, v in WEEKDAY_MAP.items() if v in weekend_days
    )
    print(f"\n{'=' * 64}")
    print(f"  VACATION PLAN — {args.country} {args.year}")
    print(f"  PTO budget: {args.budget} days  |  Weekend: {weekend_names} "
          f"[source: {workweek_source}]")
    print(f"{'=' * 64}")
    print(f"\n  Legend:")
    print(f"    🏢 {labels['holiday']:<30} — office closed, no PTO needed")
    print(f"    🏖️  {labels['pto']:<30} — your annual leave")
    print(f"    🟦 WEEKEND                       — naturally off")
    print(f"    🎎 {labels['festival']:<30} — cultural event, office open")
    print(f"    💼 WORKDAY                       — regular workday")

    if args.strategy in ("longest", "both"):
        longest = best_single_break(candidates, args.budget)
        print(f"\n{'━' * 64}")
        print(f"  🏆 LONGEST SINGLE BREAK")
        print(f"{'━' * 64}")
        if longest:
            print_trip(longest, red_days, festivals, weekend_days, labels,
                       visit_red_days, visit_country)
            if args.show_festivals_near > 0:
                print_nearby_festivals(
                    longest["start"], longest["end"], festivals,
                    args.show_festivals_near,
                )
        else:
            print("  (no break possible)")

    if args.strategy in ("portfolio", "both"):
        portfolio, total_off = best_portfolio(portfolio_candidates, args.budget)
        used = sum(p["cost"] for p in portfolio)
        print(f"\n{'━' * 64}")
        print(f"  📊 BEST PORTFOLIO — {len(portfolio)} trips, "
              f"{total_off} off-days, {used}/{args.budget} PTO used")
        print(f"{'━' * 64}")
        for p in portfolio:
            print_trip(p, red_days, festivals, weekend_days, labels,
                       visit_red_days, visit_country)
            if args.show_festivals_near > 0:
                print_nearby_festivals(
                    p["start"], p["end"], festivals,
                    args.show_festivals_near,
                )


if __name__ == "__main__":
    main()
