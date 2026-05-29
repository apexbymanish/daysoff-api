# Screen 8 — Settings

> **Usage:** paste `master.md` first, then paste this file as a follow-up
> message in Stitch.

## Purpose

The Settings tab. Three jobs: (1) let the user change the three
preferences captured at onboarding (country, workweek, PTO budget);
(2) manage their account (email, password, sign out, delete); and (3)
expose app-level options (language, theme) and meta links (terms,
privacy, version). This is the calmest surface in the app — pure list
patterns, no surprises, no marketing. Should feel like iOS Settings or
Things 3's preferences pane.

## Sample data (KR 2026)

- User profile:
  - Email: `minjun@kakao.com`
  - Display name: "Minjun K." (optional, can be blank)
- Preferences:
  - Country of work: South Korea (KR)
  - Country of residence: Nepal (NP) — optional, set in this example
  - Workweek: Sat, Sun (off)
  - PTO budget: 15 days
- App:
  - Language: English (한국어 available)
  - Theme: System (Light / Dark / System)
- About:
  - Version: 1.0.0 (build 142)
  - Terms of Service / Privacy Policy links

## Layout

**Top section — profile card** (~140pt, edge-to-edge):

- Soft sage-tinted background.
- Left: circular avatar (~64pt) with the user's initials "MK" in
  warm-cream type centered. If the user has uploaded an image, show
  that instead.
