# daysoff-api

Backend / API project for **daysoff** — a multi-source holiday aggregator and vacation planner. Given a country and a number of leave days (PTO/연차/बिदा), it finds the optimal combinations of days to take off to maximize consecutive break time.

> **Repo scope:** this is the backend (data sources, domain logic, persistence, CLI). A separate `daysoff-web` repo will hold the frontend once the API stabilizes. The original "Sandwich Days" feature is now one capability inside the broader product.

## What it does

- **Aggregates holidays** from three sources: the offline `holidays` Python library, Korea's official `data.go.kr` API, and Google News (for newly-announced temporary holidays).
- **Detects sandwich days** — workdays wedged between off-days that, if taken off, yield long breaks.
- **Plans vacations** — given a PTO budget, suggests the longest single trip AND the best portfolio of non-overlapping trips (DP knapsack on intervals).
- **Resolves workweeks automatically** by scraping policy-change news (e.g., Nepal moved from 1-day to 2-day weekend on 2026-04-05).
- **Tracks newly-announced holidays between runs** via SQLite — flags new red days the moment a source first sees them.
- **Saves user preferences** — set your country/budget/workweek once with `--save`, then run with zero flags. Custom workweeks supported (any combination: `sat,sun`, `wed,thu`, `sun,thu`, etc.).
- **Auto-refreshes stale policy data** when cached news is >30 days old, so you don't have to remember `--refresh-policies`.

## Project structure

```
daysoff-api/
├── main.py                    # holiday aggregator + sandwich detection (CLI)
├── planner.py                 # vacation optimizer (CLI)
├── sandwich.py                # sandwich-day algorithm (pure)
├── storage.py                 # SQLite — holidays + workweek policies
├── config.py                  # user preferences (forward-compatible backend)
├── requirements.txt
├── .gitignore
├── tests/                     # unittest suite (103 tests)
└── sources/
    ├── library_source.py      # offline `holidays` package (150+ countries)
    ├── gov_api_source.py      # Korea data.go.kr API (needs API key)
    ├── news_source.py         # country-dispatching news scraper
    ├── news_kr.py             # Korean Google News (임시공휴일)
    ├── news_np.py             # Nepali Google News (publish-date anchored)
    ├── _news_utils.py         # shared year-anchoring helpers
    ├── festivals_source.py    # Korean cultural festivals (non-red-day)
    └── policy_scraper.py      # workweek-policy detector (multi-country)

~/.daysoff/
└── config.json                # user preferences (chmod 600)
```

### Migration from holidaySandwicher

The repo was renamed from `holidaySandwicher` → `daysoff-api`. If you had the old config:

- Config dir moved from `~/.holidaySandwicher/` → `~/.daysoff/` — migration runs automatically on first launch.
- Environment variable renamed `HOLIDAY_BACKEND` → `DAYSOFF_BACKEND` (old name still accepted for one release).
- After verifying the new config works, you can `rm -rf ~/.holidaySandwicher` to clean up.

## Setup

```bash
cd daysoff-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: get a free API key from https://data.go.kr for the
# Korean special-day API. Skip if you only need the offline library + news.
export DATA_GO_KR_KEY="your_key_here"
```

## Commands

### `main.py` — Holiday aggregator

```bash
# All holidays in a year (library + news + gov_api)
python3 main.py --year 2026 --country KR

# Only future holidays
python3 main.py --year 2026 --country KR --upcoming

# Only confirmed red days (excludes unconfirmed news speculation)
python3 main.py --year 2026 --country KR --upcoming --only-red

# Different country
python3 main.py --year 2026 --country NP --upcoming
```

| Flag | Purpose |
|---|---|
| `--year YYYY` | Defaults to current year |
| `--country CC` | ISO 2-letter code (KR, JP, NP, US, IN, ...) |
| `--upcoming` | Only dates from today onward |
| `--only-red` | Exclude unconfirmed news-only dates |

### `planner.py` — Vacation optimizer

**Quick start — save your settings once, run with zero flags forever:**

```bash
# One-time setup
python3 planner.py --budget 15 --country KR --workweek wed,thu --save

# Then just:
python3 planner.py
```

