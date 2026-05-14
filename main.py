"""Holiday Sandwicher — aggregates holiday data from library + gov API + news,
then detects sandwich days.

Usage:
    python main.py --year 2026 --country KR
"""
import argparse
from datetime import date

from sources import library_source, gov_api_source, news_source
from sandwich import detect
from storage import upsert


def merge(records: list[dict]) -> dict[date, dict]:
    """Combine records from all sources, keyed by date.
    Naming priority (best name wins): gov_api > library > news.
    News is treated as a confirmation signal, not an authoritative name source.
    """
    name_priority = {"gov_api": 3, "library": 2, "news": 1}
    merged: dict[date, dict] = {}
    for r in records:
        existing = merged.get(r["date"])
        if existing is None or name_priority[r["source"]] > name_priority[existing["source"]]:
            prior_confirmed = existing.get("confirmed_by", set()) if existing else set()
            merged[r["date"]] = dict(r)
            merged[r["date"]]["confirmed_by"] = prior_confirmed | {r["source"]}
        else:
            merged[r["date"]]["confirmed_by"].add(r["source"])
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=date.today().year)
    ap.add_argument("--country", default="KR")
    ap.add_argument("--upcoming", action="store_true",
                    help="Only show holidays from today onward")
    ap.add_argument("--only-red", action="store_true",
                    help="Exclude unconfirmed news-detected dates (red days only)")
    args = ap.parse_args()

    all_records = []
    for src in (library_source, gov_api_source, news_source):
        try:
            all_records.extend(src.fetch(args.year, args.country))
        except Exception as e:
            print(f"[warn] {src.__name__} failed: {e}")

    newly_seen = upsert(all_records)
    merged = merge(all_records)

    today = date.today()
    visible_dates = sorted(merged)
    if args.only_red:
        visible_dates = [
            d for d in visible_dates
            if "library" in merged[d].get("confirmed_by", set())
            or "gov_api" in merged[d].get("confirmed_by", set())
        ]
    if args.upcoming:
        visible_dates = [d for d in visible_dates if d >= today]

    sandwiches = detect(set(visible_dates), args.year)
    if args.upcoming:
        sandwiches = [s for s in sandwiches if s["sandwich_date"] >= today]

    header = "Upcoming red holidays" if args.upcoming and args.only_red \
        else "Upcoming holidays" if args.upcoming \
        else "Red holidays" if args.only_red \
        else "Holidays"
    print(f"\n=== {header} in {args.country} {args.year} ===")
    for d in visible_dates:
        r = merged[d]
        confirms = ",".join(sorted(r.get("confirmed_by", {r["source"]})))
        days_away = (d - today).days
        when = f"(in {days_away}d)" if 0 <= days_away <= 365 else ""
        print(f"  {d} {d.strftime('%a')}  {r['name']:<48} {when:<9} [{confirms}]")

    print(f"\n=== Sandwich days ({len(sandwiches)}) ===")
    for s in sandwiches:
        print(
            f"  Take {s['sandwich_date']} ({s['sandwich_date'].strftime('%a')}) off → "
            f"{s['break_length_days']}-day break "
            f"({s['break_start']} → {s['break_end']})"
        )

    if newly_seen:
        print(f"\n=== Newly detected since last run ({len(newly_seen)}) ===")
        for r in newly_seen:
            extra = f" — {r.get('headline', '')}" if r.get("headline") else ""
            print(f"  {r['date']}  {r['name']} [{r['source']}]{extra}")


if __name__ == "__main__":
    main()
