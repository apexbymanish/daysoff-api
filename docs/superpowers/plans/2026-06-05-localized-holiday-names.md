# Localized Holiday Names Implementation Plan (Sub-project A)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional `name_local` (native-language name) to each `/v1/holidays` holiday, derived from the `holidays` lib's own `default_language`.

**Architecture:** `sources/library_source.fetch` does a second native-language fetch and attaches `name_local`; `api/services.get_holidays` threads it through the merge; `api/schemas.HolidayRecord` gains `name_local: str | None = None`.

**Tech Stack:** Python, FastAPI, `holidays` PyPI package, pytest/unittest.

**Repo:** `/Users/manishadhikari/Documents/Projects/daysoff-api`, branch **`feat/localized-holiday-names`** (commit there, never switch). Baseline green: `pytest` 144 passing. Tests use `unittest.TestCase`; API tests use `fastapi.testclient.TestClient(app)` (see `tests/test_api_endpoints.py`). Run tests with the existing venv: `/tmp/daysoff-venv/bin/python -m pytest -q` (falls back to creating one if absent — see Task 0). Verified: `holidays.country_holidays('KR', years=2026, language='ko')` yields Korean names (2026-02-17 → 설날); `default_language` is `ko` for KR, `ja` for JP, `None`/`en_US` for NP/US.

## Out of scope
Localizing `/v1/plan`, `/v1/sandwiches`, `/v1/compare` names; per-request language; translating news/temp names.

---

## File Structure
```
sources/library_source.py     MODIFY: _localized_names() + name_local per record
api/services.py               MODIFY: carry name_local through get_holidays
api/schemas.py                MODIFY: HolidayRecord.name_local: str | None = None
tests/test_library_source.py  NEW: localized-name coverage
tests/test_api_endpoints.py   MODIFY: + name_local endpoint assertions
```

---

## Task 0: Ensure a test environment
- [ ] Confirm a venv with deps exists: `/tmp/daysoff-venv/bin/python -c "import holidays, fastapi"`. If it fails, create it:
```bash
/usr/bin/python3 -m venv /tmp/daysoff-venv && /tmp/daysoff-venv/bin/pip install -q -r /Users/manishadhikari/Documents/Projects/daysoff-api/requirements.txt pytest
```
- [ ] Baseline: `cd /Users/manishadhikari/Documents/Projects/daysoff-api && /tmp/daysoff-venv/bin/python -m pytest -q` → expect 144 passed.

---

## Task 1: Localized names in the library source

**Files:** Modify `sources/library_source.py`; Create `tests/test_library_source.py`

- [ ] **Step 1: Write the failing test** — `tests/test_library_source.py`:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sources import library_source


class LibrarySourceLocalizedTest(unittest.TestCase):
    def test_kr_records_have_korean_name_local(self):
        recs = library_source.fetch(2026, "KR")
        self.assertTrue(recs, "expected KR holidays")
        self.assertTrue(all("name_local" in r for r in recs))
        seollal = next(r for r in recs if r["date"].isoformat() == "2026-02-17")
        self.assertEqual(seollal["name_local"], "설날")

    def test_us_name_local_is_none(self):
        recs = library_source.fetch(2026, "US")
        self.assertTrue(recs, "expected US holidays")
        self.assertTrue(all(r["name_local"] is None for r in recs))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run → FAIL** — `/tmp/daysoff-venv/bin/python -m pytest tests/test_library_source.py -q` (records have no `name_local` key → KeyError/AssertionError).

