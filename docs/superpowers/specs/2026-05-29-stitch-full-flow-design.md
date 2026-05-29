# daysoff — Full Stitch Screen Flow (Design Spec)

**Date:** 2026-05-29
**Status:** Approved (brainstorming) — ready for implementation plan
**Author:** Manish Adhikari

## Goal

Produce the **complete app surface** for the daysoff mobile app in Google
Stitch — not just the happy-path screens, but every sub-screen, the critical
states, navigation, and a component catalog — as a clean, consistent design
handoff.

This expands on the existing prompt pack in `docs/stitch/` (master prompt + 9
screen prompts), which only covered the happy path and was written for manual
pasting. This spec covers the full flow and is generated via the **Stitch MCP**.

## Decisions (from brainstorming)

| Decision | Choice |
|----------|--------|
| **State depth** | Critical states (empty / error / key success) **+ loading/skeleton** for data-heavy screens. Not every-state-everywhere. |
| **Components** | App screens **+ a dedicated component catalog** (design-system reference boards). |
| **Target project** | **Fresh, clean Stitch project** — existing project `18267593872196417998` stays as the exploration scratchpad. |
| **Build approach** | **A — Journey-ordered.** Component catalog generated first to lock the visual vocabulary, then screens in user-journey order with their states inline, ~6 screens per Stitch session. |
| **Dark mode** | **2-screen showcase** (Home timeline + Break detail). Not every screen. |
| **Platform** | Mobile / iOS-style (matches existing design system + all existing screens). |

## Design system

Reuse the existing **"Serene Efficiency"** design system already embedded in
project `18267593872196417998` (teal/indigo palette, Manrope + JetBrains Mono,
Korea-specific accent colors `korea-red` / `korea-blue` / `off-day-sage` /
`sand-accent`). Apply it to the fresh project so all screens inherit the same
vocabulary.

Source of truth for app behavior, IA, microcopy, locale rules, and API data
shapes: `docs/stitch/master.md`. Sample data convention: **South Korea, 2026**
(Seollal, Children's Day, Chuseok, etc.), consistent with the existing pack.

## Stitch generation constraints

- One screen per `generate_screen_from_text` call.
- Quality degrades after ~6–8 screens per session → batch ~6 per session.
- `edit_screens` for iteration, `generate_variants` for alternatives.
- Each call returns a screen ID + screenshot URL for review.

## Screen inventory (~37 screens)

Numbering reflects generation/journey order. "State" rows are separate screens.

### 0 · Component Catalog *(generated first)*
- **C1 Foundations** — color tokens, type scale, spacing rhythm, iconography.
- **C2 Components** — buttons (primary / secondary / disabled), inputs
  (default / focus / error), holiday card (free-day / absorbed / weekend
  variants), break card with sparkline mini-map, budget slider, status badges
  (sage PTO / sand free-day), bottom sheet, tab bar, segmented toggle, dashed
  sandwich-day card, and empty / loading / error blocks.

### 1 · Auth & Onboarding
- **1.1** Onboarding carousel (welcome + value props).
- **1.2** Sign Up — email + password, Google + Apple social sign-in.
- **1.3** Log In.
- **1.4** Forgot Password.
- **1.5** Country-of-Work picker — searchable, 250+ countries, KR/NP/JP/IN/PH
  pinned. Drives holiday data + workweek default.
- **1.6** Workweek selector — defaults from country, always overridable
  (Mon–Fri / Sun–Thu / Fri–Sat cases).
- **1.7** PTO Budget — slider 3–25 days.
- **1.8** Country-of-Residence — optional, skippable (expat overlay source).
- **State** 1.S-load — Sign Up loading / submitting.
- **State** 1.S-err — auth error (invalid credentials).

### 2 · Home / Holiday Timeline
- **2.1** Timeline — vertical, grouped by month, holiday cards showing
  date + weekday + name (English + local script), free-day (happy) vs absorbed
  (sad) icon; optional residence-country overlay (distinct treatment).
- **2.2** Calendar view — month grid (toggle from timeline).
- **2.3** Holiday detail **bottom sheet** — on tapping a holiday.
- **State** 2.S-load — skeleton timeline.
- **State** 2.S-empty — unsupported year / no holidays.
- **State** 2.S-err — failed to load holidays.

### 3 · Plan
- **3.1** Length Buffet — budget slider + horizontal carousel of best break of
  each length (3–10 days), each card: dates, length, PTO cost, anchor holidays.
- **3.2** Break Detail — day-by-day breakdown (PTO / weekend / holiday),
  anchors, and ranked same-length alternatives by cheapest PTO cost.
- **3.3** Workweek override — inline selector on the Plan surface.
- **State** 3.S-load — computing plan.
- **State** 3.S-empty — no breaks within budget.
- **State** 3.S-err — plan request failed.

### 4 · Sandwich
- **4.1** Sandwich Detector — single workdays wedged between off-days, with
  one-tap "save this PTO day".
- **4.2** Save-PTO **success** — confirmation (saved, reminder set).
- **State** 4.S-empty — no sandwich days this year.

### 5 · Connect Calendar (Apple Calendar / EventKit)
- **5.1** Permission prime — why connect, deferred + optional.
- **5.2** Permission **denied** — how to enable in Settings.
- **5.3** Calendar picker — which calendars to read.
- **5.4** Synced **success** — break written back as a multi-day event.

### 6 · Settings & Account
- **6.1** Settings — country, workweek, budget, residence, calendar
  integration, theme, locale.
- **6.2** Profile / Account — email, linked social accounts, sign out.
- **6.3** Confirm dialog (modal) — sign out / disconnect calendar.

### 7 · Dark-mode showcase
- **7.1** Home timeline (dark).
- **7.2** Break detail (dark).

## Out of scope (v1, per master.md non-goals)

Social features, sharing, team/manager view, push notifications, in-app
purchases, country comparison (`/v1/compare`) UI, and dark variants beyond the
2-screen showcase.

## Success criteria

- Fresh Stitch project with the Serene Efficiency design system applied.
- All ~37 screens generated with clean, journey-ordered naming.
- Component catalog generated first; later screens visually consistent with it.
- Critical states + loading/skeleton present for the data-heavy surfaces.
- Each screen uses realistic Korea-2026 sample data, not placeholder text.

## Open questions

None blocking. Country-comparison UI and full dark mode are explicitly deferred.
