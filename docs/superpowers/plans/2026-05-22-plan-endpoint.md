# `/v1/plan` Vacation-Planner Endpoint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `GET /v1/plan` endpoint that, for a country + PTO budget, returns the best break alternative(s) of each requested length, by reusing `planner.candidate_breaks` and the workweek cascade from `/v1/sandwiches`.

**Architecture:** Pure additive change to the existing `api/` package — one new service function (`get_plans`), two new Pydantic models (`PlanTrip`, `PlanResponse`), one new FastAPI route. The internal workweek-resolver `_resolve_workweek_for_sandwiches` is renamed to `_resolve_workweek` (now shared between `/v1/sandwiches` and `/v1/plan`). No new modules; no logic added outside `api/services.py`.

**Tech Stack:** Python 3.10+, FastAPI, Pydantic v2, unittest via `fastapi.testclient.TestClient`. Same stack as the rest of `api/`.

**Spec:** `docs/superpowers/specs/2026-05-22-plan-endpoint-design.md`

---

## File Structure

| File | Role |
|---|---|
| `api/services.py` (modify) | Rename `_resolve_workweek_for_sandwiches` → `_resolve_workweek` (also update the one caller in `get_sandwiches`); add `get_plans()`. |
| `api/schemas.py` (modify) | Add `PlanTrip` and `PlanResponse` Pydantic models. |
| `api/main.py` (modify) | Add `GET /v1/plan` route wired to `services.get_plans`. |
| `tests/test_api_endpoints.py` (modify) | Add `TestPlan` class with 8 tests. |
| `README.md` (modify) | Add `/v1/plan` row to the endpoints table. |

Nothing else changes. Existing 128 tests stay green; final count: 136.

---

## Task 1: Rename `_resolve_workweek_for_sandwiches` → `_resolve_workweek`

This is a no-behavior-change refactor. We do it first, in isolation, so it shows up as a clean diff and so the `/v1/plan` code can call `_resolve_workweek` without confusion.

**Files:**
- Modify: `api/services.py`

- [ ] **Step 1: Run the test suite to capture the baseline**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: `Ran 128 tests in ...` ending with `OK`.

- [ ] **Step 2: Rename the helper definition**

In `api/services.py` (around line 168), change:

```python
def _resolve_workweek_for_sandwiches(country: str, workweek: str | None
                                     ) -> tuple[set[int], list[str], str]:
    """Return (weekend_days_int_set, weekend_days_str_list, source_string).

    Cascade: explicit param → most recent policy → hardcoded fallback → 400.
    """
```

to:

```python
def _resolve_workweek(country: str, workweek: str | None
                      ) -> tuple[set[int], list[str], str]:
    """Return (weekend_days_int_set, weekend_days_str_list, source_string).

    Cascade: explicit param → most recent policy → hardcoded fallback → 400.
    Shared between /v1/sandwiches and /v1/plan.
    """
```

- [ ] **Step 3: Update the call site inside `get_sandwiches`**

In `api/services.py` (around line 205), change:

```python
    weekend_set, weekend_names, source = _resolve_workweek_for_sandwiches(
        cc, workweek
    )
```

to:

```python
    weekend_set, weekend_names, source = _resolve_workweek(cc, workweek)
```

- [ ] **Step 4: Verify the rename did not break anything**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && grep -n "_resolve_workweek_for_sandwiches" api/ tests/ -r`
Expected: no matches (the old name is fully gone).

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: `Ran 128 tests in ...` ending with `OK`. No skipped, no failures.

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add api/services.py
git commit -m "$(cat <<'EOF'
refactor(api): rename _resolve_workweek_for_sandwiches → _resolve_workweek

Prep for /v1/plan, which reuses the same workweek cascade. The helper
is no longer sandwich-specific.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Add `PlanTrip` and `PlanResponse` schemas

Schemas land before the service function so that `get_plans` can construct dict payloads the route will validate against these models.

**Files:**
- Modify: `api/schemas.py`

- [ ] **Step 1: Add the two new models at the bottom of `api/schemas.py`**

Append after the existing `SandwichesResponse` class:

```python


class PlanTrip(BaseModel):
    break_start: date
    break_end: date
    break_length: int
    pto_dates: list[date]
    pto_cost: int
    anchors: list[str]


class PlanResponse(BaseModel):
    country: str
    year: int
    budget: int
    workweek: list[str]
    workweek_source: str
    results_by_length: dict[str, list[PlanTrip]]
