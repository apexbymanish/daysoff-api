# Localized Holiday Names — Design (Sub-project A)

**Date:** 2026-06-05
**Status:** Approved (design)

## Goal

Add a `name_local` field (native-language holiday name) to each holiday returned by `/v1/holidays`,
so the mobile app can show e.g. *설날* under "Seollal Lunar New Year". This is sub-project A of the
6.1 Home redesign; the mobile app (sub-project B) consumes this field.

## Background

`/v1/holidays` currently returns `{date, name, source}` with English-only names. The `holidays` PyPI
package supports a `language=` argument and exposes each country's native language as
`instance.default_language`. Verified behaviour (2026):

| Country | `default_language` | localized sample |
|---|---|---|
| KR | `ko` | 신정연휴, 설날 |
| JP | `ja` | 元日, 成人の日 |
| NP | `None` | (no translations — English names are already the local ones) |
| US | `en_US` | (English) |

So the native language can be derived from the lib itself — **no hand-maintained country→language map
is needed.**

## Approach

In `sources/library_source.py`, after the normal English fetch, do a second fetch in the country's
native language (when `default_language` is non-English) and attach `name_local` to each record.
Thread `name_local` through `api/services.get_holidays`, and add it to the `HolidayRecord` schema.

### Rule for the native language
```
inst = holidays.country_holidays(country, years=year)
lang = inst.default_language            # e.g. 'ko', 'ja', 'en_US', or None
use localization only if lang is truthy AND lang.split('_')[0] != 'en'
```
When localization is not used, `name_local` is `None` (the app falls back to the English `name`).

## Changes

### `sources/library_source.py`
- Add `def _localized_names(country, year) -> dict[date, str]`: returns `{date: localized_name}` using
  the native-language fetch per the rule above; returns `{}` when no native localization applies (and
  swallows `NotImplementedError`/lookup errors defensively → `{}`).
- `fetch(year, country)` builds each record as
  `{"date": d, "name": name, "name_local": local_map.get(d), "country": country, "source": "library"}`.

### `api/services.py` — `get_holidays`
- The merged record dict gains `"name_local": r.get("name_local")`. News-source records have no native
  name, so theirs is `None` (the app shows the English/native `name`, which for 임시공휴일 is already
  Korean). The dedup key stays `(date, name)`.

### `api/schemas.py` — `HolidayRecord`
- Add `name_local: str | None = None` (optional, defaults to None → backward compatible; existing
  clients and the other endpoints are unaffected).

## Testing

- **`tests/` library source:** `library_source.fetch(2026, "KR")` — every record has a `name_local`
  key; the record for Seollal (2026-02-17) has `name_local == "설날"` (or assert it contains Hangul /
  differs from the ASCII English name). A US fetch (`fetch(2026, "US")`) yields `name_local is None`
  for all records (English default).
- **service:** `get_holidays("KR", 2026)` records include `name_local`; at least one is non-None and
  non-ASCII.
- **API endpoint:** `GET /v1/holidays?country=KR&year=2026` — each holiday object includes
  `name_local`; a known Korean name is present. `GET ...?country=US&year=2026` — `name_local` is null.
- **Regression:** full `pytest` green; the existing `(date, name)` dedup and response shape unchanged
  apart from the added optional field.

## Out of scope

Localizing names in `/v1/plan`, `/v1/sandwiches`, `/v1/compare` anchors (English there is fine for
now); per-request language selection; translating news/temp holiday names.

## File summary
```
sources/library_source.py    MODIFY: _localized_names() + name_local in records
api/services.py              MODIFY: carry name_local through get_holidays merge
api/schemas.py               MODIFY: HolidayRecord.name_local: str | None = None
tests/test_*.py              ADD: name_local coverage (library + service + endpoint)
```
