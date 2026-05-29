# daysoff Full Stitch Flow — Implementation Plan (Generation Runbook)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate the complete ~39-screen daysoff app surface (component catalog, value-first entry, home, plan, save/calendar/reminders, settings, dark showcase) into a fresh Google Stitch project via the Stitch MCP.

**Architecture:** Journey-ordered generation in review-gated sessions of ~6 screens. A fresh Stitch project gets the "Serene Efficiency" design system applied, then the component catalog is generated first to lock the visual vocabulary, then app screens in user-journey order with states inline. Prompts live in `docs/stitch/` (master + per-screen files); screens live in Stitch.

**Tech Stack:** Google Stitch MCP (`mcp__stitch__*`), `docs/stitch/master.md` + `docs/stitch/screens/*.md` prompt pack.

**Not code/TDD:** there are no unit tests. Each screen's verification is a **screenshot review against acceptance criteria** (returned `screenshot.downloadUrl`) before proceeding. "Commit" steps apply only to prompt-pack file edits in git, not to Stitch screens.

**Spec:** `docs/superpowers/specs/2026-05-29-stitch-full-flow-design.md`

---

## File Structure (prompt pack)

The pack drives generation. Paste order per session: `master.md` first, then the screen file.

**Modify (existing → new structure):**
- `docs/stitch/master.md` — update for value-first entry, 3-tab IA (Home/Plan/Settings), Sandwich-as-Plan-section, Saved & Reminders, local reminders scope, scenery-as-accent.
- `docs/stitch/screens/01-onboarding.md` — split: auth no longer gates; becomes the minimal-onboarding reference. Superseded by new `1x-*` files below; keep as reference.
- `docs/stitch/screens/03-home-holiday-timeline.md` — tab bar 4→3 (drop Sandwich tab); add Saved & Reminders header entry.
- `docs/stitch/screens/04-holiday-detail-sheet.md` — add scenic festival hero.
- `docs/stitch/screens/05-plan-length-buffet.md` — tab bar 4→3; add Sandwich section affordance.
- `docs/stitch/screens/06-break-detail.md` — add scenic hero; add Save-break entry (preview→write).
- `docs/stitch/screens/07-sandwich-tab.md` — reframe from tab to **section inside Plan**.
- `docs/stitch/screens/08-settings.md` — add reminder prefs; confirm 3-tab.
- `docs/stitch/screens/09-connect-calendar.md` — keep (prime→picker), feeds 4.5–4.7.

**Create (new screen prompts):**
- `docs/stitch/screens/cat-foundations.md` (C1)
- `docs/stitch/screens/cat-components.md` (C2)
- `docs/stitch/screens/10-welcome.md` (1.0)
- `docs/stitch/screens/11-country-pick.md` (1.1)
- `docs/stitch/screens/12-guest-home-preview.md` (1.2)
- `docs/stitch/screens/13-signup.md` (1.3), `14-login.md` (1.4) — split from old 01
- `docs/stitch/screens/15-save-break-preview.md` (4.1)
- `docs/stitch/screens/16-calendar-write-success.md` (4.2)
- `docs/stitch/screens/17-reminder-set.md` (4.3)
- `docs/stitch/screens/18-saved-and-reminders.md` (4.4)
- `docs/stitch/screens/19-settings-editors.md` (5.2–5.4: workweek / budget / residence editors)
- `docs/stitch/screens/20-profile-account.md` (5.5), `21-confirm-dialog.md` (5.6)
- State prompts are short and authored inline in their generation step (no separate file needed).

---

## Screen → session map (~39 screens)

| Session | Screens | Count |
|---|---|---|
| 1 | C1 Foundations, C2 Components | 2 |
| 2 | 1.0 Welcome, 1.1 Country pick, 1.2 Guest preview, 1.3 Sign up, 1.4 Log in, 1.5 Forgot pw | 6 |
| 3 | 1.S-load, 1.S-err, 2.1 Timeline, 2.2 Calendar, 2.3 Holiday sheet, 2.S-load | 6 |
| 4 | 2.S-empty, 2.S-err, 3.1 Buffet, 3.2 Break detail, 3.3 Sandwich section, 3.4 Workweek override | 6 |
| 5 | 3.S-load, 3.S-empty, 3.S-err, 4.1 Save preview, 4.2 Write success, 4.3 Reminder set | 6 |
| 6 | 4.4 Saved & Reminders, 4.5 Connect prime, 4.6 Permission denied, 4.7 Calendar picker, 4.S-conflict, 5.1 Settings | 6 |
| 7 | 5.2 Workweek editor, 5.3 Budget editor, 5.4 Residence editor, 5.5 Profile, 5.6 Confirm dialog, 6.1 Home (dark) | 6 |
| 8 | 6.2 Break detail (dark) | 1 |