```

- [ ] **Step 2: Verify the module still imports cleanly**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -c "from api.schemas import PlanTrip, PlanResponse; print('ok')"`
Expected: prints `ok` (no `ImportError`, no Pydantic schema error).

- [ ] **Step 3: Re-run the existing suite**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: still 128 tests, all `OK`.

- [ ] **Step 4: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add api/schemas.py
git commit -m "$(cat <<'EOF'
feat(api): add PlanTrip and PlanResponse schemas for /v1/plan

results_by_length keys are stringified ints (JSON object keys cannot
be ints). Mobile clients should treat them as numeric.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Happy-path `get_plans` + wire `/v1/plan` route (menu view)

This is the largest task. We write the canonical menu-view test first, then build the minimum service + route to make it pass. Single-length mode, top-K sort, and validation come in later tasks.

**Files:**
- Modify: `tests/test_api_endpoints.py`, `api/services.py`, `api/main.py`

- [ ] **Step 1: Add the failing menu-view test**

Append at the bottom of `tests/test_api_endpoints.py`, **before** `if __name__ == "__main__":`:

```python


class TestPlan(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_menu_view_returns_one_per_length_in_range(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=3&max_length=7&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["country"], "KR")
        self.assertEqual(body["year"], 2026)
        self.assertEqual(body["budget"], 15)
        self.assertEqual(body["workweek"], ["sat", "sun"])
        # range 3..7 = 5 lengths, each capped at top=1 (default)
        self.assertEqual(
            sorted(body["results_by_length"].keys()),
            ["3", "4", "5", "6", "7"],
        )
        for length_key, entries in body["results_by_length"].items():
            self.assertLessEqual(len(entries), 1)
            for trip in entries:
                self.assertEqual(trip["break_length"], int(length_key))
                self.assertIn("break_start", trip)
                self.assertIn("break_end", trip)
                self.assertIn("pto_dates", trip)
                self.assertIn("pto_cost", trip)
                self.assertIn("anchors", trip)
```

- [ ] **Step 2: Verify the test fails for the right reason**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_api_endpoints.TestPlan -v 2>&1 | tail -15`
Expected: failure with status code `404` (route not registered yet).

- [ ] **Step 3: Implement `get_plans` in `api/services.py`**

Add the following at the bottom of `api/services.py` (after `get_sandwiches`):

```python


def _trip_to_payload(trip: dict, red_days: dict) -> dict:
    """Shape one candidate_breaks output into the API trip dict.

    `trip` keys (from planner.candidate_breaks): start, end, pto, cost, length.
    `red_days`: {date: name} from planner.compute_calendar.
    """
    anchor_names: list[str] = []
    seen_names: set[str] = set()
    for d in daterange(trip["start"], trip["end"]):
        name = red_days.get(d)
        if name and name not in seen_names:
            seen_names.add(name)
            anchor_names.append(name)
    return {
        "break_start": trip["start"],
        "break_end": trip["end"],
        "break_length": trip["length"],
        "pto_dates": list(trip["pto"]),
        "pto_cost": trip["cost"],
        "anchors": anchor_names,
    }


def get_plans(country: str, year: int, budget: int,
              length: int | None = None,
              min_length: int = 3, max_length: int = 10,
              top: int = 1,
              workweek: str | None = None,
              from_today: bool = False) -> dict:
    """Return the /v1/plan response body as a plain dict.

    Two modes:
      - length set: returns only that length, up to `top` entries.
      - length unset: returns each length in [min_length, max_length],
        up to `top` entries each.
    """
    cc = _validate_country(country)
    _validate_year(year)
    if budget < 0:
        raise ApiInputError(f"budget must be >= 0, got {budget}")
    if top < 1:
        raise ApiInputError(f"top must be >= 1, got {top}")

    if length is not None:
        if length < 1 or length > 31:
            raise ApiInputError(
                f"length must be in [1, 31], got {length}"
            )
        wanted_lengths = [length]
    else:
        if min_length < 1 or max_length > 31:
            raise ApiInputError(
                f"min_length/max_length must be in [1, 31], "
                f"got [{min_length}, {max_length}]"
            )
        if min_length > max_length:
            raise ApiInputError(
                f"min_length ({min_length}) > max_length ({max_length})"
            )
        wanted_lengths = list(range(min_length, max_length + 1))

    weekend_set, weekend_names, source = _resolve_workweek(cc, workweek)

    off_days, red_days, _festivals = compute_calendar(year, cc, weekend_set)
    cap = max(wanted_lengths)
    candidates = candidate_breaks(year, off_days, budget, max_break_len=cap)

    if from_today:
        today = _date.today()
        candidates = [c for c in candidates if c["start"] >= today]

    wanted_set = set(wanted_lengths)
    results_by_length: dict[str, list[dict]] = {str(L): [] for L in wanted_lengths}
    grouped: dict[int, list[dict]] = {L: [] for L in wanted_lengths}
    for c in candidates:
        if c["length"] in wanted_set:
            grouped[c["length"]].append(c)

    for L, trips in grouped.items():
        trips.sort(key=lambda t: (t["cost"], t["start"]))
        results_by_length[str(L)] = [
            _trip_to_payload(t, red_days) for t in trips[:top]
        ]

    return {
        "country": cc,
        "year": year,
        "budget": budget,
        "workweek": weekend_names,
        "workweek_source": source,
        "results_by_length": results_by_length,
    }
