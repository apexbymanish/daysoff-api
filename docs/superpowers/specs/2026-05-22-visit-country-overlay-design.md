# Visit-Country Overlay for the Vacation Planner

**Date:** 2026-05-22
**Status:** Approved (brainstorm) — implementation pending

## Problem

`planner.py` optimizes vacation plans for a single country. A user who works
in country A but plans to travel to country B has no way to see, in one run,
which days off from their **home** country line up with **destination**-country
holidays. Today they must run the planner against home, separately run
`main.py` against the destination, and eyeball overlaps.

## Goal

Add a single flag (`--visit CC`) that overlays destination-country holidays
onto the existing single-country plan output, **without changing how trips are
selected or ranked**.

## Non-goals

- Re-ranking trips based on destination-country overlap (rejected during
  brainstorming — picked "annotate only" over "boost overlap" and "optimize
  for overlap").
- Cross-country workweek logic. The user's PTO is governed by their home
  country's workweek; the destination's workweek is irrelevant because they
  are not working there.
- Festivals for the destination country. `festivals_source` is KR-only today;
  expanding it is out of scope.
- News-source data (`news_kr`, `news_np`, `gov_api`) for the destination. The
  overlay uses only `library_source`, which covers 150+ countries offline,
  keeping the feature deterministic and dependency-free.
- Changes to `main.py` (the aggregator CLI). Single-country, untouched.

## CLI shape

```
python3 planner.py --budget 15 --country KR --visit NP
python3 planner.py --budget 15 --country KR --visit NP --save
python3 planner.py                                            # uses saved visit
```

| Flag | Meaning |
|---|---|
| `--country CC` | **Home** country. Drives workweek, PTO math, red-day calendar. Unchanged. |
| `--visit CC` | Destination country. Optional. Drives the overlay only. |

Edge cases:

- If `--visit == --country`: silently ignored (no error, no overlay).
- If `--visit` names a country the `holidays` library does not support: print
  a one-line warning and continue with no overlay. The plan itself still
  prints normally.
- `--save` persists `--visit` alongside the existing saved keys.

## Behavior

1. Home-country calendar is computed exactly as today (`compute_calendar`
   unchanged in shape).
2. When `--visit` is set, the planner additionally calls
   `library_source.fetch(year, visit_country)` and builds a `set[date]` of
   destination red days.
3. For each trip emitted (longest, portfolio, alternatives):
   - Each day in the trip is checked against the destination red-day set.
     A match adds a new tag `🌏 LOCAL HOLIDAY (<visit_country>)` rendered
     alongside the existing tags.
   - A summary line is printed after the trip's day list:
     `In-country NP holidays during this trip: 2026-10-12 Dashain, 2026-10-13 Vijaya Dashami`
   - If no destination holidays fall inside the trip, no summary line prints
     (no noise).
4. PTO math, trip length, trip selection: **unaffected**. A destination red
   day that falls on a home-country workday still costs a PTO day. The home
   country's office is the only thing that determines whether you have to
   burn leave.

## Day-tag priority

A single day can carry multiple tags. Existing priority (highest first):
OFFICE HOLIDAY → PTO → WEEKEND → FESTIVAL → WORKDAY. The new
`LOCAL HOLIDAY` tag is **additive**, not a replacement — it is printed
alongside the primary tag (e.g. `🏖️ PTO + 🌏 LOCAL HOLIDAY (NP)`).

## Files touched

| File | Change |
|---|---|
| `planner.py` | Add `--visit` argparse entry. Load visit red-day set. Thread it into the day-rendering and trip-summary functions. Persist via `--save`. |
| `config.py` | Add `visit` to the default-user schema; ensure missing key reads as `None`. |
| `tests/test_planner_algos.py` | One new test: given home=KR red days {X} and visit=NP red days {Y}, assert (a) PTO math equals the no-`--visit` baseline; (b) trips containing Y emit the overlay tag and summary; (c) trips not containing Y emit no summary line. |

## Test plan

- Existing 103-test suite continues to pass unchanged.
- New planner test covers the three assertions above.
- Manual smoke:
  `python3 planner.py --budget 15 --country KR --visit NP --year 2026 --from-today`
  should show Dashain/Tihar inside any trip window that contains them.

## Open questions resolved during brainstorming

- **Q: Optimize for overlap, boost overlap, or annotate only?** → Annotate only.
- **Q: Source for destination holidays?** → `library_source` only.
- **Q: Same-country `--visit`?** → Silent no-op.
- **Q: Destination workweek?** → Not loaded, not used.