**Full command examples:**

```bash
# Basic: best plan for 15 PTO days
python3 planner.py --budget 15 --year 2026 --country KR

# Future-only + restrict trip lengths
python3 planner.py --budget 15 --country KR --from-today --min-length 4 --max-length 10

# Only the longest single trip
python3 planner.py --budget 15 --country KR --strategy longest

# Only the portfolio (multiple non-overlapping trips)
python3 planner.py --budget 15 --country KR --strategy portfolio

# Different country (auto-refreshes workweek policies if needed)
python3 planner.py --budget 15 --country NP

# Override workweek manually — any combination works
python3 planner.py --budget 15 --workweek sat,sun
python3 planner.py --budget 15 --workweek wed,thu
python3 planner.py --budget 15 --workweek sun,thu

# Force a fresh policy scrape
python3 planner.py --budget 15 --country NP --refresh-policies

# Skip auto-refresh (use cached data only)
python3 planner.py --budget 15 --country NP --no-auto-refresh
```

| Flag | Default | Purpose |
|---|---|---|
| `--budget N` | from config | PTO/연차/बिदा days available |
| `--year YYYY` | current year | Year to plan for |
| `--country CC` | from config or `KR` | ISO 2-letter code |
| `--workweek` | config → news → fallback | Comma list of OFF days, e.g. `sat,sun`, `wed,thu`, `sun,thu` |
| `--save` | off | Persist `--budget`, `--country`, `--workweek` to config |
| `--strategy` | both | `longest` \| `portfolio` \| `both` |
| `--from-today` | off | Skip past dates |
| `--min-length N` | 1 | Reject trips shorter than N days |
| `--max-length N` | 31 | Reject trips longer than N days |
| `--top N` | 3 | Alternative single-break options to list |
| `--refresh-policies` | off | Force re-scrape of workweek policy news |
| `--no-auto-refresh` | off | Disable automatic refresh of stale policies |
| `--show-festivals-near N` | 7 | Festivals within ±N days of each trip |

## Day classification (planner output)

Every day in a trip is tagged:

| Tag | Meaning |
|---|---|
| 🏢 **OFFICE HOLIDAY** (공휴일 / सार्वजनिक बिदा / 祝日) | Red day, office closed, no PTO needed |
| 🏖️ **PTO** (연차 / बिदा / 有給休暇) | Your annual leave |
| 🟦 **WEEKEND** | Naturally off |
| 🎎 **FESTIVAL** (기념일 / पर्व / 記念日) | Cultural event, office stays open |
| 💼 **WORKDAY** | Regular workday |

## Workweek auto-detection

The planner resolves the country's workweek through a fallback cascade:

```
1. --workweek flag (user override this run)
2. Saved preference for this country in ~/.daysoff/config.json
3. Most recent policy in SQLite for that country (from news scraping)
4. Hardcoded fallback (WORKWEEK_FALLBACKS in planner.py)
5. Exit with "no policy on record" warning
```

Each plan's header shows where the value came from:

```
Weekend: Wed, Thu [source: user-flag]                         ← --workweek this run
Weekend: Sat, Sun [source: saved preference]                  ← from config.json
Weekend: Sat, Sun [source: news (2026-04-18, conf=medium)]    ← news-backed
Weekend: Sat, Sun [source: hardcoded fallback]                ← stale risk
```

The policy scraper currently covers: **KR, JP, NP, SA, AE, BD, IL**.

## User preferences (config.py)

Settings live in `~/.daysoff/config.json` (chmod 600). Sample:

```json
{
  "default": {
    "country": "KR",
    "budget": 15,
    "workweeks": {
      "KR": "wed,thu",
      "NP": "sat,sun"
    }
  }
}
```

**Custom workweek values:** any subset of `mon,tue,wed,thu,fri,sat,sun`. Examples:

- `sat,sun` — standard 5-day workweek
- `sat` — 6-day workweek with Saturday off only
- `fri,sat` — Middle East / Israel style
- `wed,thu` — split rest days mid-week
- `sun,thu` — non-contiguous; any combination is valid

