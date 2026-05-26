# Read-Only Public API (v1) — Design Spec

**Date:** 2026-05-22
**Status:** Approved (brainstorm) — implementation pending
**Sub-project:** A of the daysoff product roadmap (see "Roadmap context" below)

## Problem

The daysoff codebase today is a Python CLI. To enable the mobile app (a
separate repo, separate spec) and any future web client, we need a
read-only HTTP API that exposes the existing holiday and sandwich-detection
logic over JSON.

## Goal

Stand up a stateless, public read-only FastAPI service that wraps the
existing `library_source`, `sandwich`, and `news_source` modules. Five
endpoints, no auth, no DB writes from API requests, deployable on a free
PaaS tier.

## Roadmap context

This spec implements **sub-project A** of the broader product roadmap:

| # | Sub-project | Status |
|---|---|---|
| **A** | Read-only public API | **this spec** |
| B | Employee mobile app v1 (browse + sandwich list, settings on-device) | Future spec, separate repo (`daysoff-mobile`) |
| C | Auth + push notifications | Future spec |
| D | Vacation planner endpoint + mobile UI | Future spec |
| E | Employer/B2B mode (HR integration noted for v2+) | Future spec |

Approved v1 product scope: **A + B** ship together. Reminders (C), planner
endpoint (D), and B2B (E) come later. This spec covers A only.

## Non-goals (explicitly out of scope)

- **Authentication, signup, sessions, JWTs** — sub-project C.
- **Per-user preferences, saved plans** — sub-project C/D. Implements the
  `ApiBackend` stub in `config.py` later.
- **Push notifications / reminders** — sub-project C.
- **`POST /plan`** — vacation planner endpoint is sub-project D.
- **Employer/B2B endpoints, company accounts, leave-request integrations**
  (BambooHR, Workday) — v2+. Noted here so the API surface stays simple
  and we don't accidentally bake B2C assumptions into the data model.
- **Subdivision support** (`subdiv=CA`, `subdiv=TN`, etc.). The `holidays`
  library supports subdivisions for many countries (US, IN, DE, AU, CA, BR);
  threading `subdiv` through the API is a small future addition but adds
  surface area to v1 we don't need. Future spec.
- **Generic config-driven news scraper** for countries beyond KR/NP
  (PH, ID, VN, IN, ...). Designed as a separate spec (sub-project
  "news-scaling"). v1 ships with the existing hand-tuned KR + NP scrapers
  only.
- **LLM-based news extraction** — explored as an option for the
  news-scaling spec, not in v1.
- **Official-source per-country ingestion** (`data.go.kr`-style for other
  governments) — per-country snowflakes; future, per-source spec.
- **Rate limiting / API keys** — defer to PaaS-level rules (Fly.io / Render
  built-ins) for v1.
- **DB writes from API requests** — the API reads only. The existing CLI
  populates `holidays.db` (gov-API + news scrapes) on its own cadence.
- **Mobile app implementation** — separate repo, separate spec.

## Coverage matrix

| Capability | v1? | Source |
|---|---|---|
| ~150 countries' national holidays | ✅ | `library_source` (offline `holidays` lib) |
| News-detected holidays (KR + NP) | ✅ | existing `news_kr`, `news_np` |
| Workweek policy lookup | ✅ (read-only) | existing `storage.resolve_workweek` |
| Sandwich-day detection | ✅ | existing `sandwich.py` |
| Subdivisions (US states, IN states, DE Länder, ...) | ❌ | future spec |
| News for PH, ID, VN, IN, BR, etc. | ❌ | future "news-scaling" spec |
| Per-user accounts / saved settings | ❌ | sub-project C |
| Vacation planner endpoint | ❌ | sub-project D |

## Endpoint surface

