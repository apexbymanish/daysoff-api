# Visit-Country Overlay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an annotate-only `--visit CC` flag to `planner.py` so a user planning travel from a home country to any destination country can see, in one run, which home-country off-days coincide with destination-country holidays.

**Architecture:** Home-country planning logic is unchanged. When `--visit` is set, the planner also loads destination red days from `library_source.fetch(year, visit_country)` and threads them as an additive overlay through `classify_day` and `print_trip`. A new pure helper `visit_overlap` produces the per-trip summary line. PTO math, trip selection, ranking: untouched.

**Tech Stack:** Python 3.10+, `holidays` PyPI package (already in `requirements.txt`), `unittest` (project convention).

**Spec:** `docs/superpowers/specs/2026-05-22-visit-country-overlay-design.md`

---

## File Structure

| File | Role |
|---|---|
| `planner.py` (modify) | Extend `classify_day`, add `visit_overlap` helper, extend `print_trip`, wire `--visit` flag in `main()`, persist via `--save`. |
| `config.py` (modify, comment only) | Add `visit` to the documented schema in the module docstring. |
| `tests/test_planner_algos.py` (modify) | Add `TestClassifyDayVisit` and `TestVisitOverlap` test classes. |
| `README.md` (modify) | Add `--visit` flag row to the planner flag table and a usage example. |
| `docs/superpowers/specs/2026-05-22-visit-country-overlay-design.md` | Already committed — reference only. |

No new files. Two new test classes; one new public function (`visit_overlap`); one extended signature (`classify_day`); one extended call site (`print_trip`); one new argparse entry plus persistence.

---

## Task 1: Extend `classify_day` to render the LOCAL HOLIDAY tag

**Files:**
- Modify: `planner.py` (function `classify_day` at lines 84–105)
- Test: `tests/test_planner_algos.py` (append new `TestClassifyDayVisit` class)

- [ ] **Step 1: Write the failing tests**

Append at the bottom of `tests/test_planner_algos.py`, before the `if __name__ == "__main__":` line:

```python
# ─── classify_day with visit-country overlay ─────────────────────────────

class TestClassifyDayVisit(unittest.TestCase):
    def test_visit_red_day_adds_overlay_tag(self):
        # Workday in home country that is a red day in visit country
        label = classify_day(
            date(2026, 10, 12),  # Mon — home workday
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
            visit_red_days={date(2026, 10, 12): "Dashain"},
            visit_country="NP",
        )
        self.assertIn("LOCAL HOLIDAY", label)
        self.assertIn("Dashain", label)
        self.assertIn("NP", label)

    def test_visit_overlay_does_not_replace_primary_tag(self):
        # PTO day that is also red in visit country → both tags
        label = classify_day(
            date(2026, 10, 12),
            pto_set={date(2026, 10, 12)},
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
            visit_red_days={date(2026, 10, 12): "Dashain"},
            visit_country="NP",
        )
        self.assertIn("PTO", label)
        self.assertIn("LOCAL HOLIDAY", label)
        self.assertIn("Dashain", label)

    def test_no_overlay_when_visit_red_days_empty(self):
        label = classify_day(
            date(2026, 10, 12),
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
            visit_red_days={},
            visit_country="NP",
        )
        self.assertNotIn("LOCAL HOLIDAY", label)

    def test_omitted_visit_args_preserve_legacy_behavior(self):
        # Calling classify_day without the new kwargs must still work
        label = classify_day(
            date(2026, 5, 14),
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
        )
        self.assertIn("workday", label)
        self.assertNotIn("LOCAL HOLIDAY", label)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_planner_algos.TestClassifyDayVisit -v`

Expected: FAIL with `TypeError: classify_day() got an unexpected keyword argument 'visit_red_days'`

- [ ] **Step 3: Extend `classify_day` to accept and render the visit overlay**

Replace the entire `classify_day` function in `planner.py` (lines 84–105) with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_planner_algos.TestClassifyDayVisit tests.test_planner_algos.TestClassifyDay -v`

Expected: PASS — all 4 new tests pass AND the 5 existing `TestClassifyDay` tests still pass (the optional kwargs preserve the old call sites).

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add planner.py tests/test_planner_algos.py
git commit -m "feat(planner): classify_day renders LOCAL HOLIDAY overlay for visit country"
```

---

## Task 2: Add `visit_overlap` pure helper

**Files:**
- Modify: `planner.py` (insert new function immediately after `print_trip`, around line 203)
- Test: `tests/test_planner_algos.py` (append new `TestVisitOverlap` class)

- [ ] **Step 1: Write the failing tests**

First, extend the imports at the top of `tests/test_planner_algos.py` to include the new symbol. Change:

```python
from planner import (
    parse_workweek, daterange, candidate_breaks,
    best_single_break, best_portfolio, classify_day,
    DEFAULT_LABELS,
)
```

to:

```python
from planner import (
    parse_workweek, daterange, candidate_breaks,
    best_single_break, best_portfolio, classify_day,
    visit_overlap,
    DEFAULT_LABELS,
)
```

Then append at the bottom of `tests/test_planner_algos.py`, before `if __name__ == "__main__":`:

