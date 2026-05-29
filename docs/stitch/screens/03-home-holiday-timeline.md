# Screen 3 — Home / Holiday timeline

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

The default landing surface after onboarding (and on every cold launch
for a signed-in user). It answers the first half of the value
proposition — *"when are the holidays?"* — with a vertical, month-
grouped scrolling timeline of every red day for the selected country
and year. The user should be able to glance at this and immediately
see what's coming up and how many of the upcoming holidays land on
workdays (the "free day off" wins) versus weekends ("absorbed"). The
Plan tab is one tap away via the bottom tab bar.

## Sample data (KR 2026)

A representative subset of Korean public holidays for 2026 (the user's
**country of work**):

- **Feb 16–18 (Mon–Wed)** — Seollal / 설날 — weekdays · free
- **Mar 1 (Sun)** — Independence Movement Day / 삼일절 — weekend · absorbed
- **Mar 2 (Mon)** — Substitute holiday — weekday · free
- **May 5 (Tue)** — Children's Day / 어린이날 — weekday · free
- **May 24 (Sun)** — Buddha's Birthday / 부처님오신날 — weekend · absorbed
- **Jun 6 (Sat)** — Memorial Day / 현충일 — weekend · absorbed
- **Aug 15 (Sat)** — Liberation Day / 광복절 — weekend · absorbed
- **Sep 24–26 (Thu–Sat)** — Chuseok / 추석 — mostly weekdays · free
- **Oct 3 (Sat)** — National Foundation Day / 개천절 — weekend · absorbed
- **Oct 9 (Fri)** — Hangul Day / 한글날 — weekday · free
- **Dec 25 (Fri)** — Christmas / 크리스마스 — weekday · free

"Days until next holiday" banner at top: **17 days until Children's
Day** (assuming today is mid-April 2026).

**If the user set a country of residence** (e.g., NP for a Nepali expat
working in Korea), the timeline overlays the home country's holidays
with a distinct treatment. For the KR-work / NP-home case, additional
rows appear: **Dashain / दशैं** (Oct 12–20, 2026, 9 days) and **Tihar /
तिहार** (Nov 1–5, 2026, 5 days). These render with a dashed left edge
and a small house glyph instead of the sun/moon glyph used for work-
country holidays.

## Layout

**Sticky header** (60pt tall):

- Left: country chip showing flag + ISO code: `🇰🇷 KR`. Tap opens the
  country search sheet.
- Center: year stepper `◀  2026  ▶` with small chevrons.
- Right: filter icon (a horizontal sliders glyph) — opens a sheet with
  toggles like "Only free days" and "Hide past".

**Hero strip** (just below header, 80pt tall, dismissible):

- Soft peach-tinted card with: large numeral "17" on the left, label
  "days until" middle, holiday name "Children's Day" with date subline
  "Tue, May 5" on the right. Small chevron suggests it's tappable
  (opens the holiday detail sheet — Screen 4).

**Body — month-grouped scroll list.**

- Section header for each month: month name spelled out ("February"),
  18pt medium, left-aligned with a thin divider underneath.
- Each holiday row (~84pt tall):
  - **Left date stack** (~60pt wide): large day numeral (28pt semibold)
    above abbreviated weekday in caps (12pt secondary): `16 / MON`. For
    multi-day holidays like Seollal, show a range stack: `16–18 / MON–
    WED` in slightly smaller type.
  - **Middle column:** holiday name in English (16pt medium), with
    `한글` subhead one line below in 12pt secondary. For multi-day
    holidays, append " (3 days)" to the name.
  - **Right column:** small monoline status glyph + label. Free
    weekday → peach sun glyph + "free" in 11pt. Absorbed weekend →
    muted grey moon-on-circle + "absorbed" in 11pt.
- Faint hairline divider between rows.

**Bottom tab bar** (standard iOS/Android pattern, ~56pt):

- Tabs: **Holidays** (current, sage fill) · **Plan** · **Sandwich** ·
  **Settings**. Icons are monoline; selected tab gets the sage fill +
  full label, unselected tabs show icon only.

**FAB** (optional, bottom-right above tab bar): peach circular button
with a small "+" → quick action to "Plan a break around the next
holiday" (jumps to Plan tab pre-filtered).

**Calendar events overlay (when connected — see Screen 9).** When the
user has connected Apple Calendar, personal events render as a third
row type within the same month-grouped list:

- A small (~28pt tall) event row appears tucked underneath the
  relevant holiday row (or as its own row if no holiday that day).
- Left margin shows a 4pt vertical stripe in the calendar's color
  (e.g., blue for "Personal", green for "Work — Naver").
- Body line: event title in 13pt medium, time range in 11pt
  secondary (e.g., "Dentist · 10:00–10:45").
