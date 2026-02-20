# Design Spec: PL-010 Paddock Social Registry

## 1. Objective
Build a static "Phonebook" of the F1 paddock. This registry maps social media handles to specific teams, drivers, and technical roles for the 2026 season.

## 2. Data Models

### 2.1 `SocialHandle` (Proposed)
- `handle`: e.g. "@james_allison_f1"
- `platform`: Enum (INSTAGRAM, TWITTER, TIKTOK)
- `entity_type`: Enum (TEAM, DRIVER, STAFF, PARTNER)
- `entity_id`: Link to existing models (or generic Entity ID)
- `metadata`: JSONB (Role title, e.g., "Chief Technical Officer")

## 3. Operations (Phase 1)
- **Roster Seeding**: Bulk import of the 2026 grid.
- **CLI Ingestion**: `python manage.py add-handle <handle> --role <role>`
- **No Scraping**: Active content analysis is out of scope for Phase 1.

## 4. Success Criteria
- All 10 teams and 20 drivers have verified official accounts in the DB.
- At least 100 key staff members (TPs, TDs, Engineers) registered.