```python
# ─── visit_overlap ───────────────────────────────────────────────────────

class TestVisitOverlap(unittest.TestCase):
    def _trip(self, start_str, end_str):
        return {
            "start": date.fromisoformat(start_str),
            "end": date.fromisoformat(end_str),
            "pto": [], "cost": 0, "length": 1,
        }

    def test_no_visit_red_days_returns_empty(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        self.assertEqual(visit_overlap(trip, {}), [])

    def test_returns_only_dates_inside_trip(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        visit_red = {
            date(2026, 10, 9): "Before",
            date(2026, 10, 12): "Dashain",
            date(2026, 10, 13): "Vijaya Dashami",
            date(2026, 10, 16): "After",
        }
        result = visit_overlap(trip, visit_red)
        self.assertEqual(
            result,
            [(date(2026, 10, 12), "Dashain"),
             (date(2026, 10, 13), "Vijaya Dashami")],
        )

    def test_inclusive_at_both_endpoints(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        visit_red = {
            date(2026, 10, 10): "Start",
            date(2026, 10, 15): "End",
        }
        result = visit_overlap(trip, visit_red)
        self.assertEqual(
            result,
            [(date(2026, 10, 10), "Start"),
             (date(2026, 10, 15), "End")],
        )

    def test_sorted_by_date(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        visit_red = {
            date(2026, 10, 14): "Later",
            date(2026, 10, 11): "Earlier",
        }
        result = visit_overlap(trip, visit_red)
        self.assertEqual([d for d, _ in result],
                         [date(2026, 10, 11), date(2026, 10, 14)])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_planner_algos.TestVisitOverlap -v`

Expected: FAIL with `ImportError: cannot import name 'visit_overlap' from 'planner'`

- [ ] **Step 3: Add `visit_overlap` to `planner.py`**

Insert the following new function in `planner.py` immediately after the `print_trip` function (i.e. between the current `print_trip` and `print_nearby_festivals`, around line 203):

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_planner_algos.TestVisitOverlap -v`

Expected: PASS — all 4 tests pass.

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add planner.py tests/test_planner_algos.py
git commit -m "feat(planner): add visit_overlap helper for trip/visit-country intersection"
```

---

## Task 3: Thread visit overlay through `print_trip`

**Files:**
- Modify: `planner.py` (function `print_trip` at lines 193–202)

There is no dedicated unit test for `print_trip` (it writes to stdout). The two underlying functions it depends on — `classify_day` and `visit_overlap` — are already covered by Task 1 and Task 2. This task is a pure integration wiring change.

- [ ] **Step 1: Replace `print_trip`**

Replace the entire `print_trip` function in `planner.py` (lines 193–202) with:

```python
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
```

- [ ] **Step 2: Confirm the full planner test module still passes**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_planner_algos -v`

Expected: PASS — all tests in the module pass (the new optional kwargs are backward-compatible with all current call sites).

- [ ] **Step 3: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add planner.py
git commit -m "feat(planner): print_trip threads visit overlay tag and summary line"
```

---

## Task 4: Wire `--visit` flag in `main()`

**Files:**
- Modify: `planner.py` (function `main()`, especially around the argparse block at lines 227–264 and the two `print_trip` call sites at lines 358 and 375)

- [ ] **Step 1: Add `--visit` argparse entry**

In `planner.py` inside `main()`, immediately after the `--country` argparse entry (currently at lines 244–245), insert:

```python
    ap.add_argument("--visit", default=cfg.get("visit"),
                    help="Destination country (ISO 2-letter). Overlays "
                         "its red days as annotations onto each trip.")
```

- [ ] **Step 2: Load visit red days after `compute_calendar`**

In `planner.py`, locate line 328 (the `off_days, red_days, festivals = compute_calendar(...)` call) and insert immediately after it:

```python
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
```

- [ ] **Step 3: Pass overlay through both `print_trip` call sites**

In `planner.py`, locate the `print_trip(longest, red_days, festivals, weekend_days, labels)` call (currently at line 358) and change it to:

```python
            print_trip(longest, red_days, festivals, weekend_days, labels,
                       visit_red_days, visit_country)
```

Then locate the `print_trip(p, red_days, festivals, weekend_days, labels)` call inside the portfolio loop (currently at line 375) and change it to:

```python
            print_trip(p, red_days, festivals, weekend_days, labels,
                       visit_red_days, visit_country)
```

- [ ] **Step 4: Smoke-test the wiring against the actual library**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 planner.py --budget 5 --country KR --visit NP --year 2026 --strategy longest --workweek sat,sun`

Expected output: A LONGEST SINGLE BREAK trip prints, AND if any day inside that trip is a NP red day per the `holidays` library for 2026, you see a `🌏 LOCAL HOLIDAY (NP) — …` tag on that day plus a final line `In-country NP holidays during this trip: …`. If the chosen trip happens to contain no NP red days, try a wider budget (e.g. `--budget 20`) — Dashain in October will appear in any long break that spans early-mid October 2026.

Also run the negative case:
`python3 planner.py --budget 5 --country KR --visit ZZ --year 2026 --strategy longest --workweek sat,sun`

Expected: a one-line warning `⚠️  --visit ZZ: not supported by the holidays library. Continuing without overlay.` followed by a normal plan without any 🌏 tags.

And the same-country no-op:
`python3 planner.py --budget 5 --country KR --visit KR --year 2026 --strategy longest --workweek sat,sun`

Expected: a normal plan, no 🌏 tags, no warning.

- [ ] **Step 5: Confirm the test suite is still green**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests -v 2>&1 | tail -5`