**Backend abstraction:** `config.py` exposes `get(key, user_id)` / `save(updates, user_id)`. Today the backend is JSON (`DAYSOFF_BACKEND=json`). Future stages can swap to SQLite multi-user (`DAYSOFF_BACKEND=sqlite`) or a REST API (`DAYSOFF_BACKEND=api`) without changing callers.

## Auto-refresh of stale policies

Workweek policy news is refreshed automatically when:

- No policies are cached for the country, OR
- The most recent cached policy is more than **30 days** old

You can override:

```bash
python3 planner.py --refresh-policies   # force refresh
python3 planner.py --no-auto-refresh    # never refresh automatically
```

## Inspecting the database

```bash
# Cached workweek policies
sqlite3 holidays.db "SELECT country, effective_date, weekend_spec, confidence, substr(headline, 1, 70) FROM workweek_policies ORDER BY effective_date DESC;"

# Cached holidays (when each was first seen)
sqlite3 holidays.db "SELECT date, country, name, source, first_seen FROM holidays ORDER BY first_seen DESC LIMIT 20;"

# Drop the DB to start fresh
rm holidays.db
```

## Updating

The `holidays` package is rule-based and ships new releases roughly monthly. Refresh before doing major planning:

```bash
pip install -U holidays
```

For workweek/policy changes, re-scrape news:

```bash
python3 planner.py --budget 15 --country NP --refresh-policies
```

## Most useful combos

```bash
# "Save my office setup once"
python3 planner.py --budget 15 --country KR --workweek wed,thu --save

# "Best Chuseok engineering?"
python3 planner.py --budget 5 --country KR --from-today --strategy longest --max-length 10

# "Balanced year of 4–5 day trips"
python3 planner.py --budget 15 --country KR --from-today --min-length 4 --max-length 5

# "Dashain plan for Nepal"
python3 planner.py --budget 7 --country NP --from-today --strategy longest

# "Just the dates"
python3 main.py --year 2026 --country KR --upcoming --only-red
```

## HTTP API

`api/` exposes the same data over a stateless FastAPI service. Run locally:

```bash
python3 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8080
```

Endpoints (all GET, all public, all under `/v1/`):

| Path | Example |
|---|---|
| `/v1/healthz` | `curl localhost:8080/v1/healthz` |
| `/v1/countries` | `curl localhost:8080/v1/countries` |
| `/v1/holidays` | `curl 'localhost:8080/v1/holidays?country=KR&year=2026'` |
| `/v1/compare` | `curl 'localhost:8080/v1/compare?countries=KR,NP&year=2026'` |
| `/v1/sandwiches` | `curl 'localhost:8080/v1/sandwiches?country=KR&year=2026&workweek=sat,sun'` |

Spec: [`docs/superpowers/specs/2026-05-22-read-api-design.md`](docs/superpowers/specs/2026-05-22-read-api-design.md).

OpenAPI docs auto-generated at `/docs` when the server is running.

Deploy via the included `api/Dockerfile`. A starter `fly.toml` ships in the
repo; Render and Railway can use the Dockerfile directly with no extra config.

The image ships with an empty `holidays.db` — news/policy rows accumulate
only when the CLI commands (`main.py`, `planner.py --refresh-policies`)
run inside the container. The library-sourced holidays (~250 countries)
need no DB at all and are available immediately.

## Caveats

- **News scraping is heuristic.** False positives (Indian-state news leaking into Nepal queries) and misses (policy-style news without explicit dates) are possible. Always verify high-stakes plans against an official source.
- **Lunar holidays** are computed offline by the `holidays` library — date accuracy depends on the library's lunar conversion staying current. Some Korean and Nepali festivals shift by 1 day depending on which lunar table is used.
- **Some holiday names appear in English** even for non-English countries (e.g., "Chuseok" instead of "추석") because that's how the `holidays` library labels them. Cosmetic only.
- **Korean `gov_api_source`** requires a free API key from data.go.kr. Without it, the script still works using library + news.
- **Festivals source is Korea-only** so far. Nepal/Japan festival data would need similar hardcoding or a separate source.
- **Config file is single-user today.** The `config.py` interface accepts `user_id` (defaults to `"default"`), so multi-user / API backends can be added without changes to callers.