Reset the Stitch session between batches (start a fresh chat / re-send `master.md`) to avoid per-session quality decay.

---

## Phase 0 — Setup & prompt-pack prep

### Task 0.1: Update master.md to the new structure

**Files:** Modify `docs/stitch/master.md`

- [ ] **Step 1:** Edit the "Three primary user flows" + "Hard requirements" sections so they read:
  - Entry is **value-first**: a guest picks a country and browses holidays + a teaser plan *before* signup; account is required only to **save breaks, sync calendar, and persist preferences across devices**.
  - Navigation is **3 tabs — Home / Plan / Settings**. Sandwich-day detection is a **section inside Plan**, not a tab.
  - **Saved & Reminders**: saving a break/PTO day sets a **local/calendar reminder**; saved items live on a Saved & Reminders screen reachable from the Home header.
  - Calendar writes are **previewed before write, confirmed, and undoable**; conflicts with personal events are warned.
- [ ] **Step 2:** Add a "Visual accent" note: scenic/festival photography appears only on Welcome, holiday & break detail heroes, and as a calm empty-state backdrop (with text scrim); lists/timeline/plan stay data-dense.
- [ ] **Step 3:** Update "Non-goals" — keep no-social/no-sharing/no-team/no-IAP; clarify **marketing push notifications are out, local/calendar reminders are in**.
- [ ] **Step 4:** Commit.

```bash
git add docs/stitch/master.md
git commit -m "docs(stitch): update master prompt for value-first 3-tab structure + reminders"
```

### Task 0.2: Edit existing screen prompts for the new structure

**Files:** Modify `docs/stitch/screens/03-home-holiday-timeline.md`, `05-plan-length-buffet.md`, `06-break-detail.md`, `07-sandwich-tab.md`, `04-holiday-detail-sheet.md`, `08-settings.md`

- [ ] **Step 1:** In `03-…` and `05-…`: change the bottom tab bar from 4 tabs to **3 (Holidays / Plan / Settings)**; in `03-…` add a "Saved & Reminders" entry in the sticky header (bookmark glyph) routing to screen 4.4.
- [ ] **Step 2:** In `07-sandwich-tab.md`: reframe the header note from "a tab" to "a **section within the Plan tab**, reached by scrolling below the length buffet or via a 'Sandwich days' segmented control." Keep all sample data/layout.
- [ ] **Step 3:** In `04-…` and `06-…`: add a "Scenic hero" layout note — full-bleed festival photo header tied to the holiday (Chuseok → Hanok courtyard) with a bottom gradient scrim for legible overlaid text. In `06-…` add a primary "Save this break" action that routes to the Save-break preview (4.1).
- [ ] **Step 4:** In `08-settings.md`: add a "Reminders" preferences row group (default reminder lead time, calendar-vs-local) and confirm the 3-tab bar.
- [ ] **Step 5:** Commit.

```bash
git add docs/stitch/screens/
git commit -m "docs(stitch): adapt existing screen prompts to 3-tab + scenery + save flow"
```

### Task 0.3: Author the new screen prompt files

**Files:** Create the files listed in "Create" above. Each follows the existing pack style (Purpose / Sample data KR-2026 / Layout / Microcopy / States / Dark mode / Accessibility), tightened. Content for each is provided in its generation task below; author the file first, then generate from it.

- [ ] **Step 1:** Create `cat-foundations.md`, `cat-components.md`, `10-welcome.md`, `11-country-pick.md`, `12-guest-home-preview.md`, `13-signup.md`, `14-login.md`, `15-save-break-preview.md`, `16-calendar-write-success.md`, `17-reminder-set.md`, `18-saved-and-reminders.md`, `19-settings-editors.md`, `20-profile-account.md`, `21-confirm-dialog.md` using the prompt bodies embedded in the matching generation tasks (Sessions 1–8 below).
- [ ] **Step 2:** Commit.

```bash
git add docs/stitch/screens/
git commit -m "docs(stitch): author new screen prompts for full flow (catalog, entry, save, reminders)"
```

### Task 0.4: Create the fresh Stitch project

**Tool:** `mcp__stitch__create_project`

