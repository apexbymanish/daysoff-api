# User data via Firebase Auth + Firestore — design note

Brainstormed 2026-05-28. **Parked for the daysoff-mobile sessions** —
not in scope for the current Flutter scaffold (which lands on Home
without any auth gate).

## Goal

Persist user-specific data with cross-device sync, satisfying the
master Stitch spec's "account required; preferences sync to account"
hard requirement. The daysoff-api stays focused on public holiday
content; user data lives in Firebase.

## Why Firebase over extending daysoff-api

| Concern | Firebase | Extend daysoff-api |
|---|---|---|
| Auth (email/password + Google + Apple) | Out of the box | Several days of plumbing |
| User data CRUD | Firestore + security rules | Custom endpoints + auth middleware |
| Cross-device sync | Built-in real-time listeners | Need polling or websockets |
| Effort to v1 | Hours | Weeks |
| Data ownership | Google holds it | You hold it |
| Vendor lock-in | High | Low |

For v1 the speed-to-market wins. Migrating to a Postgres-backed
endpoint in `daysoff-api` is a documented later step (see "Migration"
below) — kept feasible by keeping the Flutter data layer thin.

## Auth

**Firebase Auth providers** (matches Stitch screen 01):

- Email + password
- Google
- Apple (required for App Store if any social sign-in is offered)

**Token model:** Firebase ID tokens. The Flutter client gets a JWT on
sign-in and forwards it as `Authorization: Bearer <id_token>` to any
future authenticated endpoint on daysoff-api (none yet — see
"daysoff-api auth follow-up" below).

## Firestore schema

One top-level collection plus per-user subcollections.

### `users/{uid}` (single document per user)

```typescript
{
  uid: string,                      // matches Firebase Auth uid
  email: string,                    // denormalized for display
  display_name: string | null,
  avatar_url: string | null,

  // Preferences (master.md hard requirements)
  country_of_work: string,          // 'KR'
  country_of_residence: string | null, // 'NP' or null
  workweek: string[],               // ['sat', 'sun']
  pto_budget: number,               // 15

  // App preferences
  language: string,                 // 'en' | 'ko' | 'ne' | 'ja' | 'hi' | 'fil'
  theme: 'system' | 'light' | 'dark',

  // Calendar integration state (Stitch screen 09)
  calendar_connected: boolean,
  selected_calendar_ids: string[],  // EventKit calendar IDs the user opted in

  // Metadata
  created_at: Timestamp,
  updated_at: Timestamp
}
```

### `users/{uid}/saved_breaks/{break_id}` (subcollection)

```typescript
{
  break_id: string,                 // auto-generated
  country: string,                  // 'KR'
  year: number,                     // 2026
  break_start: string,              // ISO date '2026-09-23'
  break_end: string,                // ISO date '2026-09-27'
  break_length: number,             // 5
  pto_dates: string[],              // ['2026-09-23']
  pto_cost: number,                 // 1
  anchors: string[],                // ['Chuseok', ...]
  saved_at: Timestamp,
  added_to_calendar: boolean,       // true after "Add to calendar" tapped
  calendar_event_id: string | null  // EventKit identifier for unlink
}
```

### `users/{uid}/saved_sandwiches/{sandwich_id}` (subcollection)

```typescript
{
  sandwich_id: string,              // auto-generated
  country: string,
  year: number,
  pto_date: string,                 // ISO date
  break_start: string,
  break_end: string,
  break_length: number,
  context: string,                  // 'wedged between weekend and Children's Day'
  saved_at: Timestamp,
  reminder_date: string | null      // ISO date — 1 week before pto_date
}
```

