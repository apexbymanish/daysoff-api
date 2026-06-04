# daysoff Mobile App — Front-End Design Spec (Flutter)

**Date:** 2026-06-04
**Status:** Draft for review
**Author:** Manish Adhikari

## Goal

Build the daysoff mobile app — a Flutter front-end consuming the existing
public `/v1` FastAPI backend — realizing the screens designed in Stitch
(`docs/superpowers/specs/2026-05-29-stitch-full-flow-design.md`). The app
follows **Uncle Bob's Clean Architecture** with a **reusable, component-based
design system**, using **GetX** for the presentation layer only.

## Decisions (from brainstorming)

| Decision | Choice |
|----------|--------|
| **Framework** | Flutter (Dart), iOS + Android from one codebase |
| **State / DI / routing** | GetX — **presentation layer only** (controllers, `Bindings`, `Get.to`, `Get.bottomSheet`, `Get.dialog`) |
| **Architecture** | Clean Architecture, dependency rule points inward; domain + data layers are pure Dart (no GetX/Flutter/HTTP) |
| **Code organization** | Feature-first: `core/` + `design_system/` + `features/<f>/{domain,data,presentation}` |
| **Reusable UI** | A `design_system/` layer: design tokens + shared widgets (Button, BottomSheet, Modal, cards, pills, day-ribbon, tab bar, scaffolds) |
| **Scope** | Full spec, built in **phases** (foundation → vertical slices → integrations) |
| **Backend** | Existing public API `https://daysoff-api.fly.dev` (configurable); routes `/v1/{countries,holidays,plan,sandwiches,compare,healthz}` |

## Project location

Create the Flutter project at **`app/`** inside this repo for now (the README
earmarks a future standalone `daysoff-web` repo; we can extract `app/` into its
own repo later without code changes). The Python backend is untouched.

## Layering (Clean Architecture)

```
Presentation (GetX)        Domain (pure Dart)           Data
─────────────────────      ────────────────────         ─────────────────────
Page (StatelessWidget)  →  UseCase (callable class)  →  Repository (interface)
GetxController (state)     Entity (immutable)            ↑ implemented by
Binding (DI/composition)   RepositoryInterface           RepositoryImpl
                           Failure (sealed)              ├─ RemoteDataSource (Dio → /v1)
                                                         │   DTO ↔ Entity mappers
                                                         └─ LocalDataSource (prefs/SQLite)
```

**Dependency rule:** Presentation → Domain ← Data. Domain depends on nothing.
Controllers call **use cases only**; they never touch data sources or Dio.
Each feature's `Binding` is the composition root that wires
`RemoteDataSource → RepositoryImpl → UseCase → Controller` via `Get.lazyPut`.

**Error handling:** use cases return `Either<Failure, T>` (fpdart). Data sources
throw typed exceptions; `RepositoryImpl` maps them to `Failure`
(`NetworkFailure`, `ServerFailure`, `CacheFailure`, `PermissionFailure`).
Controllers translate `Failure` → UI state (error banner, empty-as-CTA, retry).

## Tech / packages

- **get** — state, DI, routing, snackbars/sheets/dialogs (presentation only)
- **dio** — HTTP client (+ interceptors: base URL, logging, error mapping)
- **freezed** + **json_serializable** — immutable entities/DTOs + JSON
- **fpdart** — `Either`/`Option` for functional error handling in domain
- **get_storage** (light prefs) and/or **sqflite** (blocked dates, saved breaks)
- **device_calendar** — read events + write breaks (EventKit/Android equiv)
- **flutter_local_notifications** — local reminders (the "nudge me" feature)
- **google_fonts** — Manrope (+ JetBrains Mono for numeric/label text)
- Dev/test: **mocktail**, **bloc_test**-style controller tests via GetX, flutter_test

Config via `--dart-define=API_BASE_URL=…` (default `https://daysoff-api.fly.dev`,
local dev `http://localhost:8000`).

## Design system (`design_system/`)

The reusable component library — built first, used everywhere.

- **Tokens** — `AppColors` (Serene Efficiency: teal `#1a4d4e`, sage `#8E9775`,
  sand `#E9C46A`, korea-red/blue, neutrals), `AppTypography` (Manrope scale +
  JetBrains Mono label), `AppSpacing` (4px grid), `AppRadii`. Exposed through a
  single `AppTheme` (light + dark `ThemeData`).
