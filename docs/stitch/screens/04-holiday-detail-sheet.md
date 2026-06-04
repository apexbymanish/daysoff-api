# Screen 4 — Holiday detail sheet

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

A bottom sheet that slides up when the user taps a holiday row on Home
(Screen 3) or any "next holiday" affordance elsewhere in the app. The
sheet's job is to enrich a single holiday with three things: a clearer
date display, 1–2 sentences of historical context, and a list of
"nearby opportunities" (sandwich days, related festivals, plannable
breaks). Users should leave the sheet with a clear next action — either
dismiss because they were curious, or jump into Plan/Sandwich because
they spotted something worth doing.

## Sample data (KR 2026)

- **Holiday:** Chuseok / 추석 — Thu, Sep 24, 2026 (first day of a 3-day
  holiday running Thu–Sat).
- **Historical context:** "Korea's harvest festival, observed for over
  a thousand years. Families return to their hometowns to share food
  and honor their ancestors."
- **Nearby opportunities:**
  1. **Sandwich:** "Wed Sep 23 — take this 1 day for a 5-day break
     (Wed–Sun)."
  2. **Related festival:** "Andong Mask Dance Festival, Sep 25–Oct 4."
  3. **Plan suggestion:** "Stretch to 9 days for 3 PTO (Sep 21–29)."

## Layout

The sheet covers approximately **78% of the screen height** when fully
extended, with the Home timeline visible behind it at 30% opacity.

**Sheet handle:** thin pill 4pt × 36pt at top center, soft grey,
draggable.

**Top bar inside sheet:** sheet title is *not* a top-aligned text label;
instead, a soft close X sits top-right (24pt, neutral grey).

**Hero block (top third of sheet):**

- **Country badge:** small 11pt pill aligned top-center, above the
  day numeral. "🇰🇷 Work" with peach fill for work-country holidays;
  "🇳🇵 Home" with sage fill for residence-country holidays. The badge
  is hidden entirely if the user has no country of residence set
  (no need to disambiguate when only one country is in play).
- Centered "date stack" but bigger than the Home row variant: day
  numeral at 56pt semibold ("24"), abbreviated weekday underneath at
  16pt caps ("THURSDAY"). For multi-day holidays, a horizontal date
  range card directly below: "Thu Sep 24 – Sat Sep 26 · 3 days" in a
  soft peach pill.
- Holiday name in 28pt semibold below the date: "Chuseok".
- Korean script `한글` subhead, 18pt regular, slightly muted: "추석".

**Context block (middle):**

- Section heading "About" in 12pt caps, 60% opacity, left-aligned with
  a 24pt left margin.
- 1–2 paragraph explainer in 15pt regular, line-height 1.5. The first
  sentence is bold to anchor.

**Opportunities block (bottom):**

- Section heading "What's nearby" in 12pt caps, left-aligned.
- Stacked cards, ~72pt each, full-width with 12pt vertical gap:
  - **Sandwich card:** sage tinted background. Left icon: sandwich
    glyph (two horizontal lines). Body: "Take **Wed Sep 23** off →
    5-day break (Wed–Sun)." Right side: chevron + "1 PTO" pill.
  - **Festival card:** neutral background. Left icon: small lantern
    glyph. Body: "Andong Mask Dance Festival, Sep 25–Oct 4." Right:
    chevron.
  - **Plan card:** peach tinted. Left icon: chain-link. Body:
    "Stretch to 9 days for 3 PTO (Sep 21–29)." Right: chevron + "3
    PTO" pill.
  - **Calendar conflict card (only when connected — Screen 9):**
    cream background with a soft warning-triangle glyph on the left.
    Body: "**2 events** during this holiday — Dentist (Sep 24), Team
    standup (Sep 25)." Right: chevron → opens an inline expansion
    listing each event with time and source calendar. Card is hidden
    if there are no overlapping events or if calendar isn't connected.