```

- [ ] **Step 4: Add the missing imports at the top of `api/services.py`**

The new code uses `compute_calendar` and `candidate_breaks` from `planner`. Update the existing `from planner import ...` line (currently around line 14) so it reads:

```python
from planner import (
    WEEKDAY_MAP, WORKWEEK_FALLBACKS, candidate_breaks, compute_calendar,
    daterange, parse_workweek,
)
```

- [ ] **Step 5: Add the `/v1/plan` route in `api/main.py`**

Append the following at the bottom of `api/main.py` (after the `sandwiches` route, keeping it the last route in the file):

```python


@app.get("/v1/plan", response_model=schemas.PlanResponse)
def plan(
    country: str = Query(..., description="ISO-2 country code"),
    budget: int = Query(..., description="Total PTO days available (>= 0)"),
    year: int = Query(default_factory=lambda: _date.today().year),
    length: int | None = Query(
        default=None,
        description="If set, focus on this single length and ignore min_length/max_length",
    ),
    min_length: int = Query(3, description="Inclusive lower bound (ignored if length is set)"),
    max_length: int = Query(10, description="Inclusive upper bound (ignored if length is set)"),
    top: int = Query(1, description="Max alternatives per length"),
    workweek: str | None = Query(default=None, description="Comma list of OFF days, e.g. sat,sun"),
    from_today: bool = Query(False),
) -> schemas.PlanResponse:
    result = services.get_plans(
        country, year, budget,
        length=length, min_length=min_length, max_length=max_length,
        top=top, workweek=workweek, from_today=from_today,
    )
    return schemas.PlanResponse(**result)
```

- [ ] **Step 6: Run the menu-view test to verify it passes**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_api_endpoints.TestPlan -v 2>&1 | tail -15`
Expected: `test_menu_view_returns_one_per_length_in_range ... ok`. One test, passing.

- [ ] **Step 7: Verify the full suite still passes**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: `Ran 129 tests in ...` ending with `OK`.

- [ ] **Step 8: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add api/services.py api/main.py tests/test_api_endpoints.py
git commit -m "$(cat <<'EOF'
feat(api): add /v1/plan menu view (one best break per length)

Wraps planner.candidate_breaks behind a length-buffet response.
results_by_length is keyed by stringified ints; values are sorted by
(pto_cost asc, break_start asc) and capped at `top` (default 1).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Drill-down mode + sort-order tests

Now add the `length=` override and the sort assertions. The service already supports both; we only add tests.

**Files:**
- Modify: `tests/test_api_endpoints.py`

- [ ] **Step 1: Add the drill-down test**

Inside the existing `TestPlan` class in `tests/test_api_endpoints.py`, append a new method:

```python
    def test_single_length_with_top_returns_alternatives(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&length=5&top=5&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        # Only key "5" is present, ignoring min/max defaults.
        self.assertEqual(list(body["results_by_length"].keys()), ["5"])
        entries = body["results_by_length"]["5"]
        self.assertLessEqual(len(entries), 5)
        self.assertGreater(len(entries), 0)
        for trip in entries:
            self.assertEqual(trip["break_length"], 5)
```

- [ ] **Step 2: Add the sort-order test**

Inside `TestPlan`, append:

```python
    def test_alternatives_sorted_by_pto_cost_ascending(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&length=5&top=5&workweek=sat,sun"
        )
        entries = r.json()["results_by_length"]["5"]
        if len(entries) < 2:
            self.skipTest("need at least 2 alternatives to compare sort order")
        for prev, curr in zip(entries, entries[1:]):
            self.assertLessEqual(prev["pto_cost"], curr["pto_cost"])
            if prev["pto_cost"] == curr["pto_cost"]:
                # tie-break: earlier break_start first
                self.assertLessEqual(prev["break_start"], curr["break_start"])
```

