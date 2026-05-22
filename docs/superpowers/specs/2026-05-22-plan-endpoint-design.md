# Vacation-Planner API Endpoint (`/v1/plan`) — Design Spec

**Date:** 2026-05-22
**Status:** Approved (brainstorm) — implementation pending
**Sub-project:** D of the daysoff product roadmap (plan endpoint)
**Depends on:** sub-project A (read API) — branch `feat/read-api` / PR #2

## Problem

The mobile app needs a vacation-planning endpoint that surfaces, for a given
country and PTO budget, the **best break of each length** the user might
care about. The existing CLI (`planner.py`) already computes this for one
country at a time and prints it to the terminal; the API needs to expose
the same data over JSON.

## Goal

Add a single `GET /v1/plan` endpoint that wraps `planner.candidate_breaks`
and returns a **length buffet**: for each integer length in a requested
range (e.g. 3..10 days), the top-K alternative breaks, sorted by lowest
PTO cost. The endpoint reuses the workweek cascade already proven in
`/v1/sandwiches`.

## Endpoint surface

`GET /v1/plan` — public, no auth, CORS allow-all (matches the rest of v1).

| Query param | Default | Notes |
|---|---|---|
| `country` | required | ISO-2; validated via existing `_validate_country` |
| `year` | current year | range 1900–2100, validated like other endpoints |
| `budget` | required | total PTO days available; integer ≥ 0 |
| `length` | — | If set, focus on this single length and ignore `min_length`/`max_length` |
| `min_length` | `3` | Lower bound of the range (inclusive); ignored if `length` is set |
| `max_length` | `10` | Upper bound (inclusive); ignored if `length` is set |
| `top` | `1` | Max alternatives per length |
| `workweek` | resolved via cascade | Comma list of OFF days, e.g. `sat,sun` |
| `from_today` | `false` | Drop trips whose `break_start` is before today |

**Two usage patterns:**

```
# Menu view — best of each length 3..10 (8 entries, one per length)
GET /v1/plan?country=KR&year=2026&budget=15&min_length=3&max_length=10&workweek=sat,sun

# Drill-down — top 5 five-day breaks
GET /v1/plan?country=KR&year=2026&budget=15&length=5&top=5&workweek=sat,sun
```

**Validation specifics:**

- `length` and (`min_length`, `max_length`) are mutually exclusive in
  semantics: when `length` is provided, the range params are silently
  ignored. No error.
- `min_length > max_length` → 400 with clear detail.
- `length < 1` or `length > 31` → 400.
- `top < 1` → 400.
- `budget < 0` → 400.

**Workweek cascade** (same order as `/v1/sandwiches`):

1. Explicit `workweek` query param.
2. Most recent policy in `storage.resolve_workweek(country, today)`.
3. `planner.WORKWEEK_FALLBACKS[country]`.
4. 400 `{"detail": "no workweek on record for <CC>; pass ?workweek=sat,sun"}`.

## Response shape

```jsonc
{
  "country": "KR",
  "year": 2026,
  "budget": 15,
  "workweek": ["sat", "sun"],
  "workweek_source": "user",            // same enum as /v1/sandwiches
  "results_by_length": {
    "3": [
      {
        "break_start": "2026-09-26",
        "break_end": "2026-09-28",
        "break_length": 3,
        "pto_dates": ["2026-09-28"],
        "pto_cost": 1,
        "anchors": ["Chuseok"]
      }
    ],
    "4": [ ... ],
    "5": [ ... ],
    "10": [ ... ]
  }
}
```

- `results_by_length` keys are **stringified integers** (JSON object keys
  cannot be ints). Mobile clients should treat them as numeric.
- An empty list for a length is valid (e.g. budget too small to make a
  length-10 break with `from_today=true` late in the year) — the key is
  still present in the response with `[]`.
- Trip-level fields:
  - `break_start`, `break_end` — inclusive, ISO date strings.
  - `break_length` — total days in the contiguous off-stretch (always
    equals the length the result is filed under).
  - `pto_dates` — list of dates the user must burn PTO on, sorted.
  - `pto_cost` — `len(pto_dates)`.
  - `anchors` — names of red days inside the break (deduped, sorted by
    date); empty list if none.

## Sort order

Per length, alternatives sort by:

1. `pto_cost` ascending — fewest PTO days needed first ("cheapest").
2. `break_start` ascending — earlier breaks before later ones as tie-break.

This matches the CLI's `best_single_break(key=(length, -cost))` intuition,
inverted because here length is fixed and cost is the variable.

## What it reuses

