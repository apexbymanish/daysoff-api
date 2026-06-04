# Country / holiday / festival images — design note

Brainstormed 2026-05-28. **Parked as future backend work** — not in
scope for the current Stitch-prompt-pack or Flutter scaffold sessions.

## Goal

Serve illustrative imagery to the daysoff mobile app for three uses:

1. **Country hero backdrops** — one landscape/scene per country, used
   behind country chips, the onboarding country card, and the country
   picker. Example: Himalayas for NP, Gyeongbokgung for KR.
2. **Holiday-specific imagery** — one image per major holiday, shown
   on the holiday detail sheet hero (Stitch Screen 4).
3. **Cultural festival photos** — one image per festival, surfaced in
   the "What's nearby" block on Holiday detail.

## Source strategy

**Hybrid: curated + Unsplash fallback.**

- **Curated:** hand-pick high-quality images for the five primary
  countries (KR, NP, JP, IN, PH) — one country hero + ~10–15 major
  holidays each + 2–5 festivals. Total ~60–80 curated images. Upload
  to Firebase Storage (since we're already using Firebase for user
  data) at paths like:
  ```
  images/curated/country/{code}.jpg
  images/curated/holiday/{country}/{slug}.jpg
  images/curated/festival/{country}/{slug}.jpg
  ```
  Recommended size: 1200×800 JPG, ~150 KB after compression.

- **Unsplash fallback:** for the long tail (~245 countries + all
  non-major holidays/festivals), fetch from the Unsplash API on demand
  and cache the URL (not the bytes) in `holidays.db`. Unsplash search
  queries:
  ```
  country  → "{country_name} landscape" or "{country_name} city"
  holiday  → "{holiday_name} {country_name}"
  festival → "{festival_name} {country_name}"
  ```
  Unsplash free tier: 50 req/hr per app — plenty since we cache URLs
  forever (and refresh weekly to handle rare deletions).

## Schema

Single table in `holidays.db`:

```sql
CREATE TABLE IF NOT EXISTS images (
  category          TEXT NOT NULL,    -- 'country' | 'holiday' | 'festival'
  key               TEXT NOT NULL,    -- 'KR' | 'KR:Chuseok' | 'KR:AndongMaskDance'
  source            TEXT NOT NULL,    -- 'curated' | 'unsplash'
  url               TEXT NOT NULL,    -- full-size URL
  thumb_url         TEXT,             -- thumbnail (optional)
  width             INTEGER,
  height            INTEGER,
  photographer_name TEXT,             -- Unsplash attribution
  photographer_url  TEXT,             -- Unsplash profile link
  cached_at         INTEGER NOT NULL, -- unix epoch seconds
  PRIMARY KEY (category, key)
);
```

Keys are stable per content:
- Country: ISO-2 code (`KR`, `NP`).
- Holiday: `{country}:{snake_case_holiday_name}` (`KR:chuseok`,
  `KR:childrens_day`). Slugs are derived from the canonical name in
  the `holidays` library, lowercased and underscored.
- Festival: `{country}:{snake_case_festival_name}`
  (`KR:andong_mask_dance_festival`).

## Code surface

- **New module:** `sources/image_source.py`
  - `get_country_image(country_code: str) -> ImageRecord | None`
  - `get_holiday_image(country_code: str, name: str) -> ImageRecord | None`
  - `get_festival_image(country_code: str, name: str) -> ImageRecord | None`
  - Each: check `images` table → return if present → otherwise call
    Unsplash, persist URL, return.
- **Storage:** extend `storage.py` with `get_image_record(...)` and
  `upsert_image_record(...)`.
- **Unsplash client:** thin wrapper around
  `https://api.unsplash.com/search/photos` keyed by
  `UNSPLASH_ACCESS_KEY` env var. Polite `User-Agent` header.
- **Refresh policy:** entries with `source='unsplash'` and
  `cached_at` > 90 days old re-fetch on next request. Curated
  entries never auto-refresh (manual updates only).

## API surface

Two endpoint variants — pick one when implementing:

**Query-style (simplest):**
```
GET /v1/image?type=country&key=KR
GET /v1/image?type=holiday&key=KR:chuseok
GET /v1/image?type=festival&key=KR:andong_mask_dance_festival
```

**RESTful (cleaner for clients):**
```
GET /v1/images/country/{code}
GET /v1/images/holiday/{country}/{slug}
GET /v1/images/festival/{country}/{slug}
```

Response (`ImageRecord` shape):
```json
{
  "category": "country",
  "key": "KR",
  "source": "curated",
  "url": "https://storage.firebase.../images/curated/country/KR.jpg",
  "thumb_url": null,
  "width": 1200,
  "height": 800,
  "photographer_name": null,
  "photographer_url": null
}
```

404 if no image found and Unsplash returned zero results — the client
falls back to a tasteful gradient placeholder.

## Frontend integration

- Flutter side uses `cached_network_image` for on-device caching and
  fade-in transitions.
- Attribution: when `source='unsplash'` and `photographer_name` is
  set, render a 10pt secondary caption below the image (per Unsplash
  ToS): "Photo by {name} on Unsplash" with the name as a tappable
  link to `photographer_url`.
- Curated images have no attribution (the photographer is implicit /
  was paid or asset is owned).

## Curation workflow

For the initial curated batch (~60–80 images):

1. Hand-pick images (Unsplash, paid stock, or own photography).
2. Resize/compress to 1200×800 JPG ~150 KB.
3. Upload to Firebase Storage under `images/curated/...`.
4. Run a one-time seed script to populate `images` table rows with
   the resulting public URLs and `source='curated'`.

Re-curation: edit the `images` row directly (UPDATE) or re-upload
and bump the URL; clients pick up the change on next fetch.

## Caching considerations

- **URL cache vs byte cache:** the `images` table stores **URLs**,
  not image bytes. Byte caching happens on the device via
  `cached_network_image`. This keeps `holidays.db` small.
- **Unlike the Wikipedia spec, URL caching here is essentially
  required** — Unsplash's 50 req/hr free tier makes uncached
  lookups impractical even at low traffic.

## Out of scope

- Multi-language image variants (one image per (category, key) for v1).
- User-uploaded images (no upload UI in mobile app for v1).
- AI-generated imagery (avoids attribution / quality risks for now).
- Image resizing / on-the-fly transformations (would require Cloudinary
  or imgproxy; defer until needed).

## Next step

When picked up: brainstorming → writing-plans on this spec. Expected
deliverables: `sources/image_source.py`, schema migration in
`storage.py`, new endpoint(s) in `api/main.py`, response schemas in
`api/schemas.py`, tests covering curated hit + unsplash miss-then-hit
+ 404 paths, env-var docs (`UNSPLASH_ACCESS_KEY`), README update.
