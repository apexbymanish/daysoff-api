# daysoff-api — TODO / Follow-ups

Recorded 2026-06-05.

## 1. Official-only holidays + always-fresh (HIGH — designed, not yet built)

**Problem.** `/v1/holidays` currently unions `library_source` + **`news_source`** (a Google-News RSS
scraper for 임시공휴일). The scraper is loose — it surfaces *unconfirmed* "temporary holiday" candidates
from headlines (e.g. KR 2026-06-05 and 2026-06-08 show as `임시공휴일 (news-detected)`, source `news`),
which are **not official holidays**. Real June holidays are only Jun 3 (Local Election Day) and Jun 6
(Memorial Day). The app marks these news guesses identically to real days off → misleading.

**Decision (approved 2026-06-05).** Make holiday data **official-only and live**:
- In `api/services.get_holidays`, replace `news_source` with the **official `gov_api_source`**
  (Korea Public Data Portal — `getRestDeInfo`, already implemented in `sources/gov_api_source.py`,
  authoritative for substitute/temporary holidays).
- **Dedupe by DATE** when merging gov_api into the library union (not by `(date, name)`), because
  gov_api returns Korean `dateName`s that would otherwise duplicate the library's English-named
  holidays. gov_api should only ADD official dates the library lacks (e.g. a freshly-declared temp
  holiday); for a temp date, set `name`/`name_local` from the gov `dateName`.
- **Drop `news_source` from the holidays union.** Keep `news_kr`/`news_np`/`storage.py` for the CLI's
  "newly-announced" tracker if still wanted, but the API endpoint must not use the speculative scraper.
- **No cache / always refresh:** `gov_api_source.fetch` already hits the live endpoint each call (no
  memoization on the endpoint today — confirmed). Add `Cache-Control: no-store` to `/v1/holidays` to
  make this explicit. The endpoint never used `holidays.db`.

**Caveat / prerequisite.** `gov_api_source` needs `DATA_GO_KR_KEY` (free key from https://data.go.kr).
Without it, gov_api returns `[]`, so the union falls back to the **offline `holidays` library only** —
which already includes all real public + substitute holidays; you just won't get *live* API-sourced
temps until the key is configured. (This still removes the false Jun 5/8 — net win.)

**Tests to add.** `get_holidays('KR', 2026)` contains **no** `source == 'news'` / "news-detected"
records; with `gov_api_source.fetch` monkeypatched to return a temp date not in the library, it appears
with `source == 'gov_api'`; a gov_api date that duplicates a library date is not double-added.

## 2. Other parked backend follow-ups
- Wikipedia context enrichment, holiday images, user-data/Firebase — see
  `docs/superpowers/specs/2026-05-28-*` (parked).
- Backend **auth tier** (the API is currently public; mobile Profile/auth is blocked on this).
