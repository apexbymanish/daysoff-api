# Screen 1 — Onboarding

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

The first thing every user sees. Four full-screen cards swiped horizontally
(or advanced via a "Next" button on the bottom-right). The job: get the
user signed in and capture the three preferences the rest of the app
needs (country, workweek, PTO budget). Tone is welcoming and concrete —
never marketing. By the end of card 4 the user lands on Home with a fully
populated holiday timeline. Cards 3–4 each show a small "Use defaults"
link in the top-right; card 2 has no skip — auth is required. Skipping
cards 3–4 falls back to locale-detected defaults.

## Sample data (KR 2026)

- Detected locale: `ko-KR` → **country of work** defaults to **South
  Korea**, workweek defaults to **Sat, Sun**.
- **Country of residence:** optional, left blank in the default flow.
  Example expat case to mock for one variant: a Nepali working in
  Korea sets work → KR and residence → NP, so Dashain shows alongside
  Chuseok on Home.
- Suggested PTO budget: **15 days** (Korea's statutory annual leave average).
- Anchor preview holidays shown subtly in card 4: Seollal (Feb 16–18, 2026),
  Children's Day (May 5), Chuseok (Sep 24–26).
- Auth providers visible on card 2: Email + password, Continue with Google,
  Continue with Apple.

## Layout

**Card 1 — Welcome.** Full-bleed warm gradient (deep teal → peach at the
bottom edge). Centered logotype "daysoff" in a soft serif at the top
third. Below it, one calm sentence in 22pt regular: "Find the longest
break for the fewest days off." Below that, in 14pt secondary text:
"Built for 연차, बिदा, 有給休暇, and every other word for it." Two stacked
buttons near the bottom: primary "Get started" (filled, sage-green
accent), secondary text link "I already have an account" (no border,
brand teal).

**Card 2 — Sign up / Sign in.** Top-left back chevron, top-right segmented
toggle: `[ Sign up | Sign in ]`. Below the toggle: two social buttons
stacked full-width with monoline provider marks — "Continue with Google",
"Continue with Apple". Subtle horizontal divider with "or" centered. Two
text fields: Email, Password (password has a show/hide eye icon on the
right edge). Field labels float above when focused. Below the fields:
primary button "Create account" (or "Sign in" when toggle is on the
right side). Tiny helper text under the button: "By continuing you agree
to the Terms and Privacy Policy." Sign-in side adds a "Forgot password?"
link aligned to the right of the password field.

**Card 3 — Country & workweek.** Top-center: small "Step 3 of 4" pip
indicator. Question header in 24pt: "Where do you work?" Below: a chunky
country selector — a tile showing the detected country's flag + name +
ISO code (e.g., "🇰🇷  South Korea · KR") with a chevron to change.
Tapping it opens a bottom-sheet country search (250+ countries).
Directly under the picker, a small text link in brand teal: "I live
somewhere else" — tapping it reveals a second, slightly smaller country
tile beneath the first labeled "Country of residence (optional)" with
the same picker behavior, plus a "Remove" affordance once a value is
set. Most users skip this; expat/remote-work users get the value.
Below the country block: question subhead "Which days are your
weekend?" with seven day pills in a 7-column grid (M T W T F S S).
Pre-selected: Sat and Sun (sage-green fill); unselected pills are
neutral gray. Selection is multi-toggle (any subset valid). The
workweek is always tied to the **country of work**, never the
residence. Helper text below grid: "Nepali users: weekends moved to
Sat/Sun in April 2026."

**Card 4 — PTO budget.** Header: "How many days can you take this year?"
Centered numeric display in 72pt (e.g., "15 days") that updates live with
the slider. Slider underneath, range 3–25, default 15, sage-green track
with a peach handle. Tick marks at 5, 10, 15, 20, 25 with small numerals
beneath. Below the slider, a soft preview card titled "What you could do
with 15 days" listing 3 invented teaser results: "5-day Chuseok break
(1 PTO)", "10-day Seollal trip (4 PTO)", "9-day Children's Day window
(3 PTO)" — each with a tiny calendar glyph. Primary button at the bottom:
"Start planning →".

## Microcopy

- **Card 1 primary CTA:** "Get started"
- **Card 1 secondary link:** "I already have an account"
- **Card 2 toggle labels:** "Sign up" / "Sign in" (Korean: 회원가입 / 로그인
  when locale is `ko-KR`)
- **Card 2 social buttons:** "Continue with Google" · "Continue with Apple"
- **Card 2 primary CTA:** "Create account" / "Sign in"
- **Card 2 footer:** "By continuing you agree to the Terms and Privacy
  Policy."
- **Card 2 errors:** "We don't recognize that email." · "Password needs
  at least 8 characters." · "Check your connection and try again."
- **Card 3 headers:** "Where do you work?" · "Which days are your weekend?"
- **Card 3 helper:** "We use this to mark red days and weekends correctly."
- **Card 3 residence link:** "I live somewhere else"
- **Card 3 residence sub-label:** "Country of residence (optional)"
- **Card 3 residence helper:** "We'll show your home country's
  holidays on the timeline too."
- **Card 4 header:** "How many days can you take this year?"
- **Card 4 helper under slider:** "You can change this anytime in Settings."
- **Card 4 CTA:** "Start planning"
- **Skip links (cards 3–4):** "Use defaults" (not "Skip" — feels more
  confident)

## States

- **Default** — populated as in Sample data. Korean locale auto-detected,
  Sat/Sun preselected, slider at 15.
- **Empty** — N/A (this is the entry surface; nothing to be empty).
- **Loading (auth submit)** — Card 2 primary button collapses width and
  shows a small centered spinner; fields lock; toggle disables.
- **Auth error** — Inline red helper text under the affected field;
  primary button stays enabled to retry. Generic banner only for network
  errors.
- **Country search loading** — Bottom sheet shows 8 skeleton rows; search
  input remains active.
- **Returning user** — If a session token is found on launch, skip
  straight to Home; never show cards 1–4 again. Cards 3–4 remain
  reachable from Settings.

## Dark mode

Card 1 gradient flips to deep navy → muted brick (very low saturation).
Logotype goes warm-white (#F4ECD8) instead of pure white. Sage-green CTA
shifts one stop darker; peach accent stays as the highlight. Text fields
use a 1px stroke at 12% white instead of fills. Slider track on Card 4
stays sage but the unfilled portion sits at 8% white. The overall feel
should mirror Apple Calendar's dark mode — nearly black, with the accent
popping.

## Motion

- **Card transitions:** horizontal swipe, 320ms spring (stiffness 220,
  damping 26). Pip indicator on Card 3+4 fills as the user advances.
- **Slider on Card 4:** the 72pt number above the slider runs a 120ms
  tween between integer values; if the user drags fast, the preview list
  crossfades (180ms) when the budget bucket crosses a threshold
  (5/10/15/20).
- **Auth submit:** button width collapses to 56px square as it spins,
  then expands back on response. On success, a 220ms fade-out moves to
  the next card.
- **Country selection:** tapping the country tile slides a sheet up from
  the bottom (cubic-bezier(0.32, 0.72, 0, 1), 360ms).
- **No bouncy splash** on entry — fade master logotype in over 240ms.

## Accessibility

- All tap targets ≥ 44×44pt; day-pill grid on Card 3 uses 48pt squares
  to avoid mis-taps.
- Field labels announce on focus (`aria-label` / VoiceOver hint);
  password show/hide announces state ("Password hidden" / "Password
  visible").
- Slider on Card 4 supports both drag and discrete left/right keyboard
  nudges (1-day step, 5-day shift+step). Announce as "PTO budget,
  15 days, slider, 3 to 25".
- Color is never the only cue: selected day pills also carry a check
  glyph; auth errors carry an icon, not just red text.
- Dynamic Type: the 72pt budget number reflows down to 56pt at largest
  accessibility size; layout never clips.
- Contrast: body text ≥ 4.5:1 against background in both modes;
  secondary text ≥ 3:1.