All endpoints under the `/v1/` prefix. All `GET`, all public, all return
`application/json`. CORS allow-origin `*` (v1 is a read-only public API).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/healthz` | Liveness probe — returns `{"status": "ok"}` |
| `GET` | `/v1/countries` | List supported ISO codes and which have news enrichment |
| `GET` | `/v1/holidays` | Holidays for a country/year |
| `GET` | `/v1/compare` | Side-by-side comparison of N countries |
| `GET` | `/v1/sandwiches` | Sandwich-day opportunities for a country |

### `GET /v1/healthz`

No parameters. Returns:

```json
{ "status": "ok", "version": "1.0.0" }
```

### `GET /v1/countries`

No parameters. Returns the list of countries the API can serve, with a
flag indicating which have news enrichment beyond the library baseline.

```json
{
  "count": 156,
  "countries": [
    { "code": "KR", "name": "South Korea", "news_enriched": true },
    { "code": "NP", "name": "Nepal", "news_enriched": true },
    { "code": "PH", "name": "Philippines", "news_enriched": false },
    { "code": "JP", "name": "Japan", "news_enriched": false }
  ]
}
```

Sources: the `holidays` library's enumeration of supported countries +
the keys registered in `news_source` for the `news_enriched` flag (the
implementation should expose a public helper rather than reach into a
private attribute — add `news_source.supported_countries() -> set[str]`
during implementation).

Country names: there's no name-from-code function in the `holidays`
package itself. v1 uses a small static mapping in `api/services.py`
covering the codes we actively support (KR, NP, JP, US, IN, PH, etc.);
for codes not in the map, `name` falls back to the ISO-2 code itself.
Adding `pycountry` as a dep is a tempting upgrade but is deferred — it
adds ~3 MB and we don't need 249 country names for v1.

### `GET /v1/holidays?country=NP&year=2026&from_today=false&only_red=true`

| Query param | Type | Default | Notes |
|---|---|---|---|
| `country` | string (ISO-2) | required | 400 if missing or unsupported by `holidays` lib |
| `year` | int | current year | 400 if outside `[1900, 2100]` |
| `from_today` | bool | `false` | If `true`, drop dates before today |
| `only_red` | bool | `false` | If `true`, exclude `source="news"` rows with confidence flagged as unconfirmed (matches CLI `--only-red`) |

Response:

```json
{
  "country": "NP",
  "year": 2026,
  "count": 32,
  "holidays": [
    { "date": "2026-01-15", "name": "Maghe Sankranti", "source": "library" },
    { "date": "2026-10-12", "name": "Dashain", "source": "library" }
  ]
}
```

Service-layer behavior: union `library_source.fetch(year, country)` with
`news_source.fetch(year, country)` (returns `[]` for unsupported news
countries). Dedupe on `(date, name)`.

### `GET /v1/compare?countries=KR,NP&year=2026`

| Query param | Type | Default | Notes |
|---|---|---|---|
| `countries` | comma-separated ISO-2 list | required | 400 if < 2 countries or any unsupported |
| `year` | int | current year | same bounds as `/v1/holidays` |

Response — semantics: `shared` is the intersection (same date across all
countries; name comes from the first country in the list). `only[CC]` is
dates in country CC but in **no** other listed country.

```json
{
  "year": 2026,
  "countries": ["KR", "NP"],
  "shared": [
    { "date": "2026-12-25", "name": "Christmas Day" }
  ],
  "only": {
    "KR": [
      { "date": "2026-09-25", "name": "Chuseok" }
    ],
    "NP": [
      { "date": "2026-10-12", "name": "Dashain" }
    ]
  }
}
```

For N > 2 countries, `shared` is the strict N-way intersection, and
`only[CC]` is dates unique to CC. There is no `partial[CC1,CC2]` listing
for v1 (could add `pairs` in a future version if useful for the UI).

### `GET /v1/sandwiches?country=KR&year=2026&workweek=sat,sun&from_today=false`

| Query param | Type | Default | Notes |
|---|---|---|---|
| `country` | string (ISO-2) | required | 400 if missing or unsupported |
| `year` | int | current year | same bounds |
| `workweek` | comma-list of `mon..sun` | resolved per cascade below | days OFF |
| `from_today` | bool | `false` | drop sandwiches whose break starts before today |

Workweek resolution cascade (no `--save`-style persistence; API is
stateless):

1. Explicit `workweek` query param, if given.
2. Most recent policy in `storage.resolve_workweek(country, today)`.
3. `planner.WORKWEEK_FALLBACKS[country]` if present.
4. **400** `{"detail": "No workweek on record for <CC>. Pass ?workweek=sat,sun."}`

Response:

```json
{
  "country": "KR",
  "year": 2026,
  "workweek": ["sat", "sun"],
  "workweek_source": "saved-policy:2026-04-18:medium",
  "count": 14,
  "sandwiches": [
    {
      "pto_date": "2026-09-28",
      "weekday": "Mon",
      "break_start": "2026-09-25",
      "break_end": "2026-09-29",
      "break_length": 5,
      "pto_cost": 1,
      "context": "Chuseok long weekend"
    }
  ]
}
```

`context` is a short human-readable label naming the adjacent holiday(s)
the sandwich is anchored on — derived from the red days inside
`[break_start, break_end]`. Empty string if no anchor (rare for a true
sandwich).

## Error model

All errors return JSON with HTTP status:

```json
{ "detail": "country 'ZZ' not supported by holidays library" }
```

| Status | When |
|---|---|
| `400` | Missing required param, unsupported country, malformed `workweek`, year out of range, fewer than 2 countries in `/v1/compare` |
| `500` | Anything else (logged, generic message returned) |

No `404` — missing data for a valid country returns `200` with an empty
list, not a 404. This matches REST conventions and is friendlier to mobile
clients.

## Architecture and file structure

```
api/
├── __init__.py
├── main.py           # FastAPI app, route definitions, CORS, exception handlers
├── schemas.py        # Pydantic request/response models
├── services.py       # thin adapters over library_source, news_source,
│                     #   sandwich, storage — no business logic of its own
└── Dockerfile

