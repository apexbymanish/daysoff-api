# Screen 5 — Plan tab — Length buffet

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

The hero surface of the Plan tab. Answers the second half of the value
proposition — *"which PTO days will give me the longest break for the
least cost?"* — by showing one card per break length (3 through 10
days). Each card is the **best break of that length** given the user's
budget and workweek. Cards are arranged horizontally and snap-scrolled,
so users can quickly compare "3-day break for 0 PTO" against "10-day
break for 4 PTO" with a thumb swipe. Tapping a card drills into Break
detail (Screen 6) for the day-by-day breakdown.

## Sample data (KR 2026, budget=15, workweek=Sat,Sun)

Eight cards, one per length:

- **3 days** — Oct 9 (Fri Hangul Day) + Oct 10–11 weekend · 0 PTO ·
  anchor: Hangul Day
- **4 days** — May 2–3 weekend + May 4 PTO + May 5 Children's Day ·
  1 PTO · anchor: Children's Day
- **5 days** — Sep 23 PTO + Sep 24–26 Chuseok + Sep 27 Sun · 1 PTO ·
  anchor: Chuseok
- **6 days** — Feb 14–15 weekend + Feb 16–18 Seollal + Feb 19 PTO ·
  1 PTO · anchor: Seollal
- **7 days** — Sep 22 PTO + Sep 23 PTO + Sep 24–26 Chuseok + Sep 27–28
  weekend (28 sub) · 2 PTO · anchor: Chuseok
- **8 days** — Feb 13 PTO + Feb 14–15 weekend + Feb 16–18 Seollal +
  Feb 19–20 PTO · 3 PTO · anchor: Seollal
- **9 days** — May 2–3 weekend + May 4 PTO + May 5 Children's Day +
  May 6–8 PTO + May 9–10 weekend · 4 PTO · anchor: Children's Day
- **10 days** — Sep 19–20 weekend + Sep 21–22 PTO + Sep 23 PTO + Sep
  24–26 Chuseok + Sep 27–28 (Sun + sub) · 3 PTO · anchor: Chuseok

Header stats: **Budget 15 PTO** · **8 breaks shown** · best value =
"5-day break for 1 PTO."

## Layout

**Top section** (~140pt fixed, above carousel):

- Title row: "Plan your year" 24pt semibold on the left, small
  edit-pencil icon on the right (opens budget/workweek/country quick-
  edit sheet).
- Chips row below title: `🇰🇷 KR` · `2026` · `Sat–Sun off` · `15 days`
  — all 4 chips tappable to edit inline. Subtle border, neutral fill.
- One-line "best value" headline: "Best value: 5-day break for 1 PTO"
  in 14pt with a small star glyph on the left. Tapping it scrolls the
  carousel to the 5-day card.

**Horizontal carousel** (center of screen, ~360pt tall):

- 8 cards in a horizontal snap-scroll. Each card is **78% of viewport
  width** with **12pt gaps**, so 1.2 cards are visible at once
  (encourages swipe discovery).
- **Card composition** (within each card):
  - Top-left: length label as a giant numeral, e.g., "**5 days**"
    (40pt semibold). Below it, range subhead: "Sep 23 – Sep 27"
    (14pt secondary).
  - Top-right: PTO cost pill: "1 PTO" — color varies by cost. **0 PTO
    → peach pill** (free wins), **1–2 PTO → sage pill**, **3+ PTO →
    neutral grey pill**.
  - Middle: small visual "ribbon" — a horizontal strip of 5 colored
    blocks (one per day in the break) showing day-by-day composition.
    Sage = PTO, peach = holiday, neutral teal = weekend. Tooltips
    appear under each block (e.g., "Wed: PTO").
  - Bottom: anchor block: "Anchored on **Chuseok**" with a tiny
    lantern glyph. Below that, a "tap for breakdown →" text link
    aligned right.
  - **Conflict indicator (only when calendar connected — Screen 9):**
    if any day in the break overlaps a personal event, a small
    warning-triangle glyph appears at the **top-right** of the card,
    next to the PTO pill, with a "2 events" caption. Cards without
    conflicts show no glyph. Tap reveals an inline 1-line list of
    the conflicting event titles before drilling to Break detail.
- Card background: cream by default; peach gradient when cost is
  0 PTO; sage tinge when ≤ 2 PTO; neutral when more — makes scanning
  visual.

**Pagination dots** below carousel (8 dots, sage = current).

