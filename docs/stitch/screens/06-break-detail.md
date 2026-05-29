# Screen 6 — Break detail

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

Drill-down from a card in the length-buffet carousel (Screen 5). Shows
the day-by-day composition of the selected break so the user can see
exactly which days are PTO, which are holiday, and which are weekend —
plus a list of alternative same-length breaks ranked by PTO cost. The
goal is to give the user enough confidence to commit ("yes, that's the
break I want") and a "Save to plan" mock action that establishes the
v2 surface even though there's no real persistence in v1.

## Sample data (KR 2026)

Matches the existing `/v1/plan` sample response in `master.md`:

- **Selected break:** 5-day break, Sep 23–27, 2026, 1 PTO day,
  anchored on Chuseok.
- **Day breakdown:**
  - Wed, Sep 23 — 🏖️ PTO (1 day used)
  - Thu, Sep 24 — 🏢 Holiday: The day preceding Chuseok
  - Fri, Sep 25 — 🏢 Holiday: Chuseok
  - Sat, Sep 26 — 🟦 Weekend (also "The second day of Chuseok")
  - Sun, Sep 27 — 🟦 Weekend
- **Return on PTO:** 1 PTO → 5 days off (5× return).
- **Alternative 5-day breaks** (same length, ranked by cost):
  1. Feb 14 weekend + Feb 16–18 Seollal + Feb 19 PTO (1 PTO,
     anchored on Seollal)
  2. May 1 PTO + May 2–3 weekend + May 4 PTO + May 5 Children's
     Day (2 PTO, anchored on Children's Day)
  3. Oct 3–4 weekend + Oct 5 PTO + Oct 6 PTO + Oct 7 PTO (3 PTO,
     no holiday anchor — a "pure" stretch)
  4. Aug 14 PTO + Aug 15 Liberation Day (Sat) + Aug 16 Sun + Aug 17
     sub-holiday + Aug 18 PTO (2 PTO, anchored on Liberation Day)

## Layout

**Hero header** (~220pt, edge-to-edge):

- Background: a soft peach-to-cream gradient, same hue family as the
  card that pushed into this screen.
- Top-left: back chevron (returns to Screen 5 with a shared-element
  transition).
- Top-right: share glyph (mock — opens system share sheet with a
  pre-filled string).
- Center: title "5-day break" 32pt semibold.
- Below title: date range "Wed Sep 23 — Sun Sep 27" 16pt secondary.
- Below date: a horizontal **day-by-day ribbon** of 5 colored blocks,
  full-width within the header. Each block has a small day-of-week
  label below (W T F S S) and a glyph above (PTO / Holiday / Weekend).
  This is a larger, more legible version of the mini ribbon on Screen
  5.

**ROI strip** (~52pt, just below header):

- Soft sage pill, centered: "**1 PTO** → **5 days off**" with a small
  arrow between. Tiny subline: "5× return on your time".

**Day list** (vertical, scrollable):

- Section header in caps, 12pt, 60% opacity: "Day by day".
- Five rows, ~72pt each, with a left color stripe matching the block
  color (sage / peach / neutral teal):
  - **Row composition:** Date stack on the left (day numeral + weekday
    caps), middle column shows the day type label ("PTO", "Holiday",
    "Weekend") in 16pt medium, and a 12pt secondary subline giving
    the holiday name where applicable. Right column: small glyph
    matching the type.
  - Holidays show the anchor string verbatim from the API:
    "Holiday — Chuseok", "Holiday — The day preceding Chuseok",
    "Holiday — The second day of Chuseok".
  - Multi-purpose days (e.g., a Saturday that is also a holiday) show
    both labels: "Weekend · The second day of Chuseok".
  - **Personal events on a day (calendar connected — Screen 9):**
    rendered as a sub-row indented under the day row, ~36pt tall.
    Left: 3pt color stripe in the calendar's color. Center: event
    title + time (e.g., "Team standup · 10:00–10:30"). Right: tiny
    "View" link (opens iOS Calendar app via deep link). Days with no
    events show no sub-row.

**Alternatives block:**

- Section header: "Other 5-day breaks" (12pt caps).
- A "Show alternatives" chevron button (collapsed by default).
- When expanded, shows a vertical list of 3–4 alternative cards in
  compact form. Each card has: length numeral + range, PTO cost pill
  (same color logic as Screen 5), anchor line. Tap → replaces the
  current break with that alternative (full screen rebuilds with new
  data, fade transition).

**Bottom action bar** (fixed, ~80pt):

- **Two-button row** when calendar is connected (Screen 9):
  - Primary "Save to my plan" (sage fill, ~60% width).
  - Secondary "Add to calendar" (outline, ~40% width) — writes a
    multi-day event to the user's default writable calendar via
    EventKit. On success, the button morphs to "✓ Added" with a
    small "Undo" link.
- **Single-button row** when calendar is not connected: primary
  "Save to my plan" only. Below it, a 12pt text link "Add to
  calendar — connect first" routes to Screen 9 with this break's
  context preserved so the user lands back here after connecting.
- The "Save to my plan" button morphs to "✓ Saved" on success in
  either layout (sage → peach accent, 60% → 40% width if in the
  two-button layout, plus an "Undo" link).

## Microcopy

- **Title:** "{n}-day break"
- **Date range:** "{weekday} {month} {day} — {weekday} {month} {day}"
- **ROI strip:** "**{n} PTO** → **{n} days off**" · "{n}× return on
  your time"
- **Day type labels:** "PTO", "Holiday", "Weekend"
- **Holiday subline pattern:** "{anchorString}"
- **Combined subline pattern:** "Weekend · {anchorString}"
- **Alternatives heading:** "Other {n}-day breaks"
- **Alternatives toggle:** "Show 4 more alternatives" / "Hide
  alternatives"
- **Save button:** "Save to my plan" → on success: "✓ Saved"
- **Undo link:** "Undo"
- **Share string (mock):** "I'm planning a 5-day Chuseok break in
  Korea: Sep 23–27 (1 PTO). Built with daysoff."

## States

- **Default** — Populated as in Sample data, alternatives collapsed.
- **Alternatives expanded** — Alt cards visible, toggle reads "Hide
  alternatives".
- **No alternatives** — Toggle disabled; replaced with helper text:
  "No other 5-day breaks within your budget."
- **Saved** — Save button morphs to "✓ Saved"; Undo link appears for
  10 seconds, then fades out. Saved breaks persist (mocked) until
  the user logs out or clears state.
- **Past break (year is over)** — Save button replaced with a calm
  badge: "This break has passed." Share still works.
- **Loading (deep link in)** — If user arrives via deep link rather
  than from Screen 5, the hero header shows a skeleton ribbon while
  the day list loads.

## Dark mode

Hero gradient flips to deep coral → near-black. Day-ribbon blocks
retain semantic colors but lose saturation by one stop. Left color
stripes on day-list rows stay vivid (they're the primary semantic
cue). Sage ROI pill becomes a 14% sage fill on near-black. The "✓
Saved" peach accent stays warm.

## Motion

- **Entry (from Screen 5):** shared-element transition — the active
  card on Screen 5 grows to fill the hero header (cubic, 380ms). The
  ROI strip slides in from below 180ms later. Day rows stagger in
  from below, 40ms apart.
- **Alternatives expand:** chevron rotates 180° (220ms), alt cards
  slide down with a 60ms stagger.
- **Save tap:** button shrinks to 56pt square as a sage spinner
  rotates; on confirm, scales up to a "✓ Saved" pill (380ms spring).
  Subtle confetti (3–4 tiny peach dots fade up + away over 600ms) —
  this is the one celebratory moment, kept understated.
- **Undo tap:** button morphs back to "Save to my plan" (240ms),
  confetti does not replay.
- **Alternative swap:** when user picks an alternative, the whole
  Day list crossfades (260ms) to the new break; hero ribbon rebuilds
  block-by-block (60ms stagger).

## Accessibility

- Hero ribbon: each block is announced as "Day {n} of {n}, {weekday},
  {dayType}{, anchor}". The ribbon as a whole is `aria-label`'d
  "Day-by-day composition".
- Day rows: each announces as a single phrase: "Wednesday September
  23rd, PTO, costs 1 day from your budget."
- Color is never the only cue: day type labels are spelled out;
  glyphs carry `aria-label`s; the left stripe is decorative.
- Save button has `aria-pressed` state when in "Saved" mode.
- Undo link disappears at 10s but is reachable by screen reader users
  via `aria-live` announcement: "Saved. Undo available for 10
  seconds."
- Alternatives toggle has `aria-expanded`.
- Share share-sheet text is pre-composed; screen reader announces
  what will be shared before opening the system sheet.
- Dynamic Type: hero title reflows from 32pt down to 24pt at largest
  size; day rows grow to accommodate two-line type subline.
- Reduced motion: shared-element transition becomes a 240ms fade;
  confetti disables; alternatives expand without slide stagger.
