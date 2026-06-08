# daysoff Accounts & Saved-Breaks Sync — Design (Phase 1)

Recorded 2026-06-08.

## Goal

Add user accounts to daysoff and sync **saved breaks** across devices, backed
by **our own SQLite database**. Make the Profile screen (6.5) real. The
holiday / plan / sandwich endpoints stay **public**.

This spec covers **Phase 1 only: email + password**, built and tested
**locally** (no Fly deploy yet). Google & Apple sign-in (Phase 2) and
preference sync are explicitly out of scope but the design leaves clean seams
for them.

## Decisions (locked)

- **Scope:** accounts + **saved-breaks sync only**. Preferences (budget, break
  length, days off, country/year, theme) stay device-local.
- **Auth (Phase 1):** our own **email + password** — bcrypt hashes, JWT access
  token + rotating refresh token, all in our DB.
- **Database:** built to scale to **millions of users**. **PostgreSQL in
  production** via **async SQLAlchemy 2.0** (`asyncpg`) + Alembic; **SQLite
  (`aiosqlite`) for local dev and tests** so we can build now with zero setup.
  The two are swappable via a single `DATABASE_URL`; the Phase-1 schema uses
  only portable column types (no Postgres-only features), so dev/prod parity
  holds.
- **Local-first:** develop against `127.0.0.1:8080` on a local SQLite file;
  provision managed Postgres + secrets + deploy in a later pass.

### Scaling architecture (how it reaches millions of users)

- **Stateless API:** auth is JWT-based, so the FastAPI app holds no per-user
  session state and scales **horizontally** — add machines behind a load
  balancer, all sharing one Postgres.
- **Async I/O:** async SQLAlchemy + `asyncpg` keeps request handlers
  non-blocking under high concurrency.
- **Connection pooling:** a bounded engine pool per machine, fronted by a
  managed pooler (pgbouncer / Neon / Supabase pooler) in prod so thousands of
  app connections collapse onto a small Postgres connection budget.
- **Indexes:** `users.email` (unique), `saved_breaks.user_id`,
  `refresh_tokens.token_hash`, `oauth_identities (provider, provider_sub)` —
  every hot lookup is indexed; UUID primary keys avoid hot-spotting.
- **Read-replica / partition headroom:** read-heavy endpoints can later be
  routed to replicas; `saved_breaks` is already keyed by `user_id` for clean
  sharding/partitioning if ever needed. No Phase-1 work, just no design
  dead-ends.

## Out of scope (Phase 1)

- Google / Apple OAuth (Phase 2 — backend ID-token verification + native
  buttons; the `oauth_identities` table is created now so Phase 2 only adds
  endpoints, not migrations).
- Preference sync (prefs stay local).
- Email verification, password-reset email (note as future; not blocking).
- Fly deployment (local-first).

---

## Backend (`daysoff-api`)

### Dependencies (add to `requirements.txt`)

- `sqlalchemy[asyncio]>=2.0`
- `alembic>=1.13`
- `asyncpg>=0.29` (Postgres driver, prod)
- `aiosqlite>=0.19` (SQLite async driver, local/test)
- `bcrypt>=4.1`
- `pyjwt>=2.8`
- `pydantic-settings>=2.0`

### Config — `api/settings.py` (pydantic-settings)

- `DATABASE_URL` — default dev `sqlite+aiosqlite:///./daysoff.db`; prod
  `postgresql+asyncpg://…`.
- `DAYSOFF_JWT_SECRET` — required, HS256 signing key.
- `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` (defaults sane for Postgres; ignored by
  SQLite).
- `ACCESS_TTL_MIN = 30`, `REFRESH_TTL_DAYS = 30`.

This is a **separate** database from the holidays cache (`storage.py`'s
`holidays.db`), which is unchanged.

### DB layer — `api/db.py`

