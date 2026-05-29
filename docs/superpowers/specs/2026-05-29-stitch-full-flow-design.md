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

### UX design decisions (design-critique pass)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Value-first entry** | Let users pick a country and **browse holidays + a teaser plan before signup**. Gate only saving, calendar sync, and cross-device prefs. | The "aha" (long break for little PTO) sells the signup; hiding it behind an account wall kills conversion. The holiday API is public read-only anyway. |
| **Minimal onboarding** | Ask **country only** up front. Infer workweek from country, default budget to 15 ("change anytime"), defer residence to a contextual later prompt. Workweek/budget/residence become **Settings editors**, not linear onboarding steps. | Progressive disclosure + smart defaults — fastest path to value. |
| **Sandwich = section, not tab** | 3-tab IA (**Home / Plan / Settings**). Sandwich-day detection lives **inside Plan** as a section. | Sandwich is a mode of planning, not a peer destination; tab bars get muddy past 4. |
| **Saved & Reminders** | Saved breaks + saved PTO days (with reminders) live on a **"Saved & Reminders"** screen reachable from the Home header — not a 4th tab. | Reminders need a real home without breaking the 3-tab IA. |
| **Reminders scope** | **Local / calendar-based reminders** (the "save this PTO day → reminder" action). NOT marketing push notifications (still a non-goal). | Honors master.md non-goals while delivering the requested reminder feature. |
| **Reversible calendar writes** | Saving a break **previews events before write**, confirms *"Added N events,"* and offers **undo**. Warn on conflicts with personal events. | Silently mutating a user's real calendar erodes trust; preview + undo is the safe pattern. |
| **Scenery as accent** | Scenic/festival photography appears on **emotional/payoff moments only**: a Welcome splash, holiday & break **detail heroes**, and as a **calm backdrop in empty states** (CTA stays the headline). Timeline, plan buffet, and lists stay clean and data-dense. | The Serene Efficiency system is minimal + Linear-density; pervasive photography fights it. Accent-only contrast reads premium, not like a stock-photo travel app. Destination/inspiration gallery and a seasonal showcase board are **out** (v2 / marketing, not in-app). |

### Per-screen craft patterns (applied throughout)

- **Outcome-first cards** — hero the break *length* ("9-day break"), then dates,
  then PTO cost as satisfying small print. **"Best value" badge** on the
  highest-leverage option (most days off per PTO day).
- **Empty-state-as-CTA** — e.g. "No breaks within budget" → *"Bump budget to 18
  → unlocks a 9-day Chuseok break."*
- **Pre-permission priming** — never trigger the OS calendar dialog cold; prime
  with value first.
- **Redundant encoding** — never rely on hue alone (sage PTO / sand free-day /
  red holiday / gray workday); always pair color with icon or label
  (~8% red-green colorblind).
- **Locale hierarchy** — decide which script leads per locale (e.g. Hangul
  primary for KR users), not English-with-a-translation-appended.
- **Skeletons over spinners** on data-heavy screens; **persist view preference**
  (timeline ⇄ calendar toggle remembered).
- **Benefit-led microcopy** — concrete dates, no exclamation marks, treat the
  user like a busy adult (per master.md voice).
- **Text-over-image scrim** — any text on scenic photography sits on a
  gradient/scrim for legibility (critical in dark mode). For mockups, reuse the
  scenic imagery already generated in project `18267593872196417998`
  (Chuseok Hanok, Himalayas, Kyoto Zen garden, Kerala backwaters, etc.).
  Production needs a real per-holiday image strategy (curated set + fallback).

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

## Screen inventory (~39 screens)

Numbering reflects generation/journey order. "State" rows are separate screens.

### 0 · Component Catalog *(generated first)*
- **C1 Foundations** — color tokens, type scale, spacing rhythm, iconography.
- **C2 Components** — buttons (primary / secondary / disabled), inputs
  (default / focus / error), holiday card (free-day / absorbed / weekend),
  break card with sparkline + "best value" badge, budget slider, status badges
  (sage PTO / sand free-day), reminder row, bottom sheet, tab bar, segmented
  toggle, dashed sandwich-day card, guest/upsell banner, undo toast, and
  empty / loading / error blocks.

### 1 · Entry & Auth *(value-first)*
- **1.0** Welcome — full-bleed **scenic** splash (calm, aspirational) with the
  value prop and a single "Get started" CTA into country pick.
- **1.1** First-launch country pick — searchable, 250+ countries,
  KR/NP/JP/IN/PH pinned. The single up-front step; no account required.
- **1.2** Guest Home preview — browsing as guest, with subtle "sign up to save"
  affordances on gated actions.
- **1.3** Sign Up — email + password, Google + Apple; **contextual** (triggered
  when a guest taps save / sync).
- **1.4** Log In.
- **1.5** Forgot Password.
- **State** 1.S-load — auth submitting.
- **State** 1.S-err — auth error (invalid credentials).