- Right of avatar: display name "Minjun K." in 18pt medium (or "Add
  your name" placeholder link if empty), email in 13pt secondary
  below.
- Edit-pencil glyph top-right of the card → opens a half-sheet to
  edit display name + upload avatar.

**Section 1 — Account.**

- Section header in 12pt caps, 60% opacity: "Account".
- Rows (each ~56pt with left/right padding 20pt):
  - **Email** — read-only value on the right: "minjun@kakao.com". No
    chevron.
  - **Change password** → chevron, taps to push to a Change Password
    screen (out of scope for the v1 Stitch pack; mock the row).
  - **Sign out** — text in danger-red, no chevron, no value. Tap
    opens a confirmation sheet: "Sign out of daysoff? You can sign
    back in anytime."
  - **Delete account** — text in danger-red. Tap opens a more
    serious confirmation sheet with a typed-confirmation field ("Type
    DELETE to confirm") and a destructive primary button.

**Section 2 — Preferences.**

- Section header: "Preferences".
- Rows:
  - **Country of work** → value "South Korea", chevron. Tap →
    country search sheet (same component as Onboarding Card 3).
    Helper subline below value: "Drives your holidays and PTO
    planning."
  - **Country of residence** → value "Nepal" (or "Not set" in muted
    grey when empty), chevron. Tap → same country search sheet,
    with a "Remove" option pinned to the top of the sheet so the
    user can clear it. Helper subline: "Optional — we'll show home
    holidays on your timeline."
  - **Workweek** → value "Sat, Sun off", chevron. Tap → 7-day pill
    picker sheet. Helper subline: "Tied to your country of work."
  - **PTO budget** → value "15 days", chevron. Tap → slider sheet
    (same as Onboarding Card 4 but in sheet form).

**Section 3 — Calendar.**

- Section header: "Calendar".
- Rows:
  - **Status row** — left: small monoline calendar glyph; center:
    "Connected — 2 calendars" (or "Not connected" in muted grey
    when off); right: chevron. Tap → Screen 9 (Connect calendar)
    for setup or reconfiguration.
  - **Show events on Home** → toggle (default on when connected).
    Subline: "Personal events appear under the matching day."
  - **Warn about conflicts** → toggle (default on when connected).
    Subline: "Flag breaks that overlap your events."
  - **Disconnect** — only visible when connected, in danger-red.
    Tap opens a confirmation sheet: "Stop reading your calendar?
    daysoff will keep your saved breaks but won't show events on
    Home anymore." Confirming calls EventKit to release access
    and returns to the Settings list.

**Section 4 — App.**

- Section header: "App".
- Rows:
  - **Language** → value "English (한국어 available)", chevron. Tap
    → simple list picker (English, 한국어, नेपाली, 日本語, हिन्दी,
    Filipino, …).
  - **Theme** → value "System", chevron. Tap → bottom sheet with
    three segmented options: System / Light / Dark.

**Section 5 — About.**

- Section header: "About".
- Rows:
  - **Version** → value "1.0.0 (142)" on the right, no chevron.
  - **Terms of Service** → chevron (opens in-app browser).
  - **Privacy Policy** → chevron.

**Bottom tab bar** as in Screen 3 (current tab = Settings).

## Microcopy

- **Profile card empty-name placeholder:** "Add your name"
- **Account section labels:** "Email", "Change password", "Sign out",
  "Delete account"
- **Preferences labels:** "Country of work", "Country of residence",
  "Workweek", "PTO budget"
- **Country-of-residence empty value:** "Not set" (muted grey)
- **Country-of-residence sheet:** includes "Remove" option pinned at
  the top of the picker
- **Preference helper sublines:** "Drives your holidays and PTO
  planning." · "Optional — we'll show home holidays on your
  timeline." · "Tied to your country of work."
- **App labels:** "Language", "Theme"
- **About labels:** "Version", "Terms of Service", "Privacy Policy"
- **Sign-out confirmation title:** "Sign out of daysoff?"
- **Sign-out confirmation body:** "You can sign back in anytime."
- **Sign-out confirmation actions:** "Cancel" (text) · "Sign out"
  (sage fill)
- **Delete-account confirmation title:** "Delete your account?"
- **Delete-account confirmation body:** "This permanently removes
  your preferences and saved breaks. We can't undo it."
- **Delete confirmation field label:** "Type DELETE to confirm"
- **Delete confirmation primary:** "Delete account" (danger red,
  enabled only when field reads exactly "DELETE")
- **Theme sheet labels:** "System" · "Light" · "Dark"
- **Language sheet section heading (when many):** "Available
  languages"
- **Korean variants** (when locale is `ko-KR`): "계정", "환경설정",
  "언어", "테마", "로그아웃", "계정 삭제"

## States

- **Default** — Populated as in Sample data.
- **Display name empty** — Profile card shows "Add your name"
  placeholder link in brand teal.
- **Avatar empty** — Show initials on sage background.
- **Sign out in progress** — Confirmation sheet's primary button
  collapses to a spinner; on success, app routes back to Onboarding
  Card 1 with a brief sage toast: "Signed out."
- **Delete in progress** — Confirmation primary button collapses to
  spinner; on success, app routes to Onboarding Card 1 with a calm
  fade (no toast — the account is gone).
- **Delete field empty / wrong** — Primary button disabled (greyed),
  helper text under field: "Type the word DELETE to confirm."
- **Language change applied** — Closing the picker triggers a full
  app re-render in the new language (240ms crossfade); show a brief
  toast: "Language changed to 한국어."
- **Theme change applied** — Closing the picker fades the entire app
  to the new theme over 320ms.

## Dark mode

Profile card sage tint becomes a 14% sage fill on near-black. Section
headers stay 60% white. Danger-red shifts to a softer coral-red
(better contrast on near-black) — never bright pure red. Theme
picker's "Dark" option is pre-highlighted when current. The settings
list overall echoes Apple Calendar's dark mode — generous whitespace,
near-black surfaces, accent only where needed.

## Motion

- **Row tap → push to detail/sheet:** standard iOS push (cubic, 360ms)
  for screens; sheet rise (cubic-bezier(0.32, 0.72, 0, 1), 360ms) for
  bottom sheets.
- **Confirmation sheets:** half-height bottom sheet, drag-to-dismiss
  with rubber-band.
- **Sign out / Delete success:** entire app fades (240ms) to the
  Onboarding card.
- **Theme change:** full-app crossfade between light and dark
  surfaces, 320ms.
- **Language change:** full-app crossfade as the locale switches,
  240ms. Korean script in any visible labels animates in subtly.
- **Profile card edit:** edit-pencil rotates 15° on tap (140ms) and
  the half-sheet rises.
- **Reduced motion:** all crossfades become 180ms linear; pushes are
  instant.

## Accessibility

- Each row announces as a button or read-only value as appropriate:
  - Read-only: "Email, minjun at kakao dot com."
  - Tap-through: "Country, currently South Korea. Button."
  - Danger: "Sign out. Button." with `aria-describedby` linking to a
    short hint.
- Confirmation sheets have focus trapped inside; the destructive
  primary button is **not** auto-focused (prevents accidental
  triggers); cancel is the default focus.
- Delete-confirmation field is `aria-required="true"`; the primary
  button uses `aria-disabled` until the field reads exactly "DELETE".
- Theme picker uses radio-group semantics; selection announces "Dark,
  selected, 3 of 3".
- Avatar is decorative (`aria-hidden`); the display name + email
  carry the semantic identity.
- Dynamic Type: all rows grow vertically to accommodate; values
  truncate with ellipsis only when necessary and announce the full
  value to screen readers.
- Color is never the only cue: danger-red rows include the word
  "Delete" / "Sign out" — not just color.
- Korean labels (when active locale is `ko-KR`) are read with proper
  Korean pronunciation by the system; English fallback labels are
  hidden from the screen reader to avoid double-reading.
