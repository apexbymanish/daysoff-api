# Screen 7 — Sandwich tab

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

A dedicated tab that surfaces "sandwich days" — single workdays wedged
between off-days where one PTO day yields an outsized return (3–4 day
break for 1 PTO). The user lives here when they want to *opportunistic*
ally claim cheap wins without doing the full Plan-tab decision. Each
card is a single-day suggestion with a clear "save this day" mock action
that triggers a (future) reminder. Visually echoes Home (Screen 3) — same
vertical timeline shape — so users feel oriented; but each card carries a
trade ("take this 1 day → get 4 days off") rather than just a date.

## Sample data (KR 2026, workweek = Sat,Sun)

Sandwich candidates for the rest of 2026 (mid-April onward):

- **Mon, May 4** — wedged between May 2–3 weekend and May 5 Children's
  Day. Take 1 PTO → 4-day break (May 2–5).
- **Mon, Mar 2** (already past — hidden by default) — Mar 1 Sun + Mar 2
  workday + Mar 3 Children's substitute. Past, hidden.
- **Fri, Aug 14** — Aug 14 workday + Aug 15 Sat Liberation Day + Aug 16
  Sun + Aug 17 Mon substitute. Take 1 PTO → 4-day break (Aug 14–17).
- **Mon, Sep 28** — Sep 26 Sat (Chuseok day 3) + Sep 27 Sun + Sep 28
  workday + Sep 29 workday. Take 1 PTO on Mon → 3-day break (Sep
  26–28). Lower value (3 days, 1 PTO) so it sits lower in the list.
- **Thu, Oct 8** — Oct 9 Fri Hangul Day + Oct 10–11 weekend. Take 1
  PTO on Thu → 4-day break (Oct 8–11).
- **Thu, Dec 24** — Dec 25 Fri Christmas + Dec 26–27 weekend. Take 1
  PTO on Thu → 4-day break (Dec 24–27).

Sort default: **best value first** (4-day breaks before 3-day breaks).
Header stats: **5 sandwich days available** · best = "Take May 4 off →
4-day break for 1 PTO."

## Layout

**Sticky header** (~80pt) — same shape as Home (Screen 3):

- Left: country chip `🇰🇷 KR`.
- Center: year stepper `◀  2026  ▶`.
- Right: sort filter icon (tapping opens a half-sheet with "Cheapest
  first" / "Earliest first" toggles).

**Highlight banner** (just below header, dismissible):

- Soft peach-tinted card: large numeral "4" on the left, "days off
  from 1 PTO" middle, dates "May 2–5" on the right. Tap → opens Break
  detail (Screen 6) anchored on this sandwich.

**Body — vertical timeline:**

- Section header per month (same as Home).
- Each sandwich row (~96pt, slightly taller than Home rows):
  - **Left date stack** (~64pt wide): large day numeral (28pt
    semibold), weekday in caps (12pt). E.g., "04 / MON".
  - **Middle column:** primary line "Take this 1 day → **4-day
    break**" in 15pt medium; subline "wedged between **weekend** and
    **Children's Day**" in 12pt secondary. Hover/press shows a small
    inline ribbon (4 colored blocks) below the subline.
  - **Right column:** save action — a pill button "**Save**" with a
    bookmark glyph. After tap, morphs to "**✓ Saved**" with sage
    fill; subline appears: "Reminder for Apr 27" (one week before).
- Faint divider between rows.
- Past-row rendering: 40% opacity if "Show past" filter is on;
  otherwise hidden (so the user only sees future opportunities).

**Bottom tab bar** as in Screen 3 (current tab = Sandwich).

## Microcopy

- **Page title (screen-reader only):** "Sandwich days in Korea, 2026"
- **Highlight banner:** "{n} days off from 1 PTO" · "{startMonth} {n}
  – {endMonth} {n}"
- **Row primary:** "Take this 1 day → **{n}-day break**"
- **Row subline pattern:** "wedged between **{leftAnchor}** and
  **{rightAnchor}**" where each anchor is "weekend", "Children's
  Day", "Liberation Day", etc. — never a raw date.
- **Save action:** "Save" → on success: "✓ Saved" + "Reminder for
  {date}" (one week before the sandwich)
- **Sort sheet labels:** "Cheapest first" · "Earliest first" ·
  "Highest value first" (default)
- **Empty state title:** "No more sandwich days in 2026."
- **Empty state body:** "Switch to 2027 to find next year's wins."
- **Empty (year fully past) variant:** "2026 is done — you couldn't
  have squeezed more out of it."

## States

- **Default** — Populated, future-only, highest-value first.
- **Filtered by sort** — Reorders smoothly.
- **All past** — Empty state.
- **Loading** — Same skeleton pattern as Home: shimmer rows under a
  shimmer month header, 5 rows.
- **No internet** — Banner above body: "Couldn't refresh. Showing
  cached sandwich days." Retry icon on the right.
- **Save → reminder set** — Inline confirmation; reminder text appears
  below the row. (Note: the reminder is mocked; v1 doesn't send push
  notifications per master prompt's non-goals.)
- **Save undo** — Tapping "✓ Saved" within 4 seconds collapses back
  to "Save" with a soft toast at the bottom: "Reminder removed."

## Dark mode

Background near-black. Highlight banner uses deep teal fill with peach
numeral. Row dividers at 8% white. Save pill: outline-only in dark
mode for "Save", sage-filled for "Saved". The 40%-opacity past rows
become 32% opacity so they don't disappear entirely.

## Motion

- **Sticky header parallax:** same behavior as Home — year stepper
  rises 4pt on scroll, reverses on scroll up.
- **Highlight banner dismiss:** swipe right (rubber-band, 280ms).
  Returns on next year-step or tab-switch.
- **Save tap:** pill collapses to spinner (180ms) → springs out to
  "✓ Saved" (380ms spring). Reminder subline fades in 120ms later.
- **Save undo:** soft toast slides up from bottom (240ms), auto-
  dismisses after 3s.
- **Sort change:** rows perform a brief crossfade as they reorder
  (240ms); section headers re-pin if needed.
- **Row tap → Break detail (Screen 6):** card pushes down 6pt, then
  a sheet rises to fullscreen with the same shared-element pattern
  as Plan → Break detail.
- **No bouncy confetti** on save — keep this surface calm, since the
  user might save many in a row.

## Accessibility

- Each row announces as a single phrase: "Monday May 4th. Take 1 PTO
  day for a 4-day break, wedged between the weekend and Children's
  Day. Save button."
- Save button has `aria-pressed` state; after save: "Saved. Reminder
  set for April 27."
- Highlight banner is a single tappable region announced as: "Best
  sandwich: take May 4 off for a 4-day break, May 2 through 5."
- Sort filter announces current selection: "Sort, currently highest
  value first."
- Color is not the only cue: "Saved" pill has both color and check
  glyph.
- Dynamic Type: row primary text reflows from 15pt up to 20pt; the
  row height grows; ribbon stays inline.
- Reduced motion: parallax disables; save spring becomes a 200ms
  linear morph; reorder uses linear fades.
- Past rows (if shown) carry `aria-disabled="true"`; their save
  action is unavailable and screen reader announces "Past — save
  unavailable".
