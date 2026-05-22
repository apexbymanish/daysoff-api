# daysoff-api — Session Progress Log

> **Use this file to pick up where we left off.** Updated on each session
> wrap-up. Read top-to-bottom for product context, then jump to the
> "What's next" section.

**Last updated:** 2026-05-22

---

## Product vision (locked)

`daysoff` is a **multi-source holiday aggregator + vacation planner**
becoming a **two-audience mobile product**:

1. **Employees (B2C)** — browse holidays, see sandwich-day opportunities,
   later: push reminders before each opportunity, save preferences on
   device.
2. **Employers (B2B, v2+)** — manager view of the same data ("expect low
   staffing on these dates"). Future direction: integrate with HR
   systems (BambooHR, Workday) to flag sandwich-likely leave requests for
   approval.

### Sub-project roadmap

| # | Sub-project | Status |
|---|---|---|
| A | Read-only public API | **spec + plan written, implementation pending** |
| B | Employee mobile app v1 — separate repo (`daysoff-mobile`) | Not started — will need its own spec |
| C | Auth + push notifications | Not started |
| D | `POST /plan` vacation planner endpoint | Not started |
| E | Employer/B2B mode + HR integration | v2+ — noted in spec, no concrete plan |

**Approved v1 product scope:** A + B ship together. C and D come after.

---

## What has shipped

### `feat/visit-country-overlay` → PR #1 (open, awaiting merge)

**Branch:** `feat/visit-country-overlay`
**PR:** https://github.com/apexbymanish/daysoff-api/pull/1
**Status:** Open, all tests passing (111).

What it adds:
- `--visit CC` flag on `planner.py` — overlays destination-country red
  days as annotations on each trip.
- Days inside a trip that are red in the visit country get a `🌏 LOCAL
  HOLIDAY (CC) — <name>` tag alongside the primary tag.
- Per-trip summary line: `In-country NP holidays during this trip: …`
  (only when there's overlap).
- `--visit` persists via `--save`. Same-country `--visit` silent no-op.
  Unsupported country prints a warning and continues without overlay.
- Two new helpers in `planner.py`: extended `classify_day` (kwargs:
  `visit_red_days`, `visit_country`) and pure `visit_overlap(trip,
  visit_red_days)`.
- 8 new tests: `TestClassifyDayVisit` (4) + `TestVisitOverlap` (4).

Spec: `docs/superpowers/specs/2026-05-22-visit-country-overlay-design.md`
Plan: `docs/superpowers/plans/2026-05-22-visit-country-overlay.md`

---

## What's in flight

### `feat/read-api` → unimplemented (spec + plan committed)

**Branch:** `feat/read-api`
**Status:** Spec and plan committed; implementation about to begin via
subagent-driven execution.

**Spec:** `docs/superpowers/specs/2026-05-22-read-api-design.md`
**Plan:** `docs/superpowers/plans/2026-05-22-read-api.md` (7 tasks, TDD)

Endpoint surface (all under `/v1/`):

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/healthz` | Liveness |
| `GET` | `/v1/countries` | 250 ISO-2 codes + news-enrichment flag |
| `GET` | `/v1/holidays` | Library + news merge for one country/year |
| `GET` | `/v1/compare` | N-way intersection + per-country uniques |
| `GET` | `/v1/sandwiches` | Sandwich days with workweek cascade |

**Locked design decisions:**
- FastAPI + Pydantic v2, Python 3.11, Dockerized.
- Public, no auth, CORS allow-all.
- Country-level only (no subdivisions in v1 — deferred).
- News data: KR + NP only (no scaling in v1 — deferred to a separate
  "news-scaling" spec).
- Hosting: hosting-agnostic spec; starter `fly.toml` ships in the repo.
- `holidays.db` is **not** baked into the image; ships empty.

**Out of scope explicitly:** auth, push notifications, planner endpoint,
B2B mode, mobile app, subdivisions, generic news scraper, LLM extraction,
rate limiting.

---

## Architecture invariants worth preserving

1. **`api/services.py` contains no holiday logic.** It only adapts the
   existing `sources/`, `sandwich`, `storage`, `planner` modules. If a
   helper is missing, add it there first.
2. **CLI and API serve the same code paths** — no duplication. Adding a
   feature to one should reach the other for free.
3. **DB writes only from the CLI**, not from API requests. The API is
   read-only.
4. **Existing 111-test baseline must stay green** through every change.

---

## What's next (in priority order)

1. **Execute `feat/read-api` plan via subagent-driven-development** —
   7 tasks, TDD, ~26 new tests, ends with PR #2.
2. **Merge PR #1 (`feat/visit-country-overlay`)** once reviewed.
3. **Merge PR #2 (`feat/read-api`)** once it lands.
4. **Brainstorm sub-project B** — mobile app spec, separate repo
   (`daysoff-mobile`). Pick stack (React Native vs Flutter), decide
   on-device storage strategy.
5. **Deploy v1 API to Fly.io** (or Render). Verify endpoints from the
   public internet. Document the deploy URL for the mobile dev.
6. **Spec sub-project C** — auth + push notifications. Becomes
   prerequisite for "reminders X days before each sandwich opportunity".
7. **Spec the news-scaling sub-project** — generic config-driven scraper
   covering PH, ID, VN, IN, BR etc. Two options designed during
   brainstorming: config-driven (recommended) or LLM extraction.

---

## How to resume in a future session

If you (or a future Claude) are picking this up:

1. Read **this file** for context.
2. Check the open PRs: `gh pr list`.
3. Check branch state: `git branch -a` and `git log --oneline -20`.
4. Read the latest spec/plan in `docs/superpowers/{specs,plans}/`.
5. If executing a plan, invoke `superpowers:subagent-driven-development`
   or `superpowers:executing-plans`.
6. After significant work, **update this file** so the next session
   starts with the right context.

---

## Reference

- Project root: `/Users/manishadhikari/Documents/Projects/daysoff-api`
- GitHub: https://github.com/apexbymanish/daysoff-api
- Main branch: `main` (currently at the initial commit)
- Test command: `python3 -m unittest discover tests`
- Local API run: `python3 -m uvicorn api.main:app --reload` (once
  `feat/read-api` is implemented)