- [ ] **Step 1:** Load the tool schema: `ToolSearch "select:mcp__stitch__create_project"`.
- [ ] **Step 2:** Create a MOBILE, `TEXT_TO_UI_PRO` project titled **"daysoff — Full Flow"**.
- [ ] **Step 3:** Record the returned project id as `NEW_PROJECT_ID` (use it in every generation call). Expected: a `projects/<id>` name.

### Task 0.5: Apply the Serene Efficiency design system

**Tools:** `mcp__stitch__create_design_system_from_design_md` (or `upload_design_md`) + `mcp__stitch__apply_design_system`

- [ ] **Step 1:** Load schemas: `ToolSearch "select:mcp__stitch__create_design_system_from_design_md,mcp__stitch__apply_design_system,mcp__stitch__upload_design_md,mcp__stitch__list_design_systems"`.
- [ ] **Step 2:** Source the design markdown: the embedded `designMd` from existing project `18267593872196417998` (the "Serene Efficiency" block — teal/indigo, Manrope + JetBrains Mono, korea-red/blue, off-day-sage, sand-accent). Create a design system from it.
- [ ] **Step 3:** Apply it to `NEW_PROJECT_ID`.
- [ ] **Step 4:** Verify via `get_project` that the theme `designMd` name is "Serene Efficiency". Expected: theme applied, MOBILE device.

---

## Session 1 — Component catalog (locks the vocabulary)

> Reset session. Send `master.md`, then the catalog prompt. Generate, review, iterate with `edit_screens` before moving on — these two anchor everything after.

### Task 1.1: C1 Foundations
**Prompt file:** `cat-foundations.md`. **Tool:** `generate_screen_from_text(projectId=NEW_PROJECT_ID, prompt=<master.md + file body>)`

Prompt body:
> A design-system **foundations** board for the daysoff app (reference, not an app screen). On a single tall mobile-width canvas, lay out, in labeled sections: (1) **Color tokens** — swatches with hex + name for primary teal `#1a4d4e`, indigo secondary, off-day-sage `#8E9775`, sand-accent `#E9C46A`, korea-red `#CD2E3A`, korea-blue `#0047A0`, plus surface/on-surface neutrals for light and dark. (2) **Typography** — Manrope scale (display-numeral 48, headline-lg 24, headline-md 20, body-lg 17, body-sm 14) and JetBrains Mono label-caps 12, each shown as a live specimen with name + size. (3) **Spacing** — 4px-grid rhythm bars (4/8/12/16/32). (4) **Iconography** — a monoline icon row (sun = free day, moon = absorbed, sandwich, chain-link, bell = reminder, calendar). Calm, organized, generous whitespace; this is a spec sheet.

- [ ] **Step 1:** Generate. **Step 2:** Review screenshot — acceptance: all 6 brand colors present with hex; type specimens legible; light+dark neutrals shown; monoline icons. Iterate with `edit_screens` if off.

### Task 1.2: C2 Components
**Prompt file:** `cat-components.md`.

Prompt body:
> A design-system **component catalog** board for daysoff (reference, not an app screen). Lay out labeled component groups on one tall mobile-width canvas: **Buttons** (primary sage-fill, secondary teal-outline, disabled); **Inputs** (default, focused with floating label, error with icon+message); **Holiday card** in 3 variants (free-day peach sun, absorbed grey moon, weekend); **Break card** with the day-ribbon sparkline `[H][W][P][P][H]` + a "BEST VALUE" badge + PTO-cost pill; **Budget slider** (3–25, sage track, peach handle); **Status badges** (sage PTO, sand free-day); **Reminder row** (bell glyph, lead-time, toggle); **Bottom sheet** handle; **3-tab bar** (Holidays/Plan/Settings); **Segmented toggle**; **Dashed sandwich-day card**; **Guest/upsell banner** ("Sign up to save"); **Undo toast**; and **empty / loading-skeleton / error** blocks. Each component labeled. Colors paired with icons/text, never hue alone.

- [ ] **Step 1:** Generate. **Step 2:** Review — acceptance: every component group present and labeled; states shown; redundant encoding visible (icon+color). Iterate before Session 2.

---

## Session 2 — Entry & Auth (value-first)

> Reset session. Re-send `master.md` each new chat.

### Task 2.1: 1.0 Welcome (`10-welcome.md`)
> Full-bleed **scenic** splash (calm Korean Hanok-at-sunrise or Himalayas golden-hour photo) with a bottom gradient scrim. Centered logotype "daysoff" upper third; one calm line "Find the longest break for the fewest days off"; sub-line "Built for 연차, बिदा, 有給休暇, and every other word for it." Single primary CTA "Get started" → country pick; text link "I already have an account" → Log in. No forced signup. Calm 240ms fade-in, no bouncy splash.