## Security rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid} {
      // Owner read+write; nothing else exposed
      allow read, write: if request.auth != null && request.auth.uid == uid;

      match /{subcollection}/{docId} {
        allow read, write: if request.auth != null && request.auth.uid == uid;
      }
    }
  }
}
```

Tightening pass needed before production: validate field types in
rules, cap document size, rate-limit subcollection creation.

## Flutter integration

**Packages to add to `daysoff-mobile/pubspec.yaml`:**

```yaml
firebase_core: ^3.x
firebase_auth: ^5.x
cloud_firestore: ^5.x
google_sign_in: ^6.x
sign_in_with_apple: ^6.x
```

**File layout (lib/services/):**

```
lib/
├── services/
│   ├── auth_service.dart       wraps FirebaseAuth — signIn, signUp,
│   │                           signOut, currentUser, authStateChanges
│   └── user_data_service.dart  wraps FirestoreUserRepository —
│                               loadProfile, updatePreferences,
│                               saveBreak, deleteBreak, watchSavedBreaks
├── providers/
│   ├── auth_provider.dart      StreamProvider<User?>
│   └── user_data_provider.dart StreamProvider<UserProfile>
└── api/models/
    ├── user_profile.dart       freezed model mirroring users/{uid}
    └── saved_break.dart        freezed model mirroring saved_breaks
```

**Provider pattern:**

- `authStateProvider` is a `StreamProvider<User?>` over
  `FirebaseAuth.instance.authStateChanges()`.
- `userProfileProvider` is a `StreamProvider<UserProfile>` watching
  `users/{uid}` — only active when `authStateProvider` has a user.
- Router redirects unauthenticated users to `/onboarding` (which
  shows Card 2 — the auth card).

## Sync semantics

- **Preferences:** real-time listener on `users/{uid}`. Any local
  edit (via Settings) writes-through to Firestore; the listener
  updates other devices within seconds.
- **Saved breaks / sandwiches:** real-time listeners on the
  subcollections; UI updates without manual refresh when the user
  has the app open on multiple devices.
- **Offline:** Firestore SDK queues writes locally and replays on
  reconnect; reads come from the local cache when offline.

## daysoff-api auth follow-up

The daysoff-api endpoints are currently all public. To remain
useful when authenticated routes exist (e.g., a server-side `/v1/me`
endpoint that aggregates saved breaks across devices), the API
should accept Firebase ID tokens:

- Verify the JWT against Firebase's public keys.
- Extract the uid for per-user logic.
- Implementation: a FastAPI dependency `current_user = Depends(verify_firebase_jwt)`.

This is **not** required for v1 — the Flutter client can talk to
Firestore directly and only hit daysoff-api for public holiday data.

## Migration path (if you outgrow Firebase later)

1. Add Postgres + Alembic to daysoff-api; mirror the Firestore schema
   as relational tables.
2. Build authenticated endpoints (`POST /v1/me/preferences`, `GET
   /v1/me/saved-breaks`, etc.) that verify Firebase JWTs and read/write
   Postgres.
3. In the Flutter app, swap `cloud_firestore` calls in the services
   layer for HTTP calls to the new endpoints. The widget layer doesn't
   change (services boundary stays the same).
4. Run a one-time export from Firestore → Postgres; then disable
   Firestore writes.

Total effort estimate: ~2–3 weeks. Keeping `services/` as a clean
boundary is what makes this feasible.

## Out of scope

- Multi-user / team features (no shared docs, no permissions matrix).
- In-app purchases / paid tiers (master.md non-goal).
- Push notifications (master.md non-goal; reminder rows in Stitch
  spec are mock affordances only).
- Account deletion compliance (GDPR/CCPA right-to-be-forgotten
  workflows) — needs its own design when productionizing.

## Next step

When picked up: brainstorming → writing-plans on this spec. Expected
deliverables: Firebase project setup, three packages added to
`daysoff-mobile`, `lib/services/auth_service.dart`,
`lib/services/user_data_service.dart`, freezed models for
UserProfile / SavedBreak / SavedSandwich, provider wiring, router
redirect for unauthenticated routes, security rules deployed, and
the Onboarding auth card (Stitch screen 01 Card 2) implemented for
real.