- **Widgets** (stateless, theme-driven, no business logic):
  `DaysOffButton` (primary/secondary/disabled), `DaysOffTextField`,
  `DaysOffBottomSheet` (base for all sheets, shown via `Get.bottomSheet`),
  `DaysOffModal`/`ConfirmDialog` (via `Get.dialog`), `HolidayCard`
  (free/absorbed/multi-day variants), `BreakCard` (+ `DayRibbon` sparkline +
  `BestValueBadge`), `PtoCostPill`, `StatusBadge`, `BudgetSlider`,
  `ReminderRow`, `SandwichCard`, `UpsellBanner`, `UndoToast`, `AppTabBar`
  (3 tabs), `SegmentedToggle`, `AppScaffold`, and `EmptyState`/`LoadingSkeleton`/
  `ErrorView` blocks. Every status uses icon **and** label (accessibility:
  never color alone), matching the spec's redundant-encoding rule.

## Features (each = domain + data + presentation)

- **holidays** — `GetHolidays(country, year)`; Home timeline, calendar view,
  holiday detail sheet; loading/empty/error states. Feeds `/v1/holidays`.
- **plan** — `GetPlan(country, year, budget, workweek, min/max)` and
  `GetSandwiches(...)`; length buffet, break detail, sandwich section,
  workweek override. Feeds `/v1/plan`, `/v1/sandwiches`.
- **entry/auth** — welcome, country pick (value-first, no account), guest
  mode, contextual sign up / log in / forgot password. `AuthRepository`
  interface with a **local stub** implementation (backend is currently public,
  no tokens) — a real token-based impl drops in later behind the same interface.
- **block_date** — `BlockDate` / `UnblockDate` / `GetBlockedDates` (local
  persistence); tap-a-date sheet, busy markers on Home, planner skips blocked
  dates, listed in Saved & Reminders. Works for guests.
- **calendar** — `ConnectCalendar`, `GetCalendars`, `ReadEvents`,
  `WriteBreakEvents`; permission prime, denied state, calendar picker,
  conflict warning. Wraps `device_calendar`. Deferred + optional.
- **reminders** — `SetReminder`, `GetReminders`, `CancelReminder`; reminder-set
  confirmation, lead-time edit, Saved & Reminders list. Wraps
  `flutter_local_notifications` (local only — not push).
- **save** — `SaveBreak` (preview → write to calendar + set reminder, with
  undo); composes calendar + reminders.
- **settings** — preferences, editors, profile, confirm dialog, theme/locale.
- Cross-cutting: **dark mode** via `AppTheme.dark`; **localization** scaffold
  for EN + local scripts (ko/ne/ja) labels.

## Sample / illustrative data

Use **South Korea, 2026** consistently (Seollal, Children's Day, Chuseok) to
match the Stitch pack, but data is **live from the API** — no hardcoded
holidays in the app (only fixtures in tests).

## Testing strategy

- **Domain:** unit-test every use case (pure, trivial to test).
- **Data:** test mappers (DTO↔entity) and `RepositoryImpl` failure mapping with
  a mocked data source (mocktail).
- **Presentation:** controller tests (state transitions for load/empty/error);
  widget tests for each design-system component (renders all variants/states).
- **Smoke:** one integration test walking the core loop against a mock client.
- TDD per the team workflow: failing test → implement → pass → commit.

## Build phases (ordered)

1. **Foundation** — scaffold `app/`, add deps, `AppTheme` (tokens, light+dark),
   `core/` (Dio client, Failure, env, GetX router, base Binding), and the
   `design_system/` base widgets (Button, TextField, BottomSheet, Modal, Card,
   Pill, Scaffold, TabBar, state blocks) with widget tests. One throwaway demo
   screen to prove theming.
2. **Holidays vertical slice** — full domain/data/presentation against
   `/v1/holidays`: Home timeline + calendar view + holiday detail sheet +
   states. Proves the entire stack end-to-end.
3. **Plan** — length buffet + break detail + sandwich section + workweek
   override against `/v1/plan` + `/v1/sandwiches`.
4. **Entry & Auth** — welcome, country pick, guest mode, contextual auth (stub).
5. **Block-a-date** — local persistence + planner integration + Saved list.
6. **Calendar + Reminders + Save** — device_calendar, local notifications,
   save-break preview/write/undo, conflict warning.
7. **Settings, Profile, remaining states, dark-mode polish, localization.**

Each phase is independently shippable/testable and gets its own implementation
plan when we reach it.

## Out of scope (v1)

Real backend auth tokens (interface-ready, stubbed), push notifications
(local reminders only), country-comparison (`/v1/compare`) UI, social/sharing,
team views, in-app purchases.

## Success criteria

- Flutter app in `app/` runs on iOS + Android against the live API.
- Clean Architecture boundaries enforced (domain pure; GetX only in presentation;
  controllers depend on use cases).
- Reusable `design_system/` is the single source of UI truth (no ad-hoc colors
  or one-off buttons in feature code).
- Phase 2 (holidays slice) demonstrably works end-to-end with passing tests
  before later phases begin.

## Open questions

None blocking. Project location (`app/` here vs. standalone `daysoff-web` repo)
is the one easily-reversible call — defaulting to `app/`.