- `planner.candidate_breaks(year, off_days, budget, max_break_len)` —
  already exists and produces every viable break window with
  `start`/`end`/`pto`/`cost`/`length`. The endpoint's `get_plans` filters
  this output by length and takes top-K per length.
- `planner.compute_calendar(year, country, weekend_days)` — already
  exists, returns `off_days` plus the red-day name map for anchors.
- `_resolve_workweek_for_sandwiches` in `api/services.py` — renamed to
  `_resolve_workweek` so both `/v1/sandwiches` and `/v1/plan` share it
  without name confusion. The current name is only used internally by
  one call site, so no alias is needed — straight rename, update the
  sandwich call site in the same commit.
- `_validate_country`, `_validate_year`, `ApiInputError` — all already
  exist.
- `library_source.fetch` is NOT directly needed here — `compute_calendar`
  already calls it internally.

## Non-goals (explicitly out of scope)

- **`strategy=portfolio`** — the CLI's "best portfolio of non-overlapping
  trips that maximizes total off-days within budget" is a different DP
  problem. Future spec; can be added as `?strategy=portfolio` or its own
  endpoint without breaking this one.
- **Save-this-plan to user prefs** — needs auth (sub-project C).
- **Year-spanning trips** (Dec → Jan crossing) — single-year only, matches
  CLI.
- **Visit-country overlay** (the `--visit` CLI feature from PR #1) — could
  be a follow-up `?visit=NP` query param once PR #1 merges; not in this
  spec to avoid coupling to PR #1's merge timing.
- **Festivals** — `planner.py` shows nearby cultural festivals in CLI
  output. The API skips this for v1 because the festivals source is
  KR-only and would mislead about coverage.
- **Pagination beyond `top`** — `top` is the only cap. If a user truly
  needs 100+ alternatives for a single length, they can call again with
  filters; otherwise the endpoint stays simple.

## Files touched

| File | Change |
|---|---|
| `api/schemas.py` | Add `PlanTrip`, `PlanResponse` |
| `api/services.py` | Add `get_plans()`; rename `_resolve_workweek_for_sandwiches` → `_resolve_workweek` (sandwich call site updated) |
| `api/main.py` | Add `/v1/plan` route |
| `tests/test_api_endpoints.py` | Add `TestPlan` (~8 tests) |
| `README.md` | Add `/v1/plan` row to the endpoint table |

## Testing strategy

`TestPlan` covers:

| Test | Asserts |
|---|---|
| `test_menu_view_returns_one_per_length_in_range` | range 3..7 with top=1 → exactly 5 keys, each with at most 1 entry |
| `test_single_length_with_top_returns_alternatives` | length=5, top=5 → only key "5" present, up to 5 entries, all length 5 |
| `test_alternatives_sorted_by_pto_cost_ascending` | first entry's cost ≤ second entry's cost for any length with ≥2 entries |
| `test_pto_dates_consistent_with_cost` | `len(pto_dates) == pto_cost` for every entry |
| `test_anchors_present_when_break_spans_holiday` | KR length=5 around Chuseok includes "Chuseok" in anchors |
| `test_unsupported_country_returns_400` | `?country=ZZ` → 400 |
| `test_min_greater_than_max_returns_400` | `min_length=10&max_length=5` → 400 |
| `test_no_workweek_with_no_policy_returns_400` | AQ with no workweek param → 400 |

Existing 128 tests continue to pass. Final suite: ~136.

## Done criteria

- `/v1/plan` returns a `PlanResponse` for the canonical query
  (`country=KR&year=2026&budget=15&workweek=sat,sun`) with at least one
  trip per length in [3, 10].
- `length=5&top=5` returns up to 5 sorted alternatives, all length 5.
- All error paths return 400 with descriptive `detail`.
- `python3 -m unittest discover tests` ends OK with ~136 tests (128 + 8).
- README's API section lists the new endpoint.

## Open questions resolved during brainstorming

- **Q: Response shape — length buffet, strategy buffet, or both?** →
  Length buffet.
- **Q: Length param mode — fixed defaults, range, or top-K?** → Range
  (`min_length`/`max_length`) with single-`length` override.
- **Q: Top-K per length** → Caller chooses via `top` (default 1).
- **Q: Mutually exclusive `length` vs range?** → `length` silently
  overrides; no error.
- **Q: Sort order?** → Cheapest PTO cost first, earlier date as tiebreak.
- **Q: Festivals in response?** → No, KR-only data would mislead.
- **Q: `--visit` overlay?** → Future, after PR #1 merges.