- [ ] **Step 3: Implement** — replace `sources/library_source.py` with:
```python
"""Baseline holidays from the `holidays` PyPI package (offline, rule-based)."""
from datetime import date
import holidays


def _localized_names(country: str, year: int) -> dict[date, str]:
    """Map date→native-language name when the country has a non-English
    default language; otherwise an empty map (callers fall back to English)."""
    inst = holidays.country_holidays(country, years=year)
    lang = getattr(inst, "default_language", None)
    if not lang or lang.split("_")[0] == "en":
        return {}
    try:
        localized = holidays.country_holidays(country, years=year, language=lang)
        return dict(localized.items())
    except (NotImplementedError, KeyError, ValueError):
        return {}


def fetch(year: int, country: str = "KR") -> list[dict]:
    py_holidays = holidays.country_holidays(country, years=year)
    local = _localized_names(country, year)
    return [
        {
            "date": d,
            "name": name,
            "name_local": local.get(d),
            "country": country,
            "source": "library",
        }
        for d, name in sorted(py_holidays.items())
    ]
```

- [ ] **Step 4: Run → PASS** — `/tmp/daysoff-venv/bin/python -m pytest tests/test_library_source.py -q`.

- [ ] **Step 5: Commit**:
```bash
git add sources/library_source.py tests/test_library_source.py
git commit -m "feat(holidays): attach native-language name_local in library source"
```

---

## Task 2: Thread name_local through the service + schema + endpoint

**Files:** Modify `api/services.py`, `api/schemas.py`, `tests/test_api_endpoints.py`

- [ ] **Step 1: Write the failing endpoint tests** — add to `tests/test_api_endpoints.py`, inside the holidays `TestCase` class (the one whose `setUp` does `self.client = TestClient(app)` and tests `/v1/holidays`):
```python
    def test_kr_holidays_include_korean_name_local(self):
        r = self.client.get("/v1/holidays?country=KR&year=2026")
        self.assertEqual(r.status_code, 200)
        hols = r.json()["holidays"]
        self.assertTrue(all("name_local" in h for h in hols))
        self.assertTrue(any(h.get("name_local") == "설날" for h in hols))

    def test_us_holidays_name_local_null(self):
        r = self.client.get("/v1/holidays?country=US&year=2026")
        self.assertEqual(r.status_code, 200)
        hols = r.json()["holidays"]
        self.assertTrue(all(h["name_local"] is None for h in hols))
```

- [ ] **Step 2: Run → FAIL** — `/tmp/daysoff-venv/bin/python -m pytest tests/test_api_endpoints.py -q` (the schema drops `name_local`, so the key is absent).

- [ ] **Step 3a: Add the schema field** — in `api/schemas.py`, change `HolidayRecord` to:
```python
class HolidayRecord(BaseModel):
    date: date
    name: str
    name_local: str | None = None
    source: str
```

- [ ] **Step 3b: Carry it through the merge** — in `api/services.py` `get_holidays`, change the `merged.append({...})` block to include `name_local`:
```python
        merged.append({
            "date": r["date"],
            "name": r["name"],
            "name_local": r.get("name_local"),
            "source": r["source"],
        })
```
(News-source records have no `name_local` key, so `.get()` yields `None` for them — intended.)

- [ ] **Step 4: Run → PASS + full gate** — `/tmp/daysoff-venv/bin/python -m pytest tests/test_api_endpoints.py -q`, then the full suite `/tmp/daysoff-venv/bin/python -m pytest -q` (expect 148 passed: 144 + 2 library + 2 endpoint).

- [ ] **Step 5: Commit**:
```bash
git add api/services.py api/schemas.py tests/test_api_endpoints.py
git commit -m "feat(api): expose name_local on /v1/holidays records"
```

---

## Self-review
- **Spec coverage:** name_local via default_language ✓ (T1); schema field + service threading + endpoint exposure ✓ (T2); KR Korean + US null tested ✓; news records → None ✓.
- **Placeholder scan:** none — full code in every step.
- **Type consistency:** `_localized_names(country, year) -> dict[date,str]`; records carry `name_local` (str|None); `HolidayRecord.name_local: str | None = None`; endpoint JSON key `name_local`. The `(date, name)` dedup key is unchanged.

## Done when
`pytest` green (148); `GET /v1/holidays?country=KR&year=2026` returns each holiday with a `name_local` (Korean where available), and `?country=US` returns `name_local: null`. The mobile app (sub-project B) can then display native names.