**Stats strip** below dots (~64pt):

- 3 small cells side by side:
  - "Cheapest 5-day" → "1 PTO"
  - "Free breaks" → "1"
  - "Used budget" → "16 / 15" (or "Within budget" if total ≤ budget)
- Each cell is tappable to filter the carousel (e.g., show only free
  breaks).

**Bottom tab bar** as in Screen 3 (current tab = Plan).

## Microcopy

- **Page title:** "Plan your year"
- **Edit-chip labels:** "{country}" · "{year}" · "{workweek}" ·
  "{budget} days"
- **Best-value headline pattern:** "Best value: {n}-day break for {n}
  PTO"
- **Card length:** "{n} days"
- **Card range:** "{startMonth} {n} – {endMonth} {n}"
- **PTO pill:** "{n} PTO" (singular "1 PTO", plural "{n} PTO")
- **Anchor line:** "Anchored on **{holidayName}**"
- **Tap link:** "tap for breakdown →"
- **Stats labels:** "Cheapest 5-day" · "Free breaks" · "Used budget"
- **Empty state title:** "We can't suggest breaks with this budget."
- **Empty state body:** "Try increasing PTO budget or switching to a
  busier year."
- **Over-budget warning** (sticky banner at top): "Combined PTO across
  breaks exceeds your budget. These are independent options, not a
  plan."

## States

- **Default** — Populated, 8 cards, all chips reflecting saved
  preferences.
- **Loading** — Carousel shows 8 skeleton cards, stats strip shimmer.
- **Empty (no breaks possible)** — e.g., budget = 0. Hide carousel,
  show empty state card centered with a "Edit budget" CTA.
- **Over budget** — Banner above carousel (see microcopy). Stats strip
  still shows the total.
- **Year fully past** — Show empty state: "2026 is done. Switch to
  2027 to plan ahead."
- **Filtered (only free breaks)** — Carousel shows only 0-PTO cards;
  remaining 7-8 → 1-2 cards visible; remaining slots show a small
  "no other free breaks" card with a chevron back.
- **Workweek changed mid-session** — All cards re-compute with a 240ms
  shimmer; chip pulses to confirm.

## Dark mode

Card backgrounds drop saturation: cream becomes warm-charcoal, peach
gradient becomes a deep coral-to-navy fade, sage tinge becomes a 14%
sage fill on near-black. Day-ribbon blocks keep semantic colors but
shift one stop darker. Pagination dots: filled sage on near-black for
the current card, 24% white for inactive.

## Motion

- **Carousel snap:** snap-scroll with light spring (stiffness 200,
  damping 24). On settle, the active card scales from 96% → 100% over
  180ms; neighboring cards stay at 96%.
- **Day ribbon:** on initial card view, the 5 blocks "build in" one at
  a time, left-to-right, 60ms apart (subtle, almost incidental).
- **Best-value tap → scroll:** smooth scroll to the 5-day card,
  duration 520ms, ease-in-out. Star glyph pulses (240ms) on tap.
- **Card tap → Break detail (Screen 6):** shared-element transition —
  the active card grows to fill the screen as a hero header on Screen 6
  (cubic, 380ms).
- **Chip edit tap:** small bottom sheet rises (300ms) with the
  relevant control.
- **Filter change:** active filter cell on stats strip pulses (sage
  flash for 180ms), carousel updates with crossfade.

## Accessibility

- Carousel uses `role="region"` with `aria-label="Break length
  options"`; cards have `role="button"`.
- Each card announces: "5-day break, September 23rd through 27th,
  costs 1 PTO, anchored on Chuseok. Tap for day-by-day breakdown."
- Day ribbon: each block has `aria-label` ("Wednesday, PTO" /
  "Thursday, Chuseok" / etc.). The ribbon as a whole is `aria-
  describedby` from the card.
- Pagination dots are interactive (tap = jump to card N) and announce
  "Page 5 of 8".
- Star glyph on best-value headline is decorative; the headline text
  carries the semantic.
- All chips have ≥ 44pt vertical hit area even when visibly smaller.
- Dynamic Type: length numeral "5 days" reflows from 40pt to 28pt at
  largest accessibility size; card height grows to accommodate.
- Reduced motion: snap behavior persists; scale animations disable;
  hero transition becomes a 220ms fade.
- Color is never the only cue: PTO pills carry "PTO" text + the count;
  day-ribbon blocks carry tooltips/aria with semantics.
