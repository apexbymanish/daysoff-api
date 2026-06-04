# Screen 9 — Connect calendar

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

The first-time calendar integration flow and the source of truth for
calendar settings. Reached via three entry points: (1) the "Connect
your calendar" banner that appears on Home a day or two after first
launch, (2) Settings → Calendar → "Connect", and (3) tapping "Add to
calendar" on Break detail (Screen 6) when the app isn't yet connected.
The screen has two phases — explain + ask permission, then pick which
calendars to read — and returns the user to wherever they came from
once finished. Permission is **deferred + optional**: the app works
fully without calendar access, and the user never sees this screen
unless they choose to.

## Sample data (KR 2026)

- User's available calendars after permission is granted:
  - **Personal** (iCloud) — blue dot
  - **Work — Naver** — green dot
  - **Family — Shared iCloud** — red dot
- Pre-selected: **Personal** and **Work** (Family is unchecked by
  default to avoid surfacing kids' soccer practice on a planning
  screen — user can opt in).
- Example events that will appear on Home once connected:
  - "Dentist · Tue May 12, 10:00–10:45"
  - "Quarterly review · Wed Aug 5, 14:00–15:00"
  - "Annual physical · Mon Oct 5, 09:00–09:30"

## Layout

**Phase A — Permission prompt** (mounted on entry):

- Top-left back chevron (returns to the calling surface — Home banner
  / Settings / Break detail).
- Centered illustration (~96pt): a calendar page with two soft peach
  highlight bands and a small monoline holiday glyph in the corner.
  Calm, not playful.
- Title 28pt semibold: "See your events with your holidays".
- Body 14pt regular, 60% opacity, max-width 320pt: "daysoff reads
  your calendar to show events alongside red days on Home, and writes
  saved breaks back as multi-day events. Your data stays on your
  device."
- Three short value bullets stacked, each with a small sage check
  glyph on the left:
  - "Spot conflicts when planning breaks"
  - "Add saved breaks with one tap"
  - "Disconnect anytime in Settings"
- Two stacked buttons near the bottom:
  - Primary "Connect" (sage fill) — triggers the iOS EventKit
    permission system prompt.
  - Secondary text "Not now" (returns to caller; remembers the
    decline and won't re-prompt for 7 days).

**Phase B — Calendar picker** (after permission granted):

- Top-left back chevron (now disabled — user must complete or tap
  Done); top-right "Done" link in brand teal.
- Title 24pt semibold: "Which calendars should we read?".
- Body 13pt secondary: "We'll show events from these calendars on
  Home and warn about conflicts when planning. You can change this
  any time."
- "Select all · Clear all" small text links aligned right above
  the list.
- List of available calendars, ~56pt per row:
  - Left: 10pt color dot matching the calendar's color in iOS
    Calendar.
  - Center: calendar name in 16pt medium, source in 12pt secondary
    on the line below (e.g., "Personal" / "iCloud").
  - Right: large checkbox (sage fill when checked, neutral outline
    when not).
- Tip strip near the bottom, in a soft cream pill: "Hidden calendars
  are still searched when you tap 'Add to calendar' on a break."
- Primary button "Done" at the very bottom (sage fill) — returns to
  caller.

## Microcopy

- **Phase A title:** "See your events with your holidays"
- **Phase A body:** "daysoff reads your calendar to show events
  alongside red days on Home, and writes saved breaks back as
  multi-day events. Your data stays on your device."
- **Phase A bullets:** "Spot conflicts when planning breaks" · "Add
  saved breaks with one tap" · "Disconnect anytime in Settings"
- **Phase A primary:** "Connect"
- **Phase A secondary:** "Not now"
- **Permission-denied state:** "Calendar access is off. Turn it on
  in iOS Settings → Privacy & Security → Calendars → daysoff." Inline
  link "Open Settings" deep-links via `app-settings:`.
- **Phase B title:** "Which calendars should we read?"
- **Phase B body:** "We'll show events from these calendars on Home
  and warn about conflicts when planning. You can change this any
  time."
- **Phase B select/clear:** "Select all" · "Clear all"
- **Phase B tip:** "Hidden calendars are still searched when you tap
  'Add to calendar' on a break."
- **Phase B CTA:** "Done"
- **Empty calendars state:** "No calendars found. Add one in your iOS
  Calendar app, then come back."
- **All-unchecked warning:** "Nothing will appear on Home until you
  tick at least one calendar. (Saving breaks to your default calendar
  still works.)"

## States

- **Default (Phase A)** — illustration + value bullets + Connect /
  Not now buttons.
- **Permission granted** — Phase A crossfades to Phase B (320ms).
- **Permission denied** — Phase A replaces buttons with a calm
  helper: "Calendar access is off. Open Settings to turn it on." +
  "Maybe later" text link.
- **"Not now" tapped** — returns to caller, sets a 7-day quiet flag
  so banners on Home suppress.
- **Phase B default** — list populated, Personal + Work pre-selected,
  Family unchecked.
- **Phase B no calendars** — empty state with the helper above.
- **Phase B all unchecked** — small warning helper appears above the
  Done button.
- **Already connected (re-entry from Settings)** — skip Phase A
  entirely; mount directly into Phase B with current selections
  pre-loaded.

## Dark mode

Standard dark — background near-black (#0B0D0E). Illustration peach
bands keep saturation. Sage CTA shifts one stop darker. Color dots on
the calendar list **retain full saturation** — they're the user's
authentic calendar colors and must stay recognizable. The cream tip
pill becomes a 12% warm-grey fill.

## Motion

- **Phase A → Phase B:** crossfade 320ms; the title 28pt → 24pt size
  shift uses the same 320ms window.
- **iOS permission prompt:** native system overlay, not part of this
  design — when it dismisses, Phase B animates in.
- **Phase B mount:** calendar list rows stagger-fade in, 40ms apart
  (subtle, not theatrical).
- **Checkbox tap:** scale 92% → 100% over 120ms, sage fill animates
  from outline (180ms).
- **Done tap:** button collapses to a sage spinner during EventKit
  read, then dismisses the screen (slide-down, 280ms).
- **Reduced motion:** all transitions become 180ms linear; stagger
  disables.

## Accessibility

- Permission illustration is `aria-hidden`; the title carries the
  semantic content.
- Connect button announces: "Connect to calendar, button. Opens iOS
  permission prompt."
- Value bullets are read as a list (not three separate sentences).
- "Open Settings" link announces destination clearly.
- Phase B list uses `role="group"` with `aria-label="Calendars to
  read"`; each row is a `checkbox` with state announced.
- "Select all" / "Clear all" are buttons with appropriate aria-labels.
- Tip pill is a static helper — announced after the list.
- VoiceOver focus on Phase B lands on the title, then "Select all"
  link, then the first calendar row.
- Dynamic Type: list rows grow vertically to accommodate larger text;
  color dots keep their fixed 10pt size for color recognition.
- Color is never the sole signal: checkbox state is also indicated
  by a check glyph; the dot is a label, not a status cue.