- [ ] Generate · Review — acceptance: scenic hero with legible scrimmed text; single Get-started CTA; secondary login link; no signup wall.

### Task 2.2: 1.1 Country pick (`11-country-pick.md`)
> First real step, **no account required**. Header "Where do you work?" Searchable country list, 250+ countries, with **KR/NP/JP/IN/PH pinned** at top showing flag + name + ISO (`🇰🇷 South Korea · KR`). Search field sticky on top with 8 skeleton rows while loading. Helper: "We use this to mark red days and weekends correctly." Selecting a country advances to the guest Home preview. Small "I live somewhere else (optional)" link deferred — not required here.

- [ ] Generate · Review — acceptance: search + pinned 5 countries; no auth; KR selectable.

### Task 2.3: 1.2 Guest Home preview (`12-guest-home-preview.md`)
> The Home holiday timeline (reuse `03-…` layout, KR 2026 sample data) **in guest mode**: fully browsable, but gated actions show the guest/upsell banner ("Sign up to save this break"). A subtle top strip "Browsing as guest" with a "Sign up" pill. Plan tab is reachable and shows a teaser buffet, but "Save"/"Sync" trigger the signup sheet (1.3). 3-tab bar present.

- [ ] Generate · Review — acceptance: real timeline visible without account; upsell affordances on save; guest strip present.

### Task 2.4: 1.3 Sign Up (`13-signup.md`)
> Contextual signup sheet/screen (triggered by a gated action). Segmented `[ Sign up | Sign in ]`. Social: "Continue with Google", "Continue with Apple" stacked; "or" divider; Email + Password (show/hide eye). Primary "Create account". Footer "By continuing you agree to the Terms and Privacy Policy." Korean locale shows 회원가입/로그인 alongside. Context line at top: "Sign up to save your breaks and sync your calendar."

- [ ] Generate · Review — acceptance: social + email; contextual "why signup" line; bilingual labels.

### Task 2.5: 1.4 Log In (`14-login.md`)
> Sign-in variant: email + password, social buttons, "Forgot password?" link → 1.5. Primary "Sign in".

- [ ] Generate · Review — acceptance: sign-in form, forgot-password link.

### Task 2.6: 1.5 Forgot Password (existing `02-forgot-password.md`)
> Generate from the existing file unchanged.

- [ ] Generate · Review — acceptance: email entry + reset-sent confirmation.

---

## Session 3 — Auth states + Home core

> Reset session.

### Task 3.1: 1.S-load — auth submitting
> The Sign Up screen (2.4) in **loading** state: primary button collapses to a 56px square spinner, fields locked, toggle disabled.
- [ ] Generate · Review — acceptance: button-spinner, locked fields.

### Task 3.2: 1.S-err — auth error
> The Sign Up screen with **inline error**: red helper "We don't recognize that email." under the field with an error icon (not color alone); button stays enabled to retry.
- [ ] Generate · Review — acceptance: iconed inline error, ret*able.

### Task 3.3: 2.1 Home Timeline (existing `03-…`, edited in 0.2)
- [ ] Generate · Review — acceptance: month-grouped rows, free/absorbed glyphs, 3-tab bar, Saved entry in header, residence overlay variant.

### Task 3.4: 2.2 Calendar view
> Home in **month-grid calendar** view (toggle from timeline), KR 2026; red days marked, free vs absorbed encoded by glyph+color; segmented toggle Timeline|Calendar at top; preference persists.
- [ ] Generate · Review — acceptance: grid, toggle, encoded days.

### Task 3.5: 2.3 Holiday detail sheet (existing `04-…`, edited in 0.2)
- [ ] Generate · Review — acceptance: scenic festival hero + scrim; About + What's-nearby; "Plan a break around this".

### Task 3.6: 2.S-load — skeleton timeline
> Home timeline **loading**: placeholder month header + 6 shimmer rows, no text.
- [ ] Generate · Review — acceptance: skeleton shimmer, no spinner.

---

## Session 4 — Home states + Plan core

> Reset session.

### Task 4.1: 2.S-empty — empty-as-CTA
> Home **empty** (year fully past / unsupported): calm scenic backdrop, centered card "No more holidays this year." body "Switch to 2027 to plan ahead." with a year-stepper CTA. CTA is the headline, image is backdrop.
- [ ] Generate · Review — acceptance: CTA primary over scenic backdrop.