- [ ] **Step 3: Run the two new tests**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_api_endpoints.TestPlan -v 2>&1 | tail -15`
Expected: 3 tests pass (the original menu-view plus both new ones).

- [ ] **Step 4: Run the full suite**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: `Ran 131 tests in ...` ending with `OK`.

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add tests/test_api_endpoints.py
git commit -m "$(cat <<'EOF'
test(api): cover /v1/plan drill-down + sort order

Drill-down (length=5, top=5) returns only the requested length, capped
at top. Within a length, entries sort by (pto_cost asc, break_start asc).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Anchors + pto_dates/pto_cost consistency

Two more behaviour tests, again exercising existing logic.

**Files:**
- Modify: `tests/test_api_endpoints.py`

- [ ] **Step 1: Add the pto_dates/pto_cost consistency test**

Inside `TestPlan`, append:

```python
    def test_pto_dates_consistent_with_cost(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=3&max_length=10&workweek=sat,sun"
        )
        for entries in r.json()["results_by_length"].values():
            for trip in entries:
                self.assertEqual(len(trip["pto_dates"]), trip["pto_cost"])
```

- [ ] **Step 2: Add the anchors test (Chuseok inside a KR length-5 break)**

Chuseok 2026 falls on Fri 2026-09-25 (3-day holiday Thu–Sat per `holidays`
library), so length-5 breaks around it should include "Chuseok" in their
anchors. We assert that *at least one* length-5 trip contains "Chuseok" in
anchors — robust to scoring ties.

Inside `TestPlan`, append:

```python
    def test_anchors_present_when_break_spans_holiday(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&length=5&top=10&workweek=sat,sun"
        )
        entries = r.json()["results_by_length"]["5"]
        any_chuseok = any(
            any("Chuseok" in a for a in trip["anchors"])
            for trip in entries
        )
        self.assertTrue(
            any_chuseok,
            f"expected at least one length-5 trip with a Chuseok anchor; "
            f"got entries={entries}",
        )
```

- [ ] **Step 3: Run the new tests**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_api_endpoints.TestPlan -v 2>&1 | tail -15`
Expected: 5 tests pass.

If `test_anchors_present_when_break_spans_holiday` fails, debug by
printing the actual `entries` and the red-day names returned by
`library_source.fetch(2026, "KR")` — the holiday name may differ (e.g.
"Chuseok Holiday" — the substring match `"Chuseok" in a` still passes
in that case).

- [ ] **Step 4: Run the full suite**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: `Ran 133 tests in ...` ending with `OK`.

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add tests/test_api_endpoints.py
git commit -m "$(cat <<'EOF'
test(api): cover /v1/plan anchors + pto invariant

Asserts len(pto_dates) == pto_cost on every returned trip and that a
length-5 KR break around Chuseok surfaces "Chuseok" in anchors.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Validation errors (3 × 400 paths)

Now the negative tests. The service already raises `ApiInputError`; we
just need to assert the route returns 400 for each input shape.

**Files:**
- Modify: `tests/test_api_endpoints.py`

- [ ] **Step 1: Add the three error tests**

Inside `TestPlan`, append:

```python
    def test_unsupported_country_returns_400(self):
        r = self.client.get(
            "/v1/plan?country=ZZ&year=2026&budget=15&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("ZZ", r.json()["detail"])

    def test_min_greater_than_max_returns_400(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=10&max_length=5&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("min_length", r.json()["detail"])

    def test_no_workweek_with_no_policy_returns_400(self):
        # AQ has no saved policy and no entry in WORKWEEK_FALLBACKS.
        r = self.client.get(
            "/v1/plan?country=AQ&year=2026&budget=15"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("workweek", r.json()["detail"].lower())
```

- [ ] **Step 2: Run the new tests**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest tests.test_api_endpoints.TestPlan -v 2>&1 | tail -20`
Expected: 8 tests in `TestPlan` all pass.

- [ ] **Step 3: Run the full suite — final test count check**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: `Ran 136 tests in ...` ending with `OK`.

- [ ] **Step 4: Smoke-test the endpoint against a live server**

Run in one terminal: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8080`

In another shell, run:

