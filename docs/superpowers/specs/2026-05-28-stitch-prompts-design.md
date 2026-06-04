# Stitch prompt pack — design note

Brainstormed and produced on 2026-05-28.

## What was built

A structured pack of Google Stitch prompts for designing the **daysoff**
mobile app, replacing the single-file `docs/stitch-prompt.md` with:

- `docs/stitch/README.md` — usage guide
- `docs/stitch/master.md` — master prompt pasted first in every session
- `docs/stitch/screens/01..08-*.md` — eight detailed per-screen
  follow-up prompts

`docs/stitch-prompt.md` is now a 3-line redirect.

## Key decisions

**File layout: split per-screen.** One markdown file per screen instead
of inline sections. Cleaner per-screen iteration; each file is small
enough to paste without context-window pressure on Stitch. Trade-off:
more files to keep in sync — acceptable because the master prompt holds
the shared style/tone and the screens just describe their own surface.

**Detail level: detailed (~500–700 words/screen).** Includes layout,
microcopy, states, dark mode, motion, accessibility. Risk that Stitch
ignores some directives, but the extra fidelity is worth it for
consistency across screens.

**Sample data anchor: KR 2026.** All screens use the same worked
example (Seollal, Children's Day, Chuseok, etc.). Lets the user compare
Stitch output across runs and matches the `/v1/plan` sample already in
the master prompt. Data is invented but plausible — not pulled from the
live API.

**Auth model: required signup.** The original spec said "no auth, fully
stateless" — this was deliberately reversed. New screens added:
01-onboarding now includes an auth card with email/password + Google +
Apple sign-in; 02-forgot-password covers recovery; 08-settings has an
Account section with sign-out and delete-account flows. Signup is
**inline with onboarding** (auth card sits between Welcome and the
preference cards). The master prompt's "hard requirements" section was
revised accordingly.

**Backend note:** the API as it exists today is fully public — no
tokens enforced. `master.md` calls this out so the designer is aware
that the auth tier is a follow-up backend task; for design purposes,
assume it exists.

**Fixed: 150+/250+ inconsistency.** Earlier the master prompt
said "150+ countries supported" in one place and "250+" in another.
Both now say 250+ (confirmed against `supported_country_codes()`).

**Country-of-work vs country-of-residence.** Added late in the
session to support the expat / remote-worker case. **Country of work**
is the primary input — drives which holidays grant free days and what
workweek applies. **Country of residence** is an optional secondary
field — if set, the Home timeline overlays the user's home-country
holidays with a distinct visual treatment (dashed left edge, house
glyph) but they're not counted toward PTO planning. Onboarding Card 3
gates the secondary picker behind a small "I live somewhere else"
link so the common-case user isn't shown two fields. Settings exposes
both rows. The 4 affected screen prompts (01, 03, 04, 08) were
updated; the master prompt's hard-requirements section explains the
model.

**Apple Calendar integration via EventKit.** Reverses the original
"no calendar integration" non-goal. Read + write integration limited
to Apple Calendar (EventKit) — no Google Calendar / Outlook in v1.
Permission is **deferred + optional**: the app works fully without it,
and the connect flow is reachable from a dismissible Home banner,
from Settings, or from a "Connect first" link on Break detail. A new
screen file (`screens/09-connect-calendar.md`) holds the two-phase
permission + calendar-picker flow. Five existing screens were updated
to thread events through: Home (event rows + connect banner), Holiday
detail sheet (calendar-conflict card in opportunities), Plan
length-buffet (conflict glyph on cards), Break detail (per-day event
sub-rows + "Add to calendar" action), and Settings (new Calendar
section between Preferences and App).

**Scope creep note.** The original v1 spec described a fully
stateless, read-only, no-auth app. By the end of this session v1
includes: required signup, country-of-residence, and optional
Apple Calendar integration. These are deliberate user-driven
expansions, but downstream estimates (implementation, QA, design
polish) should reflect the larger surface.

## Out of scope

- Implementation. No code changes; this pack is design-only.
- Backend auth wiring. Flagged as a follow-up.
- Figma generation. Stitch is the chosen surface; Figma is a possible
  later step.
- A Change Password screen — referenced as a row in Settings but its
  own prompt isn't included in the v1 pack.

## How to use the pack

See `docs/stitch/README.md`. Workflow: paste `master.md` first in a
Stitch session, then paste any screen file as a follow-up message.
Stitch handles ~6–8 screens per session; the 8 included screens fit
comfortably.