### Task 4.2: 2.S-err — load error
> Home **error** banner above body: "Couldn't refresh holidays. Showing cached data from {time}." with retry icon; cached rows dimmed behind.
- [ ] Generate · Review — acceptance: error banner + retry.

### Task 4.3: 3.1 Plan Length Buffet (existing `05-…`, edited in 0.2)
- [ ] Generate · Review — acceptance: 8 break cards w/ ribbon + PTO pill + best-value badge; outcome-first; 3-tab bar.

### Task 4.4: 3.2 Break Detail (existing `06-…`, edited in 0.2)
- [ ] Generate · Review — acceptance: scenic hero; day-by-day breakdown; ranked alternatives; "Save this break" CTA.

### Task 4.5: 3.3 Sandwich section (existing `07-…`, reframed in 0.2)
> Generate as a **section within Plan** (segmented "Length buffet | Sandwich days"), KR 2026 sandwich days, one-tap "save this PTO day".
- [ ] Generate · Review — acceptance: lives under Plan, not a 4th tab; dashed sandwich cards; save action.

### Task 4.6: 3.4 Workweek override (inline)
> Plan with the inline **workweek** quick-edit sheet open (7 day-pills, Sat/Sun preselected, Nepal helper); cards re-compute note.
- [ ] Generate · Review — acceptance: day-pill selector sheet over Plan.

---

## Session 5 — Plan states + Save/Reminders core

> Reset session.

### Task 5.1: 3.S-load — computing plan
> Plan buffet **loading**: 8 skeleton cards + shimmer stats strip.
- [ ] Generate · Review — acceptance: skeleton cards.

### Task 5.2: 3.S-empty — empty-as-CTA
> Plan **empty** (no breaks within budget): centered card "No breaks within your budget." body "Bump budget to 18 → unlocks a 9-day Chuseok break." with an "Edit budget" CTA.
- [ ] Generate · Review — acceptance: actionable empty (suggests a budget bump).

### Task 5.3: 3.S-err — plan failed
> Plan **error**: "Couldn't build your plan. Check your connection and retry." retry button.
- [ ] Generate · Review — acceptance: error + retry.

### Task 5.4: 4.1 Save-break preview (`15-save-break-preview.md`)
> A confirmation sheet shown when saving a break, **before writing to the calendar**. Title "Add to your calendar?" Lists the exact events to be created (e.g., "Chuseok break · Sep 23–27 · 1 PTO day (Sep 23)") with a per-day mini-list. Toggle "Also set a reminder" (default on, lead-time chip "2 weeks before"). Primary "Add 1 event" + secondary "Not now". Conflict note if overlaps exist. Reversible-by-design messaging.
- [ ] Generate · Review — acceptance: preview-before-write; reminder toggle; explicit event count.

### Task 5.5: 4.2 Calendar write success (`16-calendar-write-success.md`)
> **Success** confirmation after write: check-mark, "Added to your calendar — Chuseok break, Sep 23–27." an **Undo** affordance (undo toast) and "View in Saved". Calm, no exclamation.
- [ ] Generate · Review — acceptance: success + undo + link to Saved.

### Task 5.6: 4.3 Reminder set (`17-reminder-set.md`)
> **Reminder set** confirmation (for a saved PTO day / sandwich day): bell glyph, "Reminder set — we'll nudge you on Sep 9 to request Sep 23 off." edit lead-time link; "Done".
- [ ] Generate · Review — acceptance: local reminder confirmation, editable lead-time.

---

## Session 6 — Saved/Reminders, Calendar connect, Settings

> Reset session.

### Task 6.1: 4.4 Saved & Reminders (`18-saved-and-reminders.md`)
> A list screen reached from the Home header. Two sections: **Saved breaks** (cards: name, dates, PTO cost, calendar-synced badge, reminder bell) and **Saved PTO days** (sandwich days with reminder status). Swipe to delete (→ confirm dialog 5.6). Empty state "Nothing saved yet — plan a break to get started." Not a tab.
- [ ] Generate · Review — acceptance: two sections; reminder + sync badges; reachable from Home; empty state.

### Task 6.2: 4.5 Connect Calendar prime (existing `09-…`)
> Generate the permission-prime portion: value explainer before the OS dialog ("See your events alongside holidays, get conflict warnings, save breaks as events"), "Connect" + "Maybe later". Deferred/optional.
- [ ] Generate · Review — acceptance: pre-permission priming, optional.