tests/api/
├── __init__.py
└── test_endpoints.py # FastAPI TestClient-based tests

requirements.txt      # adds: fastapi, uvicorn[standard], httpx (dev)
README.md             # adds an "API" section with curl examples
fly.toml              # OR render.yaml — picked at deploy time
```

Key principle: **`api/services.py` contains no holiday logic of its own.**
It calls into the existing modules (`sources.library_source`,
`sources.news_source`, `sandwich`, `storage`, `planner`). Anything an
endpoint needs that doesn't exist in those modules must be added there
first, not in `services.py`.

This keeps the CLI and the API serving the same code paths, so they can't
diverge.

## Testing strategy

`pytest` with FastAPI's `TestClient` (uses `httpx` internally). Per
endpoint:

| Endpoint | Tests |
|---|---|
| `/v1/healthz` | 200 + body shape |
| `/v1/countries` | 200, non-empty, KR and NP flagged `news_enriched=true`, PH/JP flagged `false` |
| `/v1/holidays` | (a) known year/country returns expected count, (b) `from_today=true` filters, (c) unsupported country → 400, (d) bad year → 400, (e) missing country → 400 |
| `/v1/compare` | (a) KR/NP 2026 includes `2026-12-25 Christmas` in `shared`, Chuseok in `only.KR`, Dashain in `only.NP`, (b) one country → 400, (c) unsupported member → 400 |
| `/v1/sandwiches` | (a) KR 2026 sat,sun returns at least one sandwich around Chuseok, (b) missing workweek with no policy on record → 400, (c) unsupported country → 400 |

Existing 111 tests stay untouched. New `tests/api/` adds ~12 tests.

## Deployment

- Dockerfile from `python:3.11-slim`, single `uvicorn api.main:app --host 0.0.0.0 --port 8080` entrypoint.
- `fly.toml` (or `render.yaml`) committed with sensible defaults (1 shared-cpu instance, auto-stop when idle).
- `holidays.db` is **NOT** baked into the image. v1 deploys with an empty
  `holidays.db` that lives on the container's local disk; news-sourced
  data will rebuild on first request through the existing scrape path
  *(out of scope for this spec — the API does not trigger scrapes; the
  data path is read-only)*. For v1 this means new news rows accumulate
  only if/when the CLI is run inside the container, which is fine because
  KR/NP news content is informational icing on a library baseline that
  works for all 150 countries.
- A `Makefile` target or a one-line shell script for deploys: `fly deploy`.
- No CI in v1.

## Open questions resolved during brainstorming

- **Q: API + CLI or just CLI?** → API (FastAPI).
- **Q: Auth in v1?** → No. Skip until C.
- **Q: Subdivisions in v1?** → No.
- **Q: Scale news scrapers in v1?** → No, KR + NP only.
- **Q: B2B/employer mode?** → v2+. Manager view of same data is the
  starting point. Future direction: HR/leave-request integration
  (BambooHR, Workday) to flag sandwich-likely leave requests.
- **Q: Rate limiting?** → PaaS-level only for v1.
- **Q: Where does the mobile app live?** → Separate repo
  (`daysoff-mobile`), separate spec.
- **Q: Hosting?** → Fly.io / Render / Railway — final pick at deploy time;
  spec is hosting-agnostic.

## Done criteria

- `api/` directory present with the four files described.
- `python3 -m uvicorn api.main:app` starts the server locally on port 8080.
- All 5 endpoints respond correctly per the response shapes above.
- ~12 new tests in `tests/api/` pass alongside the existing 111.
- Dockerfile builds; `docker run -p 8080:8080 daysoff-api` serves traffic.
- README updated with an "API" section listing endpoints + curl examples.
- A platform-specific deploy config file committed (`fly.toml` or
  `render.yaml`).
