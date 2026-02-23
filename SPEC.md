# PitLane: Universal Domain Intelligence Engine — Master Spec

**Last Updated:** 2026-02-22

---

## 1. Vision & Core Principles

PitLane is a **Universal Domain Intelligence Engine** — an LLM-driven, graph-based CMS template that can be instantiated for any knowledge-intensive domain. Formula 1 is the **first pilot scenario** used to validate the architecture at its limits.

> "From F1 Paddock to Hollywood Red Carpet: One Engine, Infinite Intelligence."

### The Problem We Solve

Traditional CMS and news aggregators suffer three fundamental failures:

1. **Flat & Siloed** — Data is treated as static text. The system knows "Ferrari won" but cannot link it to "the 2008 financial crisis that forced Honda to exit" or "the karting rivalry between two drivers two decades earlier."
2. **Domain Rigidity** — A system built for F1 cannot be repurposed for cinema analysis without rewriting 80% of the codebase. There is no universal "Entity-Relationship-Skill" template.
3. **No God Mode** — Traditional systems only process official news, ignoring social media (Instagram Stories, X/Twitter), human networks (relationships, feuds, mentors), historical context (Wikipedia, regulations), and hard data (telemetry, box office figures).

### North Star

Build a **Domain Digital Twin Engine** that synchronizes real-time data, social signals, and 70+ years of historical context into a single "War Room" experience — starting with F1, extensible to any domain.

---

## 2. Four Core Pillars

### Pillar 1 — Real-time Race Sync 🏎️
The system is not a news site; it **reconstructs the race in the database**. When the lights go out, every car's telemetry, gap, tyre life, and DRS state is mirrored in real time.
- Sub-second OpenF1 telemetry sync (Speed, RPM, Gear, Throttle, G-force, DRS)
- Live driver position map + head-to-head performance delta (Norris vs. Verstappen)
- Anomaly detection → auto-trigger gossip search + draft incident report
- WebSocket / SSE push to frontend (no polling, no refresh)

### Pillar 2 — Global Intelligence 🌍
- AI-powered multi-language translation (10+ languages, F1-specialized terminology)
- Full-network monitoring: RSS → IG Stories → X/Twitter (2000+ accounts)
- Gossip/Tech classifier: distinguish "mechanic posting long-night photo" from "driver at party"

### Pillar 3 — LLM Contextual Engine 🧠
- **Causal Inference**: "Hamilton DNF" auto-linked to Silver Stone tyre pressure history + team budget cap status
- **Historical RAG**: Vectorized F1 books, Wikipedia, Technical Regulations → answer "Why does Ferrari hold a veto?"
- **Auto feature story**: Weekly LLM-generated deep-dive from current news + historical context

### Pillar 4 — Universal CMS Template 🛠️
- Domain-agnostic `Entity` + `Relationship` graph (replaces hardcoded `Driver`/`Team`)
- YAML template config to switch domains (`f1_template.yaml` → `movie_template.yaml`)
- Pluggable skill interface: `TelemetryAnalyzer` (F1), `BoxOfficeScraper` (Movies)

---

## 3. Execution Roadmap

### Phase 1 — Repair & Stabilize (F1 2026 Pilot) ← **Current**
Get the system "alive" and validated with real F1 2026 data.

| # | Spec | Status | Description |
|---|---|---|---|
| PL-003 | 2026 Schema Sync | **Done** | Audi/Sauber rebrand, 20-driver grid, contract management |
| PL-006 | Open Live Data | **Done** | OpenF1 telemetry integration |
| PL-010 | Paddock Social Registry | **Done** | 2000+ social handles for drivers, staff, teams |
| PL-019 | CRUD Management | **Done** | Teams, Drivers, Staff write API + Django Admin |
| — | News Pipeline | **Done** | 22 RSS sources (en×6, de×2, it×2, es×2, pt-BR×2, nl×2, fr×2, ja×1, tr×2, pl×1), 12-language AI translation |
| — | Frontend Design System | Active | Tailwind v4 tokens, ArticleCard, CategoryPills |
| #023 | zh-TW / zh-CN / ko Source Gap | Open | No active RSS found after deep search; zh-TW is zero-coverage |
| #024 | `de` Translation Parse Error | Open | Claude response occasionally returns malformed JSON for German |
| #027 | Celery Process Supervisor | Open | Worker + Beat require manual start; no systemd/supervisor config |

### Phase 2 — Graph & Abstraction
Transform the database from flat tables to a living entity graph.