**Bottom action bar** (inside sheet, fixed):

- Single full-width primary button: "Plan a break around this →"
  (sage fill). Jumps to the Plan tab pre-filtered to this holiday.

## Microcopy

- **Sheet title (screen-reader only):** "{Holiday name} details"
- **Date range pill:** "{startDay} {startMonth} {n} – {endDay}
  {endMonth} {n} · {count} days"
- **About heading:** "About"
- **Opportunities heading:** "What's nearby"
- **Sandwich card pattern:** "Take **{weekday} {month} {day}** off →
  {n}-day break ({weekdayStart}–{weekdayEnd})."
- **Plan card pattern:** "Stretch to {n} days for {n} PTO
  ({startISO}–{endISO})."
- **Primary CTA:** "Plan a break around this"
- **No-context state:** if no historical context exists, render only
  the date hero + opportunities; do not show an empty "About" block.
- **No-opportunities state:** "Nothing nearby this time — but you can
  still plan around it."

## States

- **Default** — populated as in Sample data.
- **No context** — historical-context block omitted entirely (not
  stubbed).
- **No opportunities** — opportunities block replaced with the
  no-opportunities helper text and a slightly smaller primary CTA.
- **Loading** — Sheet animates in immediately with skeleton blocks
  (hero stack uses placeholder boxes; About uses 3 shimmer lines;
  opportunities use 2 skeleton cards). Real content fades in on
  arrival.
- **Single-day holiday** — Date range pill is hidden (just the day
  stack); rest unchanged.
- **Past holiday** — Sheet still works but the primary CTA changes to
  "Plan for next year" (and pre-fills year+1 in the Plan tab).
- **Home-country holiday** — Country badge shows "Home". Primary CTA
  ("Plan a break around this") is hidden — home-country holidays
  don't drive PTO planning. Opportunities block omits sandwich/plan
  suggestions; "What's nearby" shows only festival/context cards
  when relevant, or the no-opportunities helper otherwise.

## Dark mode

Sheet background is a slightly raised surface above the (near-black)
Home timeline behind it — #14171A. The sandwich card's sage tint drops
to a 12% sage fill; the plan card's peach tint to 12% peach fill.
Festival card uses 6% white. Date numerals stay warm-cream. Korean
subhead `한글` keeps full warm tone — never goes flat grey in dark
mode.

## Motion

- **Open:** sheet rises from the bottom (cubic-bezier(0.32, 0.72, 0,
  1), 360ms). Backdrop fades from 0% → 50% opacity over the same
  window.
- **Drag-to-dismiss:** rubber-band resistance after the sheet handle
  passes the top of the screen. Releasing below the threshold snaps
  back (220ms spring); releasing above dismisses (cubic, 280ms).
- **Card tap (sandwich/plan):** card scales to 98% on press, then
  pushes a sheet transition to Plan/Sandwich (320ms).
- **Date hero on multi-day holidays:** the date range pill subtly
  pulses on first render (scale 100% → 102% over 240ms) to draw the
  eye to the count.
- **No bouncy entries** — keep motion calm, this is informational, not
  celebratory.

## Accessibility

- Sheet uses a focus trap; tab cycles within the sheet, ESC closes.
- VoiceOver focus on open lands on the hero date stack and reads:
  "Chuseok, Thursday September 24th, 3-day holiday through Saturday
  September 26th."
- The "About" paragraph is announced as plain body text.
- Each opportunity card announces as a single button: "Sandwich
  opportunity. Take Wednesday September 23rd off. 5-day break.
  Costs 1 PTO. Button."
- Close X has `aria-label="Close holiday details"`.
- Background timeline behind the sheet is `aria-hidden` while the
  sheet is open.
- Dynamic Type: hero day numeral reflows from 56pt down to 40pt at
  largest accessibility size; body text reflows as expected.
- Reduced-motion: drag-to-dismiss still works but uses linear
  transitions; pulse on the date range pill disables.