Expected: `OK` with the test count up by 8 (4 from Task 1 + 4 from Task 2) versus baseline.

- [ ] **Step 6: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add planner.py
git commit -m "feat(planner): add --visit flag to overlay destination holidays"
```

---

## Task 5: Persist `--visit` via `--save` and document the schema

**Files:**
- Modify: `planner.py` (the `--save` block at lines 315–323)
- Modify: `config.py` (module docstring at lines 15–19)

- [ ] **Step 1: Extend the `--save` block in `planner.py`**

Replace the `--save` block in `planner.py` (currently lines 315–323) with:

```python
    if args.save:
        updates = {
            "country": args.country,
            "budget": args.budget,
            "workweeks": {args.country: workweek_spec},
        }
        if args.visit:
            updates["visit"] = args.visit.upper()
        user_config.save(updates)
        saved_visit = f", visit={args.visit.upper()}" if args.visit else ""
        print(f"✅ Saved to ~/.daysoff/config.json: "
              f"country={args.country}, budget={args.budget}, "
              f"workweek({args.country})={workweek_spec}{saved_visit}\n")
```

- [ ] **Step 2: Document `visit` in the config schema**

In `config.py`, replace the documented-schema block in the module docstring (currently lines 15–19) with:

```python
Stable keys (documented schema — don't invent new ones casually):
    budget       int     — number of PTO days available
    country      str     — ISO 2-letter country code (KR, NP, JP, ...)
    workweeks    dict    — {country_code: workweek_spec}, e.g. {"KR": "wed,thu"}
    visit        str     — default destination country for --visit overlay
```

- [ ] **Step 3: Smoke-test save and reload**

Run from a temp HOME so we don't clobber your real config:

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
TMP_HOME=$(mktemp -d) && \
  HOME="$TMP_HOME" python3 planner.py --budget 7 --country KR --visit NP \
    --workweek sat,sun --save --year 2026 --strategy longest && \
  echo "---reload---" && \
  HOME="$TMP_HOME" python3 planner.py --year 2026 --strategy longest && \
  rm -rf "$TMP_HOME"
```

Expected: first run prints `✅ Saved ... visit=NP`. Second run reuses budget=7, country=KR, visit=NP from the saved config and emits 🌏 NP tags / summary lines for any October trip.

- [ ] **Step 4: Confirm tests still pass**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -3`

Expected: `OK` (test count unchanged from Task 4).

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add planner.py config.py
git commit -m "feat(planner): persist --visit via --save; document config schema"
```

---

## Task 6: Update README and final verification

**Files:**
- Modify: `README.md` (the planner flag table around lines 131–145 and one new example)

- [ ] **Step 1: Add `--visit` to the planner flag table**

In `README.md`, locate the planner flag table (the rows starting with `| Flag | Default | Purpose |`). After the row for `--workweek`, insert a new row:

```
| `--visit CC` | from config | Destination country — overlays its red days on each trip (annotation only, doesn't affect PTO math) |
```

- [ ] **Step 2: Add a usage example**

In `README.md`, in the "Full command examples" section under the planner heading (around line 102), append after the existing examples:

```bash
# Travel from home KR to NP — see which trips overlap Nepal holidays
python3 planner.py --budget 15 --country KR --visit NP --from-today
```

- [ ] **Step 3: Run the full test suite**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests -v 2>&1 | tail -10`

Expected: `OK` — all tests pass, total count up by 8 from the original 103.

- [ ] **Step 4: Final manual smoke**

Run the canonical user story end-to-end:

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
python3 planner.py --budget 15 --country KR --visit NP --year 2026 \
  --workweek sat,sun --strategy both --from-today
```

Expected: a normal KR plan with the visit-country overlay tags and summary lines appearing on any trip whose window contains 2026 NP red days (Dashain falls in October, Tihar in November — at least one will overlap a long break in any 15-day-budget portfolio).

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add README.md
git commit -m "docs: document --visit flag in planner usage"
```

---

## Done criteria

- All 6 tasks committed.
- `python3 -m unittest discover tests` reports OK with 8 new tests (4 `TestClassifyDayVisit` + 4 `TestVisitOverlap`).
- Manual run with `--country KR --visit NP` shows 🌏 tags on NP red days inside trips and `In-country NP holidays during this trip: …` summary lines.
- Same-country `--visit KR` is silently ignored.
- Unsupported `--visit ZZ` prints a single warning and continues with no overlay.
- `--save` persists `visit`; a subsequent run with no `--visit` flag picks it up from `~/.daysoff/config.json`.
- README documents the new flag.
