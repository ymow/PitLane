# PitLane: Universal Domain Intelligence Engine - Master Spec

**Last Updated:** 2026-02-21

## 1. Vision & Core Principles
PitLane is an agentic CMS platform using real-time data and entity graphs to deconstruct complex industries.
- **North Star**: Empower fans with "Team Principal" level intelligence through LLM-driven causal inference and real-time telemetry.
- **Spec-Driven**: All development follows the Superpowers methodology (Design -> Plan -> TDD -> Execute).
- **Domain Agnostic**: The engine supports pluggable templates (F1, Movies, etc.).

---

## 2. Current Phase: Phase 1 - 2026 Season Readiness

### 2.1 Paddock Social Registry (Active) — PL-010
Establishing a curated database of 2000+ paddock personnel social handles
(Teams, Drivers, Technical Directors, Race Engineers, Mechanics).

**Revised model (see `specs/PL-010_SOCIAL_REGISTRY.md`):**
- Per-type nullable FKs: `driver → Driver`, `team → Team` (no generic `entity_id` in Phase 1)
- Platform enum: TWITTER, INSTAGRAM, TIKTOK, YOUTUBE, FACEBOOK, LINKEDIN
- Lifecycle fields: `is_verified`, `is_active`, `valid_from`, `valid_until`, `follower_count`
- Bulk JSON seed + CLI `add_social_handle` management command
- API: `GET /api/v1/social-handles/`, `GET /api/v1/drivers/{code}/social/`, `GET /api/v1/teams/{code}/social/`
- Phase 2 upgrade path: FK migrates to universal `Entity` model (PL-018)
- **Issue**: [DON-12 / PL-010]

### 2.2 Open Live Data Integration (Active) — PL-006
Ensuring stable telemetry flow using open-source data streams (OpenF1).
- **Issue**: [DON-5 / PL-006]

### 2.3 2026 Schema Sync (Planned) — PL-003
Updating the grid to reflect the 2026 Audi/Sauber transition and driver transfers.
- **Issue**: [DON-7 / PL-003]

### 2.4 News & Intelligence (Active)
Real-time news aggregation from multiple sources with automated translation and entity extraction.

**RSS Pipeline:**
- 21/21 sources scheduled in Celery Beat (was 8/21)
- Robust XML fetcher: `requests` + `_clean_xml()` + feedparser fallback
- Broken feed URLs fixed (The Race, Motorsport-Total, F1GrandPrix.it, Headliner.nl)
- Inactive sources: sportsv-f1 (URL dead), planetf1 (RSS removed)
- FIA Press Release source added (priority=98, 5-min fetch interval)

**Translation:**
- Target languages: 10 (en, zh-TW, zh-CN, es, pt-BR, it, nl, de, ja, fr) — was 4
- `confidence_score`, `translator`, `published_at` fields now correctly populated
- CLI backfill path: `translate_cli` management command via Claude Code subprocess (PL-028)

**Entity Extraction:**
- Hybrid approach: Regex fallback in absence of spaCy (Python 3.13 compatible)
- Phase 2 upgrade: query universal `Entity` table (PL-018)

**Frontend:**
- Dynamic article loading with language fallback (zh-TW default)
- Category pill tabs: horizontal scrollable filter, `GET /api/v1/categories/?lang=`
- Design token system: Tailwind v4 `@theme` with F1 brand + team colors (see §4)

### 2.5 Frontend Design System (Active)
- **Fonts**: DM Serif Display (headlines) + Plus Jakarta Sans (body)
- **Tailwind v4 Design Tokens**: `--color-f1-red`, `--color-f1-red-dark`, `--color-f1-red-light`,
  all 10 team colors, semantic surfaces, 8px spacing grid, 1200px content width
- **Component Updates**: ArticleCard, Layout, index page all migrated to token classes
- **Category Pills**: `CategoryPills` component with loading skeleton + active filter state

---

## 3. Deferred Visions (Backlog)
The following are high-value features postponed to Phase 2/3:
- **F1 TV Pro SignalR Client**: High-fidelity official stream (Requires paid account) — PL-025
- **Social Media Intelligence**: VLM-based OCR and relationship discovery from screenshots/stories
- **Historical RAG**: Vectorizing 70+ years of F1 history — PL-015
- **Temporal Race State Machine**: `RaceTemplate` heritage + `IncidentVerdict` news bridge — PL-027

---

## 4. Technical Architecture

### 4.1 Stack
- **Backend**: Django 5.x + Celery + Redis + Postgres
- **Frontend**: React 19 + Vike SSR + Tailwind 4 + Base UI v1.2.0
- **Entity Model**: Per-type Phase 1 schema; migrating to JSONB-powered universal `Entity` (PL-018)

### 4.2 Frontend Design Tokens (`frontend/styles/index.css`)
```css
@theme {
  --font-sans:    'Plus Jakarta Sans', system-ui, sans-serif;
  --font-display: 'DM Serif Display', Georgia, serif;

  --color-f1-red:       #e11d48;
  --color-f1-red-dark:  #be123c;
  --color-f1-red-light: #fb7185;

  /* Team colors: redbull, ferrari, mercedes, mclaren, astonmartin,
                  alpine, williams, rb, sauber, haas */

  --color-surface:        #ffffff;
  --color-surface-muted:  #f8fafc;
  --color-border:         #e2e8f0;
}
```

### 4.3 API Surface (`/api/v1/`)
| Endpoint | Description |
|---|---|
| `articles/` | Paginated article list (filterable by `category`, `lang`) |
| `articles/{slug}/` | Article detail with translations |
| `articles/breaking/` | Priority CRITICAL/HIGH articles |
| `categories/` | Active news categories with translations |
| `drivers/` / `teams/` | Entity lists |
| `f1/live/` | Live race session state |
| `f1/standings/` / `f1/schedule/` | Championship data |
| `social-handles/` *(planned)* | Paddock social registry |