- **Async** SQLAlchemy 2.0: `create_async_engine(DATABASE_URL, …)` +
  `async_sessionmaker`. Pool size/overflow applied for Postgres; SQLite gets
  `check_same_thread=False`. FastAPI dependency `get_db()` yields an
  `AsyncSession`.
- `Base = DeclarativeBase`.
- Alembic initialised under `alembic/` (async `env.py` bound to
  `Base.metadata`); one initial migration creates all Phase-1 tables. Portable
  column types only so the same migration runs on SQLite and Postgres.

### Models — `api/models_db.py`

- **User**: `id` (str UUID pk), `email` (unique, indexed, stored lowercased),
  `password_hash` (str, nullable — null for future OAuth-only users),
  `display_name` (str, nullable), `created_at` (UTC datetime).
- **OAuthIdentity** (created now, used in Phase 2): `id` (pk), `user_id` (fk),
  `provider` (`'google'|'apple'`), `provider_sub` (str), unique
  `(provider, provider_sub)`.
- **SavedBreakRow**: composite pk `(user_id, id)` — `id` is the client-supplied
  id (e.g. `sandwich-2026-…`), which is only unique per user. Columns: `label`
  (str), `start` (date), `end` (date), `pto_cost` (int), `kind` (str),
  `updated_at` (UTC datetime), `deleted_at` (UTC datetime, nullable tombstone).
- **RefreshToken**: `id` (pk), `user_id` (fk), `token_hash` (sha256 hex of the
  opaque token), `expires_at`, `created_at`, `revoked` (bool default false).

### Auth — `api/auth.py` + `api/routers/auth.py`

- `hash_password` / `verify_password` via `bcrypt`.
- **Access token**: JWT HS256, claims `{sub: user_id, exp, type: "access"}`,
  TTL 30 min.
- **Refresh token**: opaque random (`secrets.token_urlsafe(32)`); only its
  sha256 is stored (`RefreshToken.token_hash`) so it can be revoked/rotated.
  TTL 30 days.
- `get_current_user` FastAPI dependency: read `Authorization: Bearer <access>`,
  decode + validate (`type == "access"`, not expired), load `User` or 401.
- **Endpoints** (all under `/v1/auth` unless noted):
  - `POST /register` `{email, password, display_name?}` → 201
    `{access_token, refresh_token, token_type, expires_in, user}`. Password
    min length 8. 409 if email already exists.
  - `POST /login` `{email, password}` → 200 same shape. 401 on bad creds.
  - `POST /refresh` `{refresh_token}` → 200 `{access_token, refresh_token, …}`;
    **rotates** (revokes the presented refresh, issues a new one). 401 if
    unknown / expired / revoked.
  - `POST /logout` `{refresh_token}` → 204; marks that refresh token revoked.
  - `GET /v1/me` (auth) → `{id, email, display_name, created_at}`.
  - `DELETE /v1/me` (auth) → 204; deletes the user and cascades their saved
    breaks + refresh tokens.

### Saved-breaks sync — `api/routers/saved_breaks.py`

- DTO `SavedBreakDTO`: `{id, label, start, end, pto_cost, kind, updated_at,
  deleted_at?}`.
- `GET /v1/saved-breaks` (auth) → `{breaks: [non-deleted DTOs], server_time}`.
- `POST /v1/saved-breaks/sync` (auth) `{breaks: [DTO…]}` →
  **last-write-wins merge** scoped to the current user:
  - For each incoming row: if no stored row with that `(user_id, id)`, insert.
    Else if `incoming.updated_at >= stored.updated_at`, overwrite all fields
    (including `deleted_at`, so a tombstone with a newer timestamp deletes).
    Otherwise ignore (stored is newer).
  - Response: `{breaks: [all current non-deleted rows for the user],
    server_time}` so the client can replace its cache.
- LWW uses the **client-supplied `updated_at`** (device clock). Acceptable for
  low-conflict personal saved breaks; documented risk, revisited if needed.

