# daysoff — Stitch prompt pack

A structured pack of prompts for designing the daysoff mobile app
in **Google Stitch** (https://stitch.withgoogle.com/).

## How to use

Stitch generates one screen per conversation turn and handles
~6–8 screens well per session. The pack is split so you can paste
the master prompt once and then issue each screen as a follow-up.

```
1. Paste master.md             → establishes app context, style, tone
2. Paste screens/01-...        → Stitch generates Screen 1
3. Paste screens/02-...        → Stitch generates Screen 2
...etc
```

Screens are numbered in the recommended generation order. Onboarding
first sets the visual vocabulary; the rest reuse it.

## Layout

```
docs/stitch/
├── README.md                          ← you are here
├── master.md                          ← paste first, every session
└── screens/
    ├── 01-onboarding.md               4-card flow (welcome, auth,
    │                                   country+workweek, budget)
    ├── 02-forgot-password.md          out-of-flow auth recovery
    ├── 03-home-holiday-timeline.md    default landing surface
    ├── 04-holiday-detail-sheet.md     bottom-sheet on tap
    ├── 05-plan-length-buffet.md       horizontal carousel of breaks
    ├── 06-break-detail.md             drill-down from a break card
    ├── 07-sandwich-tab.md             sandwich-day suggestions
    ├── 08-settings.md                 preferences + account
    └── 09-connect-calendar.md         EventKit permission + picker
```

## Sample-data convention

All screens use **South Korea, 2026** as the worked example
(Seollal Feb 16–18, Children's Day May 5, Chuseok Sep 24–26, etc.).
This keeps the generated screens visually consistent and lets you
compare Stitch output across runs.

Holiday dates and `/v1/plan` results are illustrative — they're
plausible but not pulled from the live API. If you regenerate with
real API data later, expect minor date shifts (lunar holidays move).

## After Stitch

Export the screens you like, then move on to high-fidelity work in
Figma or hand off to `daysoff-web` for implementation. The API
surface section in `master.md` is included so Stitch renders
realistic data shapes — it doubles as a reference for the
implementation team.