```bash
curl -s 'http://127.0.0.1:8080/v1/plan?country=KR&year=2026&budget=15&min_length=3&max_length=10&workweek=sat,sun' | python3 -m json.tool | head -40
```

Expected: a JSON object with keys `country`, `year`, `budget`, `workweek`,
`workweek_source`, and `results_by_length` containing keys `"3"` through
`"10"`. Each value is a list of at most 1 trip dict.

Then run the drill-down:

```bash
curl -s 'http://127.0.0.1:8080/v1/plan?country=KR&year=2026&budget=15&length=5&top=5&workweek=sat,sun' | python3 -m json.tool | head -60
```

Expected: only key `"5"` is present in `results_by_length`; up to 5 trips.

Stop the server (Ctrl-C).

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add tests/test_api_endpoints.py
git commit -m "$(cat <<'EOF'
test(api): cover /v1/plan validation errors (400 paths)

Unsupported country, inverted min_length/max_length, and missing
workweek with no policy all map to HTTP 400 with descriptive detail.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: README — add `/v1/plan` to the endpoints table

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add the new row to the endpoints table**

In `README.md`, find the endpoints table (around line 279). The current table:

```markdown
| Path | Example |
|---|---|
| `/v1/healthz` | `curl localhost:8080/v1/healthz` |
| `/v1/countries` | `curl localhost:8080/v1/countries` |
| `/v1/holidays` | `curl 'localhost:8080/v1/holidays?country=KR&year=2026'` |
| `/v1/compare` | `curl 'localhost:8080/v1/compare?countries=KR,NP&year=2026'` |
| `/v1/sandwiches` | `curl 'localhost:8080/v1/sandwiches?country=KR&year=2026&workweek=sat,sun'` |
```

Add one row at the bottom so it becomes:

```markdown
| Path | Example |
|---|---|
| `/v1/healthz` | `curl localhost:8080/v1/healthz` |
| `/v1/countries` | `curl localhost:8080/v1/countries` |
| `/v1/holidays` | `curl 'localhost:8080/v1/holidays?country=KR&year=2026'` |
| `/v1/compare` | `curl 'localhost:8080/v1/compare?countries=KR,NP&year=2026'` |
| `/v1/sandwiches` | `curl 'localhost:8080/v1/sandwiches?country=KR&year=2026&workweek=sat,sun'` |
| `/v1/plan` | `curl 'localhost:8080/v1/plan?country=KR&year=2026&budget=15&min_length=3&max_length=10&workweek=sat,sun'` |
```

- [ ] **Step 2: Update the spec link list at the bottom of that section**

A few lines below the table is the line:

```markdown
Spec: [`docs/superpowers/specs/2026-05-22-read-api-design.md`](docs/superpowers/specs/2026-05-22-read-api-design.md).
```

Replace it with:

```markdown
Specs:
- [`docs/superpowers/specs/2026-05-22-read-api-design.md`](docs/superpowers/specs/2026-05-22-read-api-design.md) — `/v1/healthz`, countries, holidays, compare, sandwiches.
- [`docs/superpowers/specs/2026-05-22-plan-endpoint-design.md`](docs/superpowers/specs/2026-05-22-plan-endpoint-design.md) — `/v1/plan`.
```

- [ ] **Step 3: Update the stale "128 tests" annotation in the structure tree**

In `README.md` (around line 28), the structure block currently says:

```
├── tests/                     # unittest suite (128 tests)
```

Update to:

```
├── tests/                     # unittest suite (136 tests)
```

- [ ] **Step 4: Final full-suite run**

Run: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && python3 -m unittest discover tests 2>&1 | tail -5`
Expected: `Ran 136 tests in ...` ending with `OK`.

- [ ] **Step 5: Commit**

```bash
cd /Users/manishadhikari/Documents/Projects/daysoff-api
git add README.md
git commit -m "$(cat <<'EOF'
docs(api): document /v1/plan and refresh test count

Adds the /v1/plan endpoint row + spec link, bumps the structure-tree
test count to 136.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Done criteria (lifted from the spec)

- `/v1/plan?country=KR&year=2026&budget=15&workweek=sat,sun` returns a `PlanResponse` with at least one trip for each length in [3, 10].
- `?length=5&top=5` returns only `"5"`, up to 5 entries, all `break_length == 5`.
- All three error paths (`country=ZZ`, `min_length>max_length`, `country=AQ` without workweek) return 400 with descriptive `detail`.
- `python3 -m unittest discover tests` reports 136 tests, all OK.
- README lists `/v1/plan` and the test count tree is refreshed.