- Right side: tiny conflict glyph (a soft warning triangle) if the
  event overlaps a free-day holiday — taps open the holiday detail
  sheet (Screen 4) with the event listed under "Your calendar".
- Past events are not shown (filtered at read time).

**Connect-calendar banner (when not yet connected).** Sage-tinted
card pinned just below the hero strip (dismissible): "See your
events alongside holidays" with a small "Connect" pill button on the
right. Tap routes to Screen 9. Dismiss hides it for 7 days.

## Microcopy

- **Page title (screen-reader only):** "Days off in Korea, 2026"
- **Hero strip:** "{n} days until {holidayName}"
- **Section headers:** "February", "March", "April", … (always full
  names, never abbreviations)
- **Status labels:** "free" / "absorbed" (lowercase, no period)
- **Multi-day suffix:** " (3 days)"
- **Filter sheet labels:** "Show past holidays", "Only free days",
  "Group by quarter", "Show home holidays" (only visible when a
  country of residence is set; on by default)
- **Empty state title:** "No more holidays this year."
- **Empty state body:** "Switch to 2027 to plan ahead."
- **Loading skeleton:** show 6 placeholder rows under a placeholder
  month header — no text, just shimmer.

## States

- **Default** — populated with the sample data, hero strip showing next
  holiday, no filters applied.
- **Filtered (only free)** — absorbed-weekend rows hidden; section
  headers without surviving rows collapse.
- **Home holidays visible** — rows from the user's country of
  residence are interleaved into the same month sections, rendered
  with a **dashed left edge** (1.5pt sage) and a tiny house glyph
  instead of the work-country sun/moon glyph. Holiday name still
  shows in EN + local script (e.g., "Dashain / दशैं"). These rows
  are **not** tappable for "Plan around this" — only work-country
  rows are, since planning is driven by the work country. Tapping a
  home row still opens the holiday detail sheet (Screen 4) with a
  "Home" badge and no primary CTA.
- **Calendar connected** — Connect-calendar banner hidden. Personal
  events render as the third row type described in Layout. Events
  filter to the currently selected calendars (see Screen 9). A small
  calendar-status chip appears next to the country chip in the
  header showing "3 calendars" — tap routes to Screen 9 for
  reconfiguration.
- **Calendar not connected** — Connect-calendar banner visible
  (unless dismissed within the last 7 days). No event rows render.
- **Empty (past year)** — Once the year is fully past, hide the body
  list, show the empty state card centered. Year stepper still works.
- **Loading** — Skeleton header (no country chip until loaded), 6
  shimmer rows under a shimmer section header.
- **Error** — Banner above body: "Couldn't refresh holidays. Showing
  cached data from {timestamp}." Retry icon on the right.
- **Past holiday rows** — Rendered with 40% opacity if "Show past
  holidays" filter is on; otherwise hidden.

## Dark mode

Background near-black (#0B0D0E). Section dividers at 8% white. Date
numerals stay warm-cream. Free-day peach glyph keeps full saturation;
absorbed-weekend moon glyph drops to 30% opacity to recede further.
Hero strip uses a deep teal fill with peach numeral.

## Motion

- **Sticky header parallax:** the year stepper rises 4pt and shrinks
  type by 1pt as the user scrolls past 80pt; reverses on scroll up.
- **Hero strip dismiss:** swipe right to dismiss (rubber-band, 280ms);
  re-appears the next day or after a fresh launch.
- **Row tap → holiday detail sheet (Screen 4):** card pushes down 6pt
  and a sheet rises from the bottom (cubic-bezier(0.32, 0.72, 0, 1),
  360ms).
- **Filter sheet:** half-height bottom sheet, drag-to-dismiss.
- **Year stepper tap:** the entire scroll list crossfades to the new
  year (180ms); the section header for the current month subtly
  pulses (scale 100% → 102% → 100% over 240ms) to orient the user.
- **Pull to refresh:** standard iOS/Android pattern; spinner uses sage.

## Accessibility

- Each holiday row announces as a single phrase: "Chuseok, September
  24th through 26th, three days, weekday, free day off."
- Year stepper announces as a stepper: "Year, 2026, adjust value with
  swipe up or down".
- Tap targets: full row is tappable (≥ 84pt vertical hit area); the
  date stack alone is also tappable to open the detail sheet (no
  separate target).
- Status glyphs include `aria-label` ("free day off" / "absorbed by
  weekend") — color is not the only cue.
- Dynamic Type: date numerals reflow from 28pt down to 22pt at
  largest accessibility size; the row height grows to accommodate.
- Section headers are real headings (`<h2>` semantics) so screen
  reader users can navigate by heading.
- Reduced-motion: dismiss replaces the spring with a 180ms linear
  fade; sticky-header parallax disables.
