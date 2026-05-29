# Master Prompt — daysoff Mobile App (for Google Stitch)

> Paste this file **first** in every Stitch session. Then paste a screen
> file from `screens/` as a follow-up message to generate that screen.

---

## Prompt

Design a mobile app called **daysoff** for office workers in Asia who want
to maximize their paid time off (PTO) by combining it cleverly with public
holidays.

**Who it's for.** Salaried employees in South Korea, Nepal, Japan, India,
and the Philippines. They get 10–20 PTO days a year and want to know:
*"When are the holidays, and which PTO days will give me the longest break
for the least cost?"*

**Core value proposition.** Two answers, instantly:

1. **Holiday calendar** — every official red day in their country for the
   selected year, including newly-announced temporary holidays
   (e.g., Korea sometimes announces extra red days mid-year).
2. **Smart PTO suggestions** — given a PTO budget (say 15 days), show the
   best ways to chain PTO with holidays + weekends for long breaks.

**Three primary user flows.**

1. **Browse holidays.** User picks a country + year, sees a vertical
   timeline of red days grouped by month. Each card shows the date, day
   of week, holiday name (in English + local script when relevant, e.g.,
   "Chuseok / 추석"), and a small icon showing if it falls on a weekend
   ("absorbed" — sad face) or a weekday ("free day off" — happy face).

2. **Plan a vacation.** User sets PTO budget with a slider (3–25 days)
   and sees a "length buffet" — best break of each length from 3 to 10
   days. Each break card shows: start–end dates, total length, how many
   PTO days it costs, and the holiday(s) it's anchored to. Tap a card
   to drill down: see the day-by-day breakdown (which days are PTO,
   which are weekend, which are holiday), and view alternative
   same-length breaks ranked by cheapest PTO cost.

3. **Sandwich-day detector.** Show single workdays wedged between
   off-days (e.g., "Tuesday between Memorial Day Monday and the
   weekend"). One-tap "save this PTO day" mock action that triggers
   a future reminder.

**Visual style direction.**

- Warm, calm, optimistic — this is a tool that helps people rest. Not
  corporate, not enterprise.
- Reference points: Headspace's calm gradients, Linear's information
  density, Apple Calendar's date typography, Things 3's clean lists.
- Primary palette: deep teal or soft indigo for the brand, with warm
  accent (peach or sand) for "free days." Off-days/PTO get a muted
  sage green, workdays get neutral gray. Holiday names get a touch of
  the local culture (e.g., Korean Hangul gets a subtle traditional
  red/blue accent without being kitsch).
- Date-heavy UI — use large numerals and full weekday labels. Months
  are spelled out, not abbreviated, when space allows.
- Avoid emoji-as-icons in primary UI (use them sparingly for tone in
  empty states or onboarding). Use a clean monoline icon set.
- Light + dark mode. Dark mode should feel like Apple Calendar's dark
  mode — nearly black, with the accent color popping.

**Tone of microcopy.**

- Encouraging and concrete. "Take Fri 9/25 off → get a 5-day break"
  beats "Save 4 days by taking PTO on these dates."
- No marketing fluff. No exclamation marks. Treat the user like a
  busy adult.
- Locale-aware: Korean users see "PTO" labeled as "연차," Nepali users
  see "बिदा," Japanese users see "有給休暇." English label always
  available alongside. Auth labels follow the same rule: Korean
  users see "로그인" / "회원가입" alongside "Sign in" / "Sign up."

**Hard requirements.**

- **Account required.** Users sign up (or sign in) before the app is
  usable. Preferences (country, workweek, budget) are tied to the
  account and sync across devices. Auth supports email + password
  and social sign-in (Google, Apple).
- **Country of work** drives planning — the holidays that grant the
  user free days come from this country, and the workweek picker
  defaults from it. The country picker must include at minimum: KR
  (South Korea), NP (Nepal), JP (Japan), IN (India), PH (Philippines),
  with a search box for the long tail (250+ countries supported).
- **Country of residence** is optional and informational. If set,
  Home shows the user's home-country holidays as a secondary overlay
  (different visual treatment, not counted toward PTO planning).
  Common case: expat/remote workers whose employer is in a different
  country than where they live.
- The plan screen must show a workweek selector — most users are Mon–Fri
  off Sat/Sun, but Nepal recently moved from a 1-day to a 2-day weekend,
  and some Middle Eastern users are off Fri/Sat. Default per country,
  but always overridable.

- **Optional calendar integration (Apple Calendar via EventKit).**
  The app reads the user's calendar to show personal events alongside
  holidays on Home, warns about conflicts when planning breaks, and
  writes saved breaks back as multi-day events. Permission is
  deferred + optional — the app works fully without it. The integration
  is configured on Screen 9 (Connect calendar) and managed in Settings.

**Non-goals (v1).**

- No social features, no sharing, no team/manager view, no push
  notifications, no in-app purchases. All of that is v2+.

---

## API surface available (for Stitch reference)

The mobile app talks to a public read-only API. Here's what's exposed:

```
GET /v1/healthz                  liveness probe
GET /v1/countries                250+ ISO-2 codes, news-enrichment flag
GET /v1/holidays?country=KR&year=2026
GET /v1/compare?countries=KR,NP&year=2026
GET /v1/sandwiches?country=KR&year=2026&workweek=sat,sun
GET /v1/plan?country=KR&year=2026&budget=15&min_length=3&max_length=10
```

`/v1/plan` is the workhorse for the Plan tab. `/v1/holidays` and
`/v1/sandwiches` feed Home and Sandwich tabs.

> **Note on auth.** The backend is currently public (no auth tokens
> required). Adding bearer-token auth is a follow-up backend task; for
> design purposes, assume the auth tier exists.

Sample `/v1/plan` response (one length, top-1):

```json
{
  "country": "KR",
  "year": 2026,
  "budget": 15,
  "workweek": ["sat", "sun"],
  "workweek_source": "user",
  "results_by_length": {
    "5": [{
      "break_start": "2026-09-23",
      "break_end": "2026-09-27",
      "break_length": 5,
      "pto_dates": ["2026-09-23"],
      "pto_cost": 1,
      "anchors": ["The day preceding Chuseok", "Chuseok",
                  "The second day of Chuseok"]
    }]
  }
}
```

Use this shape to populate the Plan tab and Break detail screens with
realistic data, not placeholder text.