| # | Spec | Description |
|---|---|---|
| PL-018 | Omni-Graph Entity Model | Replace hardcoded models with universal `Entity` + `Relationship` |
| Issue #009 | Paddock Graph | Track mechanics, TPs, race engineers, physios, WAGs, journalists |
| Issue #012 | Series & Role Mapping | One person → multiple roles (F2 driver + F1 reserve) |
| Issue #016 | Temporal Causal Graph | `Event` nodes with `CAUSED_BY` edges (e.g., Honda exit → 2008 crisis) |
| PL-027 | Temporal Infrastructure | `RaceTemplate` heritage + `IncidentVerdict` state machine |

### Phase 3 — Intelligence & Social
Connect the engine to the full information universe.

| # | Spec | Description |
|---|---|---|
| Issue #010 | Social Intelligence Ingestion | Twitter/X API, Instagram Graph API, Apify (Stories) |
| Issue #011 | Gossip/Tech Classifier | AI reads tone + image context to classify paddock signals |
| Issue #015 | Historical RAG | pgvector + F1 books + Wikipedia + regulations |
| Issue #017 | Auto Feature Story Generator | Weekly LLM deep-dive from current news + history |
| Issue #021 | Live Race State Machine | WebSocket/SSE high-concurrency backend, <1s latency |
| Issue #022 | Data-Content Correlation | Anomaly detection → auto gossip search → draft incident report |
| PL-028 | CLI Translation Command | Zero-API-cost Claude Code subprocess translation |

### Phase 4 — Template & Expand
Package F1 as a reusable template; validate on a second domain.

| # | Description |
|---|---|
| Issue #019 | Domain Template Configuration (YAML-driven domain switching) |
| Issue #020 | Agent Skill Interface (pluggable `Input → Process → Output` skills) |
| Issue #013 | Cross-Series Knowledge Engine (SeriesConfiguration for MotoGP, etc.) |
| — | Second domain pilot: MotoGP or Cinema |

---

## 4. Issue Backlog (Full)

### 🔴 Critical

| Issue | Title | Phase | Status |
|---|---|---|---|
| #001 | Environment dependency breakage (spaCy, feedparser, django_extensions) | 1 | **Done** |
| #006 | Live telemetry data sync broken for 2026 | 1 | **Done** |
| #009 | Paddock People Graph (TP, RE, Mechanic, WAG, journalist models) | 2 | Planned |
| #010 | Social media ingestion (Twitter/X, IG, Apify) | 3 |
| #012 | Entity role hierarchy & series mapping | 2 |
| #013 | Cross-series knowledge engine (SeriesConfiguration) | 4 |
| #015 | Historical contextual knowledge base (RAG) | 3 |
| #016 | Temporal causal graph (`Event` + `CAUSED_BY`) | 2 |
| #018 | Entity system abstraction (universal `Entity`/`Relationship`) | 2 |
| #019 | Domain template configuration (YAML) | 4 |
| #021 | Live race state machine (WebSocket/SSE, <1s latency) | 3 |
| #022 | Data-content correlation (anomaly → gossip → draft report) | 3 |

### 🟠 High

| Issue | Title | Phase | Status |
|---|---|---|---|
| #002 | Entity extractor offline — Regex fallback enabled | 1 | **Done** |
| #004 | News pipeline stale — fixed and fetching | 1 | **Done** |
| #007 | FastF1 post-race chart auto-generation failing | 1 | Planned |
| #008 | Breaking news classifier latency on race weekends | 1 |
| #011 | Gossip/Tech classifier (tone + image context) | 3 |
| #014 | Paddock Personnel Tracker dashboard in CMS | 2 |
| #017 | Auto feature story generator (weekly LLM deep-dive) | 3 |
| #020 | Agent skill interface (pluggable skills) | 4 |
| #023 | zh-TW / zh-CN / ko RSS gap — no active feed found | 1 | Open |
| #024 | `de` translation JSON parse error — intermittent Claude response malformed | 1 | Open |

### 🟡 Medium / Low

| Issue | Title | Phase |
|---|---|---|
| ~~#003~~ | ~~2026 season data sync (Audi/Sauber, driver transfers)~~ — **Done** | 1 |
| #005 | DB model field inconsistency (`original_title` vs `title`) | 1 |
| #025 | racefans RSS teaser-only — 9.3 avg quality, never reaches translation gate | 1 |
| #026 | spaCy NER deferred to Phase 3 — Regex keyword match is Phase 1 approach | 3 |
| #027 | Celery worker / Beat require manual startup — no process supervisor configured | 1 |

---

## 5. Technical Architecture

