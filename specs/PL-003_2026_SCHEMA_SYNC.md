# Design Spec: PL-003 2026 Grid Schema Sync

**Issue:** DON-7 / PL-003
**Status:** ✅ DONE
**Last Updated:** 2026-02-22

## 1. Objective

Update the database to reflect the 2026 F1 grid — Kick Sauber → Audi rebrand, seed all 20 RACE driver contracts, fix API gaps blocking the UI.

## 2. What's Done

| Item | Command / File | Status |
| :--- | :--- | :--- |
| 2026 Season (24 races) | `seed_2026_schedule.py` | ✅ Done |
| 2026 Driver Lineup (20 drivers) | `seed_data.py` | ✅ Done |
| 10 Teams seeded | `seed_data.py` | ✅ Done |
| Kick Sauber → Audi rebrand | `seed_2026_grid.py` | ✅ Done |
| 20 RACE DriverContract rows | `seed_2026_grid.py` | ✅ Done |
| 37 paddock staff contracts (TP, TD, RE…) | `seed_staff_contracts.py` | ✅ Done |
| `ContractViewSet` `is_active` filter | `api/views.py` | ✅ Done |
| `ContractReadSerializer` exposes `primary_color` | `api/serializers.py` | ✅ Done |

## 3. Implementation Notes

### 3.1 Audi Rebrand

`seed_2026_grid.py` updates the existing `SAU` team record in-place (idempotent):
- `code`: `"SAU"` → `"AUD"`
- `base_name`: `"Kick Sauber"` → `"Audi F1 Team"`
- `primary_color`: `"#52E252"` → `"#BB0000"`
- `country`: `"Switzerland"` → `"Germany"`

CSS token renamed in lockstep: `--color-team-sauber` → `--color-team-audi: #BB0000`.

### 3.2 RACE DriverContract Rows

`seed_2026_grid.py` creates one `DriverContract(role='RACE')` per driver, resolved by `Driver.code`, linked to `Team` and `Season(year=2026)`. Validates against model `clean()` (RACE roles must have `driver` FK set).

2026 grid:

| Team | Drivers |
|---|---|
| RBR — Red Bull Racing | VER (Verstappen), LAW (Lawson) |
| FER — Scuderia Ferrari | LEC (Leclerc), HAM (Hamilton) |
| MCL — McLaren F1 Team | NOR (Norris), PIA (Piastri) |
| MER — Mercedes-AMG Petronas | RUS (Russell), ANT (Antonelli) |
| AMR — Aston Martin Aramco | ALO (Alonso), STR (Stroll) |
| ALP — Alpine F1 Team | GAS (Gasly), DOO (Doohan) |
| WIL — Williams Racing | ALB (Albon), SAI (Sainz) |
| RBT — Racing Bulls | TSU (Tsunoda), HAD (Hadjar) |
| HAA — MoneyGram Haas F1 Team | BEA (Bearman), OCO (Ocon) |
| AUD — Audi F1 Team | HUL (Hülkenberg), BOR (Bortoleto) |

### 3.3 Staff Contracts

Run after `seed_2026_grid` (requires `AUD` code to exist):
```bash
python manage.py seed_staff_contracts --file data/staff_contracts_2026.json --season 2026
```
Creates 37 entries: 10 TEAM_PRINCIPAL, 10 TECHNICAL_DIRECTOR, 14 RACE_ENGINEER, 2 PERFORMANCE_ENGINEER, 1 STAFF.

### 3.4 API Fixes

`ContractViewSet.get_queryset()` now filters on `?is_active=true|false`.

`ContractReadSerializer` now exposes `primary_color` (sourced from `team.primary_color`), enabling the Drivers page to colour-code cards directly from contract data without a second Teams API call.

### 3.5 Engine Supplier Updates (Deferred)

The 2026 PU regulation changes (Audi works unit, Honda RBPT → Aston Martin, Ford/Red Bull Powertrains) are not tracked in Phase 1 — no `EngineSupplier` model is used in the UI. Deferred to Phase 2 (PL-018 entity model).

## 4. How to Re-seed (Fresh DB)

```bash
# 1. Base data
python manage.py seed_data

# 2. 2026 grid + Audi rebrand + RACE contracts
python manage.py seed_2026_grid

# 3. Staff contracts
python manage.py seed_staff_contracts --file data/staff_contracts_2026.json --season 2026

# 4. Schedule
python manage.py seed_2026_schedule

# 5. Social handles (PL-010)
python manage.py seed_social_handles --file data/paddock_handles_2026.json
```

## 5. Success Criteria

- [x] `Team` record for Audi reflects 2026 branding (name `AUD`, color `#BB0000`)
- [x] All 20 drivers linked to correct 2026 teams via `DriverContract(role='RACE')`
- [x] `seed_2026_grid.py` command exists and is idempotent
- [x] `GET /api/v1/contracts/?role=RACE&is_active=true` returns 20 rows with `primary_color`
- [x] Teams page and Drivers page show live 2026 data (no hardcoded fallback)