### Backend tests — `tests/`

Use a throwaway SQLite file (tmp path) + dependency-override `get_db`; FastAPI
`TestClient`.

- Auth: register → login → `/v1/me` happy path; duplicate-email 409; short
  password rejected; wrong password 401; `/v1/me` without token 401; refresh
  rotates (old refresh then rejected); logout revokes.
- Sync: push new breaks then `GET` returns them; LWW (older incoming ignored,
  newer overwrites); tombstone (`deleted_at`) removes from `GET`; **user
  isolation** (user A never sees user B's breaks).
- `DELETE /v1/me` removes the user's breaks.

---

## Mobile (`daysoff-mobile`)

### Dependencies

- `flutter_secure_storage` — store access + refresh tokens (not `get_storage`).
- (Phase 2 only: `google_sign_in`, `sign_in_with_apple`.)

### Auth layer

- `ApiClient`: add `register`, `login`, `refresh`, `logout`, `me`,
  `deleteAccount`.
- `AuthRepository` + secure token store (read/write/clear access+refresh).
- **Dio interceptor**: attach `Authorization: Bearer <access>` to requests; on
  a 401, attempt one refresh and retry; on refresh failure, clear tokens →
  unauthenticated.
- `authStateProvider` (Notifier): `unauthenticated | authenticated(User)`;
  hydrates from secure storage on startup.
- **Login / Register screen** (go_router route), reachable from the Profile
  card.

### Profile (6.5)

- Make the stubbed Profile real, surfaced as a **card in the Settings tab**
  (keep the 3-tab IA — no 4th tab): when logged out, a "Sign in / Create
  account" card → auth screen; when logged in, show email/name, "Sync on",
  **Log out**, **Delete account**.

### Saved-breaks sync

- `savedBreaksProvider` stays **local-first** (`get_storage` cache) and keeps
  current behavior when logged out.
- `SavedBreak` model gains `updatedAt` + `deletedAt` (tombstone) so deletes can
  sync; locally a removed break becomes a tombstone until synced.
- When **authenticated**:
  - On login: push the local set via `/sync` (merge), then replace the local
    cache with the authoritative response.
  - On add/remove: update local + bump `updatedAt` / set `deletedAt`, then push
    `/sync`.
  - On app start (if authed): pull `GET /v1/saved-breaks` and reconcile.

### Mobile tests

- `AuthRepository` with a fake `ApiClient`: login stores tokens; 401 triggers a
  single refresh then retry; refresh failure logs out.
- Saved-breaks **LWW merge** unit test (mirror of the server rule).
- Profile card: logged-out shows sign-in; logged-in shows email + logout.

---

## Decomposition into implementation plans

Two plans (separate subsystems / repos), built in order:

1. **Plan A — backend** (`daysoff-api`): settings + DB + Alembic + models +
   auth + saved-breaks sync + tests. Establishes the API contract.
2. **Plan B — mobile** (`daysoff-mobile`): auth plumbing (secure storage, Dio
   interceptor, auth state) + login/register + Profile card + saved-breaks sync
   + tests. Depends on Plan A's contract.

## Assumptions / risks

- **Scale target:** Postgres in prod + stateless JWT API + pooling + indexes is
  the path to millions of users; SQLite is dev/test only. Risk: dev/prod DB
  drift — mitigated by using only portable column types in Phase 1 and running
  the migration against Postgres before deploy.
- `updated_at` from the device clock drives LWW — low-conflict for personal
  saved breaks; revisit if multi-device conflicts surface.
- No email verification / password reset in Phase 1 (future).
- Deploy (managed Postgres + pooler + `DAYSOFF_JWT_SECRET` secret) is a separate
  follow-up; until then the mobile app points at the local backend (SQLite).
- UUID primary keys stored as `String(36)` for SQLite/Postgres portability
  (can migrate to native `uuid`/`bigint` identity in a Postgres-only future).
