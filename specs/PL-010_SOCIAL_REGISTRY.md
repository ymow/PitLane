# Design Spec: PL-010 Paddock Social Registry

## 1. Objective

Build a curated "phonebook" of the F1 paddock that maps social media handles to
teams, drivers, and key technical staff for the 2026 season. The registry feeds
the article entity-extractor pipeline (auto-tagging) and powers entity profile
pages on the frontend.

---

## 2. Data Models

### 2.1 `SocialHandle`

| Field | Type | Notes |
|---|---|---|
| `id` | CharField(32) | UUID, auto-generated |
| `platform` | Enum | TWITTER, INSTAGRAM, TIKTOK, YOUTUBE, FACEBOOK, LINKEDIN |
| `handle` | CharField(100) | e.g. `@LewisHamilton` |
| `url` | URLField | Full profile URL |
| `entity_type` | Enum | DRIVER, TEAM, STAFF, PARTNER |
| `driver` | FK → Driver \| null | Set when entity_type = DRIVER |
| `team` | FK → Team \| null | Set when entity_type = TEAM |
| `staff_name` | CharField \| null | Free text for staff not in DB |
| `role` | CharField(100) \| null | e.g. "Chief Technical Officer" |
| `is_verified` | Boolean | Official/verified account |
| `is_active` | Boolean | False = handle defunct / driver left |
| `valid_from` | DateField \| null | Season/transfer start date |
| `valid_until` | DateField \| null | Null = currently active |
| `follower_count` | IntegerField \| null | Cached, updated weekly |
| `created_at` | DateTimeField | auto |
| `updated_at` | DateTimeField | auto |

**Constraint:** `unique_together = [platform, handle]`

**FK strategy:** Per-type nullable FKs (`driver`, `team`) instead of a generic
`entity_id`. This keeps joins explicit and avoids ContentType complexity for
Phase 1. Staff who have no DB model use `staff_name` + `team` FK.

### 2.2 DB Table

```
social_handles
```

---

## 3. Operations

### Phase 1 — Seeding

**Sources:**
- Drivers: FIA 2026 entry list + each driver's verified social bios
- Teams: Official team accounts from team websites
- Staff: FIA Technical Regulations signatory list + team press releases

**Bulk import:**
```bash
python manage.py seed_social_handles --file data/paddock_handles_2026.json
```

JSON schema:
```json
[
  {
    "platform": "TWITTER",
    "handle": "@LewisHamilton",
    "url": "https://twitter.com/LewisHamilton",
    "entity_type": "DRIVER",
    "driver_code": "HAM",
    "is_verified": true
  }
]
```

**CLI add (one-off):**
```bash
python manage.py add_social_handle \
  --platform TWITTER \
  --handle @james_allison \
  --entity-type STAFF \
  --team FER \
  --role "Chief Technical Officer"
```

### Phase 2 — Maintenance (future)

- Weekly Celery task refreshes `follower_count` via platform APIs
- On driver transfer: set `valid_until` on old team handles, seed new ones
- Deactivation: `is_active = False` (never hard-delete — preserves history)

---

## 4. API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/social-handles/` | List all active handles (filterable by `entity_type`, `platform`, `team`, `driver`) |
| GET | `/api/v1/drivers/{code}/social/` | All handles for a driver |
| GET | `/api/v1/teams/{code}/social/` | All handles for a team + their staff |

---

## 5. Entity Extractor Integration

The NLP article entity extractor (`apps/analysis/`) can consume this registry to:
1. Match social handle mentions (`@LewisHamilton`) in article bodies → auto-tag article with Driver entity
2. Boost confidence score when handle appears alongside a driver name

This is wired in Phase 2 — Phase 1 only seeds the data.

---

## 6. Frontend Usage

- Driver profile page: social links row below driver card
- Team page: team social links + staff directory with handles
- Article page: tagged entity chips link to entity profiles

---

## 7. Success Criteria

- All 10 teams and 20 drivers have ≥ 1 verified handle per major platform (Twitter, Instagram)
- ≥ 100 key staff (Team Principals, Technical Directors, Race Engineers) registered
- Bulk seed script idempotent (re-run does not create duplicates)
- `/api/v1/drivers/{code}/social/` returns correct handles within 200ms

---

## 8. Out of Scope (Phase 1)

- Active content scraping / social feed ingestion
- Sentiment analysis on posts
- Automatic handle discovery
