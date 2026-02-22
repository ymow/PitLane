# PitLane: Omni-Graph Intelligence Engine

PitLane is a **Universal Domain Intelligence Engine** — an LLM-driven, graph-based CMS that reconstructs complex industries in real time. Formula 1 is the first pilot scenario. The same architecture can be switched to MotoGP, cinema, or finance by swapping a YAML config file.

> "From F1 Paddock to Hollywood Red Carpet: One Engine, Infinite Intelligence."

---

## Why PitLane is Different

Traditional news platforms report *what* happened. PitLane answers *why* — by fusing real-time telemetry, paddock social signals, and 70+ years of historical context into a single LLM-driven War Room.

| Capability | Traditional CMS | PitLane |
|---|---|---|
| News aggregation | ✅ | ✅ |
| Multi-language | ❌ | ✅ 10+ languages |
| Live race telemetry | ❌ | ✅ Sub-second sync |
| Causal inference ("why Honda left") | ❌ | ✅ RAG + LLM |
| Paddock social monitoring (IG Stories) | ❌ | ✅ 2000+ accounts |
| Entity relationship graph | ❌ | ✅ Driver → WAG → Legend |
| Cross-domain template | ❌ | ✅ F1 → Movies → Finance |

---

## Four Core Pillars

**🏎️ Real-time Race Sync** — When lights go out, every car's telemetry is mirrored in the database. WebSocket push to frontend. Anomaly detection triggers automatic incident reports.

**🌍 Global Intelligence** — Claude AI translates with F1-specific terminology across 10+ languages. 2000+ paddock accounts monitored across X, Instagram, and TikTok.

**🧠 LLM Contextual Engine** — Historical RAG over regulations, Wikipedia, and F1 books. Causal inference links breaking news to decades of context. Auto-generates weekly deep-dive articles.

**🛠️ Universal CMS Template** — Domain-agnostic `Entity` + `Relationship` graph. Pluggable skill system. Switch domains by loading a new YAML config.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.x · Celery · Redis · PostgreSQL |
| Frontend | React 19 · Vike SSR · Tailwind CSS v4 · Base UI |
| AI | Anthropic Claude API (translation, inference) |
| NER | spaCy · SimHash |
| Live Data | OpenF1 (real-time) · Jolpica · FastF1 (analysis) |
| Vector DB | pgvector (Phase 3) |
| Dev Workflow | Spec-driven · Linear.app |

---

## Roadmap

| Phase | Focus | Status |
|---|---|---|
| **Phase 1** | F1 2026 Pilot — news pipeline, live telemetry, social registry, 2026 grid | 🟡 In Progress |
| **Phase 2** | Graph & Abstraction — universal Entity model, paddock people graph, causal graph | ⚪ Planned |
| **Phase 3** | Intelligence — social ingestion, historical RAG, live race state machine | ⚪ Planned |
| **Phase 4** | Template & Expand — YAML domain config, skill interface, second domain pilot | ⚪ Planned |

See [SPEC.md](./SPEC.md) for the full issue backlog and technical architecture.

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Database Seeding (2026 Season)

Run these commands in order to fully populate a fresh database with the 2026 F1 season data.

### Step 1 — Base data (teams, drivers, news categories, RSS sources)

```bash
cd backend
python manage.py seed_data
```

Creates 10 teams, 20 drivers, 8 news categories, and all RSS feed sources.

### Step 2 — 2026 grid sync (Audi rebrand + RACE contracts)

```bash
python manage.py seed_2026_grid
```

- Renames the Kick Sauber entry → **Audi F1 Team** (code `AUD`, color `#BB0000`)
- Creates 20 `DriverContract(role=RACE)` rows linking each driver to their 2026 team

The 2026 driver lineup:

| Team | Drivers |
|---|---|
| Red Bull Racing | Max Verstappen, Liam Lawson |
| Scuderia Ferrari | Charles Leclerc, Lewis Hamilton |
| McLaren F1 Team | Lando Norris, Oscar Piastri |
| Mercedes-AMG Petronas | George Russell, Andrea Kimi Antonelli |
| Aston Martin Aramco | Fernando Alonso, Lance Stroll |
| Alpine F1 Team | Pierre Gasly, Jack Doohan |
| Williams Racing | Alexander Albon, Carlos Sainz |
| Racing Bulls | Yuki Tsunoda, Isack Hadjar |
| MoneyGram Haas F1 Team | Oliver Bearman, Esteban Ocon |
| Audi F1 Team | Nico Hülkenberg, Gabriel Bortoleto |

This command is **idempotent** — safe to run multiple times.

### Step 3 — Paddock staff contracts (Team Principals, engineers, etc.)

```bash
python manage.py seed_staff_contracts \
  --file data/staff_contracts_2026.json \
  --season 2026
```

Creates 37 staff contract entries: 10 Team Principals, 10 Technical Directors, 14 Race Engineers, and other paddock roles.

> **Note:** Must run Step 2 first. The staff data references team code `AUD`, which is created by the Audi rebrand in Step 2.

### Step 4 — 2026 race calendar (24 races)

```bash
python manage.py seed_2026_schedule
```

Populates the full 2026 race calendar with circuit data.

### Step 5 — Paddock social handles (optional)

```bash
python manage.py seed_social_handles \
  --file data/paddock_handles_2026.json
```

Seeds 2000+ social media handles for drivers, team principals, and paddock staff across X/Twitter, Instagram, and TikTok.

### Full reset (all steps at once)

```bash
cd backend
python manage.py seed_data && \
python manage.py seed_2026_grid && \
python manage.py seed_staff_contracts --file data/staff_contracts_2026.json --season 2026 && \
python manage.py seed_2026_schedule && \
python manage.py seed_social_handles --file data/paddock_handles_2026.json
```

---

## API Overview

Base URL: `http://localhost:8000/api/v1/`

| Endpoint | Description |
|---|---|
| `GET /teams/` | All 10 teams with color and logo |
| `GET /drivers/` | All 20 drivers |
| `GET /contracts/?role=RACE&is_active=true` | 2026 race grid with team colors |
| `GET /contracts/?role=TEAM_PRINCIPAL&is_active=true` | All team principals |
| `GET /social-handles/` | Paddock social registry |
| `GET /articles/` | News articles (supports `?lang=zh-TW`) |
| `GET /f1/standings/` | Championship standings |
| `GET /f1/schedule/` | Race calendar |

Write endpoints (`POST`, `PATCH`, `DELETE`) require admin authentication.

---

*Built for the 2026 F1 season. Designed for every domain beyond it.*
