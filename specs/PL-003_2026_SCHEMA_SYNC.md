# Design Spec: PL-003 2026 Grid Schema Sync

**Issue:** DON-7 / PL-003
**Status:** 🚧 IN PROGRESS
**Last Updated:** 2026-02-21

## 1. Objective

Update the database to reflect the 2026 F1 grid — primarily the Kick Sauber → Audi rebrand and any outstanding driver/team data gaps.

## 2. What's Already Done

| Item | Command | Status |
| :--- | :--- | :--- |
| 2026 Season (24 races) | `seed_2026_schedule.py` | ✅ Done |
| 2026 Driver Lineup | `seed_data.py` (includes HUL, BOR at Sauber) | ✅ Done |
| 10 Teams seeded | `seed_data.py` | ✅ Done |

## 3. What's Pending

### 3.1 Kick Sauber → Audi Rebrand
`seed_data.py` seeds the team as `Kick Sauber` (code: `SAU`). For 2026, this team competes as **Audi** with a new identity.

Changes required in the `Team` model:
- `base_name`: `"Kick Sauber"` → `"Audi F1 Team"`
- `code`: `"SAU"` → `"AUD"`
- `primary_color`: `"#52E252"` → `"#BB0000"` (Audi red)
- `country`: `"Switzerland"` → `"Germany"`

### 3.2 Engine Supplier Updates
The 2026 season introduces a new PU regulation era. Supplier changes:
- **Audi**: New works team (formerly Sauber/Ferrari PU)
- **Honda RBPT**: Continues with Aston Martin after Red Bull split (confirm)
- **Ford/Red Bull Powertrains**: Red Bull's new PU partner

These should be reflected in the `EngineSupplier` / `brands` models if tracked.

### 3.3 Missing Management Command
There is no `seed_2026_grid.py` command. The 2026-specific team and driver changes are currently mixed into the 2025-labelled `seed_data.py`.

## 4. Implementation Plan

### Step 1: Create `seed_2026_grid.py` management command
A dedicated command that is idempotent and updates (not re-creates) the 2026-specific entries:

```
python manage.py seed_2026_grid
```

Should handle:
- Rename Kick Sauber → Audi (update existing `SAU` record)
- Update engine supplier relationships
- Verify all 20 drivers are linked to the correct 2026 teams via `DriverContract`

### Step 2: Verify Driver–Team Contracts
Confirm `DriverContract` records exist for the 2026 season, linking each driver to their team. Currently `seed_data.py` creates drivers but does not create `DriverContract` records.

### Step 3: Validate via API
Run `GET /api/v1/teams/` and `GET /api/v1/drivers/` and confirm the 2026 grid is correct before marking done.

## 5. Success Criteria

- [ ] `Team` record for Audi reflects 2026 branding (name, code, color)
- [ ] All 20 drivers linked to correct 2026 teams via `DriverContract`
- [ ] `seed_2026_grid.py` command exists and is idempotent
- [ ] API returns correct 2026 grid data
