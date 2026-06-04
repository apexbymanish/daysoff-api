# Holiday cultural context via Wikipedia — design note

Brainstormed 2026-05-28. **Parked as future backend work** — not in
scope for the current Stitch-prompt-pack session.

## Goal

Show 1-paragraph cultural context for each holiday on the Holiday
detail sheet (Stitch Screen 4 — `docs/stitch/screens/04-holiday-detail-
sheet.md`). Today that text is hand-invented in the sample data;
replace with content fetched from a structured source. Example user
need: "show me what Dashain is" without leaving the app.

## Source

**Wikipedia REST API:**

```
https://en.wikipedia.org/api/rest_v1/page/summary/{title}
```

- Returns a ~150-word `extract` field (plain text), plus a thumbnail
  URL and the canonical Wikipedia page link.
- Stable, well-documented, no API key required.
- Per-language hosts available (`ko.wikipedia.org`, `ne.wikipedia.org`,
  etc.) — v1 ships English only; localization is v2.
- Polite request rate: < 100 req/sec per IP. Wikipedia asks callers
  to identify themselves via `User-Agent`.

**Why Wikipedia, not Google News:** Google News (already used by
`sources/news_kr.py` and `sources/news_np.py` for newly-announced
holidays) is too noisy for "what is Dashain?" — it surfaces current
events, not cultural context. Wikipedia gives stable encyclopedic
summaries.

## Code surface

- **New module:** `sources/wiki_source.py`
  - `fetch_summary(title: str, lang: str = "en") -> WikipediaSummary | None`
  - Returns `None` on 404 / network failure (caller decides UX).
  - Sets a polite `User-Agent: daysoff-api/1.0 (contact@daysoff.app)`.
- **Title resolution:** most holiday names map directly to Wikipedia
  titles ("Dashain", "Chuseok", "Seollal" all work). Edge cases need
  a small lookup table in `sources/wiki_titles.py` — e.g.,
  `"Children's Day" → "Children's_Day_(South_Korea)"`.
- **API surface:**
  - **Option B (recommended):** New endpoint
    `GET /v1/holidays/{country}/{date}/context` — lazy fetch, called
    only when the Holiday detail sheet opens. Keeps `/v1/holidays`
    response fast (one call returns N holidays).
  - **Option A (not recommended):** Augment `/v1/holidays` with a
    `summary` field on each row. With no cache, this serializes N
    Wikipedia calls per `/v1/holidays` request — bad latency.

## Caching

**Decision: no cache.** Per stated preference, no Wikipedia text is
persisted in `holidays.db`. Each call to
`/v1/holidays/{country}/{date}/context` makes a fresh HTTP request
to Wikipedia.

### Trade-offs being accepted

- **Latency:** ~100–300ms per holiday-detail open. Acceptable on
  tap (the bottom sheet already shows a loading state); becomes
  obvious if a user opens many sheets in quick succession.
- **Rate limits:** Wikipedia caps at ~200 req/sec per IP. Viable at
  v1 traffic; would need revisiting at scale.
- **Resilience:** If Wikipedia is unreachable, the detail sheet
  hides the "About" block and surfaces a small footer: "Cultural
  context unavailable."

### Alternative considered (and rejected for now)

**In-memory LRU cache** — `functools.lru_cache(maxsize=500)` on
`fetch_summary`. Never writes to disk, resets on process restart.
First call per (title, lang) hits Wikipedia; subsequent calls return
in ~10ms with zero stored data. Captures most of the latency win
without violating "don't store data" if that constraint is about
the database specifically rather than RAM.

Available to revisit if no-cache proves too slow in practice.

## Frontend (Stitch Screen 4)

Minimal change to the existing prompt:

- "About" block stays in the same position.
- Add a 12pt secondary attribution line below the paragraph: "From
  Wikipedia · English". Tap opens the source page in an in-app
  browser.
- Loading state: skeleton 3-line block while the fetch is in flight.
- Failure state: hide the About block entirely; render only the
  date hero + opportunities block.

`docs/stitch/screens/04-holiday-detail-sheet.md` should be updated
to reflect this once implementation begins. No update needed during
the current Stitch session — the design intent is unchanged.

## Out of scope

- Multi-language content (English summaries only for v1).
- Custom hand-authored context for marquee holidays.
- Translation of Wikipedia content.
- Persisting any Wikipedia content to `holidays.db` (explicitly
  excluded by the no-cache decision).
- Front-end implementation work — this is a backend feature.

## Next step

When this is picked up, run the brainstorming → writing-plans flow
on this spec. Expected deliverable: `sources/wiki_source.py`, a
new endpoint, tests covering the happy path + 404 + network failure,
and a README update.