### Task 6.3: 4.6 Permission denied
> Calendar **denied** state: "Calendar access is off." steps to enable in iOS Settings, "Open Settings" button; app still fully usable without it.
- [ ] Generate · Review — acceptance: how-to-enable + graceful degradation.

### Task 6.4: 4.7 Calendar picker
> **Which calendars to read**: list of the user's calendars with color stripes + checkboxes (Personal, Work — Naver, Family), "Done". From `09-…`.
- [ ] Generate · Review — acceptance: multi-select calendar list with colors.

### Task 6.5: 4.S-conflict — conflict warning
> A break with a **calendar conflict**: warning-triangle on the break/save sheet, "2 events during this break — Dentist (Sep 24), Team standup (Sep 25)", expandable list; user can proceed or adjust.
- [ ] Generate · Review — acceptance: conflict surfaced, not blocking.

### Task 6.6: 5.1 Settings (existing `08-…`, edited in 0.2)
- [ ] Generate · Review — acceptance: country/workweek/budget/residence/calendar/**reminders**/theme/locale rows; 3-tab bar.

---

## Session 7 — Settings editors, account, dark (1/2)

> Reset session.

### Task 7.1: 5.2 Workweek editor (`19-settings-editors.md` — part A)
> Standalone **workweek** editor: 7 day-pills (Sat/Sun preselected), defaults-from-country note, Nepal Sat/Sun-since-2026 helper, "Save".
- [ ] Generate · Review — acceptance: day-pill multi-select, country default note.

### Task 7.2: 5.3 PTO budget editor (`19-…` — part B)
> Standalone **budget** editor: 72pt live numeral, slider 3–25 default 15, ticks; "You can change this anytime." "Save".
- [ ] Generate · Review — acceptance: large numeral + slider.

### Task 7.3: 5.4 Country-of-residence editor (`19-…` — part C)
> Optional **residence** editor: searchable country picker, "Remove" affordance, explainer "We'll show your home country's holidays on the timeline too."
- [ ] Generate · Review — acceptance: optional, removable, explainer.

### Task 7.4: 5.5 Profile / Account (`20-profile-account.md`)
> Account screen: avatar placeholder, email, linked social accounts (Google/Apple chips), "Sign out" (→ confirm 5.6), "Delete account" (subtle, destructive).
- [ ] Generate · Review — acceptance: email + linked accounts + sign out.

### Task 7.5: 5.6 Confirm dialog (`21-confirm-dialog.md`)
> A reusable modal: title "Sign out?" / "Disconnect calendar?" / "Delete this reminder?", body explaining consequence, destructive primary + cancel. Show the sign-out variant.
- [ ] Generate · Review — acceptance: destructive confirm modal with cancel.

### Task 7.6: 6.1 Home timeline (dark)
> Home timeline in **dark mode**: near-black `#0B0D0E`, warm-cream numerals, peach free-day glyph at full saturation, absorbed moon at 30%, teal hero strip with peach numeral.
- [ ] Generate · Review — acceptance: Apple-Calendar-dark feel, accents pop.

---

## Session 8 — Dark (2/2)

### Task 8.1: 6.2 Break detail (dark)
> Break detail in **dark mode**: scenic hero with stronger scrim for legibility; raised surface `#14171A`; sage/peach tints at ~12%; warm-cream numerals; Korean subhead keeps warm tone.
- [ ] Generate · Review — acceptance: legible scrimmed hero in dark; semantic colors hold.

---

## Self-review checklist (run before execution)

- [ ] **Spec coverage:** every spec screen (C1–C2, 1.0–1.5, 2.1–2.3 + states, 3.1–3.4 + states, 4.1–4.7 + conflict, 5.1–5.6, 6.1–6.2) maps to a task above. ✓ (39)
- [ ] **No placeholders:** each generation task has a concrete prompt body + acceptance criteria.
- [ ] **Naming consistency:** screen titles set in Stitch match the spec numbering (prefix titles, e.g. "1.0 Welcome", for clean ordering).
- [ ] **Tab-count consistency:** every app-chrome screen shows the **3-tab** bar (Holidays/Plan/Settings); Sandwich never appears as a tab.

## Post-generation

- [ ] `list_screens` on `NEW_PROJECT_ID`; confirm ~39 screens with clean titles.
- [ ] Spot-check the journey by screenshot: Welcome → Country → Guest Home → (gate) Sign up → Home → Plan → Break detail → Save preview → Success → Saved & Reminders.
- [ ] Note any screens needing `generate_variants` or `edit_screens` follow-ups.