### 2 · Home / Holiday Timeline
- **2.1** Timeline — vertical, grouped by month; holiday cards show
  date + weekday + name (local script primary + English), free-day (happy) vs
  absorbed (sad) icon; optional residence-country overlay (distinct treatment);
  header entry to **Saved & Reminders**.
- **2.2** Calendar view — month grid (toggle from timeline; preference persisted).
- **2.3** Holiday detail **bottom sheet** — on tapping a holiday; **scenic
  festival hero** tied to the holiday (e.g. Chuseok → Hanok courtyard).
- **State** 2.S-load — skeleton timeline.
- **State** 2.S-empty — unsupported year / no holidays (empty-as-CTA, calm
  scenic backdrop).
- **State** 2.S-err — failed to load holidays.

### 3 · Plan
- **3.1** Length Buffet — budget slider + horizontal carousel of best break of
  each length (3–10 days); outcome-first cards (length → dates → PTO cost);
  "best value" badge.
- **3.2** Break Detail — **scenic hero** of the anchor holiday, then day-by-day
  breakdown (PTO / weekend / holiday), anchors, and ranked same-length
  alternatives by cheapest PTO cost.
- **3.3** Sandwich section — single workdays wedged between off-days, with
  one-tap "save this PTO day" (lives inside Plan, not a tab).
- **3.4** Workweek override — inline selector on the Plan surface.
- **State** 3.S-load — computing plan.
- **State** 3.S-empty — no breaks within budget (empty-as-CTA: suggest a budget bump).
- **State** 3.S-err — plan request failed.

### 4 · Save, Calendar & Reminders
- **4.1** Save break — **preview the events before writing** (reversible pattern).
- **4.2** Calendar write **success** — "Added N events to your calendar" + undo.
- **4.3** Reminder **set** confirmation — PTO day / break reminder.
- **4.4** Saved & Reminders list — saved breaks + saved sandwich PTO days, each
  with reminder status; reachable from the Home header.
- **4.5** Connect Calendar — permission prime (why connect; deferred + optional).
- **4.6** Permission **denied** — how to enable in Settings.
- **4.7** Calendar picker — which calendars to read.
- **State** 4.S-conflict — planned break overlaps a personal event (warning).

### 5 · Settings & Account
- **5.1** Settings — country of work, workweek, budget, residence, calendar
  integration, reminder prefs, theme, locale.
- **5.2** Workweek editor — defaults from country, always overridable
  (Mon–Fri / Sun–Thu / Fri–Sat).
- **5.3** PTO budget editor — slider 3–25 days.
- **5.4** Country-of-residence editor — optional (expat overlay source).
- **5.5** Profile / Account — email, linked social accounts, sign out.
- **5.6** Confirm dialog (modal) — sign out / disconnect calendar / delete reminder.

### 5b · Block-a-date (personal commitments) — added 2026-05-29
- **5b.1** Block-a-date sheet — tapping a date (on Home timeline/calendar)
  opens a bottom sheet: "Mark **Mon Sep 22** as busy?" with an optional
  one-line note field ("Friends meeting", "Birthday party · 7pm") and a
  primary "Block this day" + "Cancel". Works for guests (no account/calendar
  needed).
- Behavior (no new screen, applied to existing surfaces): blocked dates show
  a small "busy" dot/marker on Home (2.1/2.2); the Plan engine **skips breaks
  that overlap a blocked date** (reuses the 4.S conflict pattern); blocked
  dates appear as an editable "Busy dates" group in **Saved & Reminders**
  (4.4). For connected-calendar users this layers on top of the read-only
  event overlay — both feed the same conflict-awareness.
- Scope guard: lightweight marker only (date + optional note), NOT a full
  event editor with times/recurrence — for that, users connect their real
  calendar. Keeps daysoff from becoming a second calendar to maintain.

### 6 · Dark-mode showcase
- **6.1** Home timeline (dark).
- **6.2** Break detail (dark).

## Out of scope (v1, per master.md non-goals)

Social features, sharing, team/manager view, **marketing push notifications**
(local/calendar reminders ARE in scope), in-app purchases, country comparison
(`/v1/compare`) UI, dark variants beyond the 2-screen showcase, a **destination
/ travel-inspiration gallery** (v2 — off-mission for a PTO optimizer), and a
**seasonal scenery showcase board** (marketing/app-store asset, not an in-app
screen).

## Success criteria

- Fresh Stitch project with the Serene Efficiency design system applied.
- All ~39 screens generated with clean, journey-ordered naming.
- Scenery used as an accent (welcome, detail heroes, empty backdrops) with
  legible text scrims — not pervasive across lists/timeline/plan.
- Component catalog generated first; later screens visually consistent with it.
- Value-first entry: holidays + teaser plan browsable before signup; auth is
  contextual on save/sync.
- Critical states + loading/skeleton present for the data-heavy surfaces.
- Calendar writes are previewed + reversible; reminders have a home (Saved
  & Reminders).
- Each screen uses realistic Korea-2026 sample data, not placeholder text.

## Open questions

None blocking. Country-comparison UI and full dark mode are explicitly deferred.
