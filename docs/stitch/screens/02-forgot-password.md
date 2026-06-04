# Screen 2 — Forgot password

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

Out-of-flow auth recovery, reached from the "Forgot password?" link on
the Sign in side of Card 2 in Onboarding. The screen has two states in
one flow: an email-entry form, then a "check your inbox" confirmation
once the reset has been requested. No password is ever set here — that
happens via a magic link in the email. The tone is calm and clinical
(this is a "you're locked out" moment; reassurance, not exclamation
marks).

## Sample data (KR 2026)

- User who tapped "Forgot password?" had typed `minjun@kakao.com`
  on the sign-in card. That email is pre-filled into this screen's
  field so the user doesn't retype.
- Confirmation copy references the email: "We've sent a reset link to
  **minjun@kakao.com**."

## Layout

**State A — Email entry.**

- Top-left back chevron (returns to Onboarding Card 2 sign-in).
- Centered title at the top third: "Reset your password" (28pt
  semibold). Below, in 14pt secondary: "Enter the email you signed
  up with. We'll send you a link to set a new password."
- Single text field, full-width with floating label "Email", pre-filled
  with the email from the previous screen, focus state shows the
  brand teal underline.
- Full-width primary button below the field: "Send reset link" (sage
  fill, peach accent dot on the right when input is valid).
- Small text link centered near the bottom: "I remembered it — sign in"
  (returns to Sign in).

**State B — Confirmation (after submit).**

- Same top chevron (now returns user to Sign in).
- Centered envelope illustration (~96pt) in muted sage with a peach
  seal — monoline, not playful.
- Heading 28pt semibold: "Check your inbox."
- Body 14pt: "We've sent a reset link to **minjun@kakao.com**. The link
  expires in 30 minutes."
- Two action rows stacked:
  - Text button: "Resend email" (greyed out for 30 seconds after first
    send, shows a countdown like "Resend in 18s")
  - Text button: "Use a different email" (returns to State A with the
    field cleared)

## Microcopy

- **State A title:** "Reset your password"
- **State A helper:** "Enter the email you signed up with. We'll send
  you a link to set a new password."
- **State A field label:** "Email"
- **State A CTA:** "Send reset link"
- **State A back link:** "I remembered it — sign in"
- **State B title:** "Check your inbox."
- **State B body:** "We've sent a reset link to **{email}**. The link
  expires in 30 minutes."
- **State B actions:** "Resend email" · "Use a different email"
- **State B cooldown:** "Resend in {n}s"
- **Errors:**
  - Invalid format: "That doesn't look like an email."
  - Unknown email (only after deliberate "use different email"):
    "We don't recognize that email."
  - Network: "Check your connection and try again."
  - Rate-limited: "Too many tries. Please wait a few minutes."

## States

- **Default (State A)** — Email pre-filled from prior screen, button
  enabled.
- **Submitting** — Button collapses to spinner, field locks.
- **Success → State B** — Crossfade to the envelope confirmation.
- **Cooldown (State B)** — Resend button greyed with countdown.
- **Error (State A)** — Inline red helper under the field; banner only
  for network/rate-limited cases.
- **Rate-limited** — State B may show a calm yellow banner above the
  envelope: "We've sent a few of these already. If you don't see one,
  check your spam folder."

## Dark mode

Background near-black. Envelope illustration shifts to warm-cream with
the peach seal slightly desaturated. Text field stroke at 12% white,
sage CTA one stop darker. Yellow rate-limit banner uses a deep ochre
fill, not bright yellow.

## Motion

- **State A → State B:** crossfade 240ms; envelope illustration scales
  from 92% to 100% over the same window (spring, light damping).
- **Envelope idle:** very gentle vertical bob, 4px amplitude, 1.5s loop,
  ease-in-out — should feel "waiting", not playful. No rotation.
- **Resend countdown:** numeric tween at 60fps; on completion, button
  re-enables with a 200ms color fade from grey to sage.
- **Error inline:** field underline shifts to red over 180ms; helper
  text fades up from below the field.
- **Field auto-focus:** on screen mount in State A, focus the email
  field after 220ms (after the back-navigation animation settles).

## Accessibility

- The Enter key on the keyboard submits the form when the field is
  valid; iOS keyboard Done key does the same.
- VoiceOver on State B reads the title and body together: "Check your
  inbox. We've sent a reset link to minjun at kakao dot com. The link
  expires in 30 minutes."
- Resend countdown announces every 5 seconds: "Resend available in
  15 seconds."
- Envelope illustration is `aria-hidden`; the heading carries the
  semantic content.
- All inline errors are also surfaced as ARIA live-region announcements
  so screen reader users don't miss them.
- Tap targets: text buttons have hit area expanded to 44pt vertically
  even when the visible text is smaller.