### 5.1 Stack
| Layer | Technology |
|---|---|
| Backend | Django 5.x + Celery + Redis + PostgreSQL |
| Frontend | React 19 + Vike (SSR) + Tailwind v4 + Base UI v1.2.0 |
| AI | Anthropic Claude API (translation, inference, story gen) |
| NER | spaCy (entity extraction) + SimHash (deduplication) |
| Live Data | OpenF1 (real-time telemetry) + Jolpica/FastF1 (historical) |
| Vector DB | pgvector (Phase 3 RAG) |
| Dev Workflow | Spec-driven via Superpowers + Linear.app |

### 5.2 Current Entity Model (Phase 1)
Per-type, concrete models. Migrates to universal `Entity` graph in Phase 2 (PL-018).

```
Team ──< DriverContract >── Driver
  |                              |
  └──< TeamSponsor            social_handles
  |
  └──< SocialHandle
```

`DriverContract` now covers both drivers (RACE/RESERVE/TEST/DEV/LOAN/GUEST) and staff (TEAM_PRINCIPAL/TECHNICAL_DIRECTOR/RACE_ENGINEER/PERFORMANCE_ENGINEER/HEAD_AERO/MECHANIC/STAFF).

### 5.3 Target Entity Model (Phase 2 — PL-018)
```
Entity(name, type, attributes JSONB)
  └──< Relationship(source, target, type, weight, start_date, end_date) >── Entity

Examples:
  Entity(Verstappen, DRIVER) --[DRIVES_FOR]--> Entity(Red Bull, TEAM)
  Entity(Verstappen, DRIVER) --[RIVALS]------> Entity(Norris, DRIVER)
  Entity(Nolan, PERSON)      --[CASTS]-------> Entity(Murphy, PERSON)  ← Movie domain
```

### 5.4 Frontend Design Tokens (`frontend/styles/index.css`)
```css
@theme {
  --font-sans:    'Plus Jakarta Sans', system-ui, sans-serif;
  --font-display: 'DM Serif Display', Georgia, serif;

  --color-f1-red:       #e11d48;
  --color-f1-red-dark:  #be123c;
  --color-f1-red-light: #fb7185;

  /* Team colors: redbull, ferrari, mercedes, mclaren, astonmartin,
                  alpine, williams, rb, audi (#BB0000), haas */

  --color-surface:        #ffffff;
  --color-surface-muted:  #f8fafc;
  --color-border:         #e2e8f0;
}
```

### 5.5 API Surface (`/api/v1/`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `articles/` | GET | Public | Paginated article list |
| `articles/{slug}/` | GET | Public | Article detail with translations |
| `articles/breaking/` | GET | Public | Priority CRITICAL/HIGH articles |
| `categories/` | GET | Public | Active news categories |
| `drivers/` | GET | Public | Driver list |
| `drivers/{code}/` | GET/PUT/PATCH/DELETE | Admin (write) | Driver CRUD |
| `drivers/{code}/articles/` | GET | Public | Articles by driver |
| `drivers/{code}/social/` | GET | Public | Social handles by driver |
| `teams/` | GET | Public | Team list |
| `teams/{code}/` | GET/PUT/PATCH/DELETE | Admin (write) | Team CRUD |
| `teams/{code}/articles/` | GET | Public | Articles by team |
| `teams/{code}/social/` | GET | Public | Social handles by team |
| `contracts/` | GET | Public | Driver + staff contracts (filterable by `role`, `team`, `is_active`) |
| `contracts/{id}/` | POST/PATCH/DELETE | Admin (write) | Contract CRUD |
| `social-handles/` | GET | Public | Paddock social registry |
| `f1/live/` | GET | Public | Live race session state |
| `f1/standings/` | GET | Public | Championship standings |
| `f1/schedule/` | GET | Public | Race schedule |
| `f1/results/` | GET | Public | Race results |

---

## 6. Spec Index

| Spec File | Status | Description |
|---|---|---|
| `specs/PL-003_2026_SCHEMA_SYNC.md` | **Done** | 2026 grid update |
| `specs/PL-006_OPEN_LIVE_DATA.md` | Active | OpenF1 integration |
| `specs/PL-010_SOCIAL_REGISTRY.md` | Active | Paddock social handles |
| `specs/PL-018_OMNI_GRAPH_ENTITY_MODEL.md` | Planned (Phase 2) | Universal entity model |
| `specs/PL-025_DEFERRED_LIVE_CLIENT.md` | Deferred | F1 TV Pro SignalR |
| `specs/PL-027_TEMPORAL_INFRASTRUCTURE.md` | Planned (Phase 2) | Race state machine |
| `specs/PL-028_CLI_TRANSLATION_COMMAND.md` | Planned (Phase 3) | CLI translation |
