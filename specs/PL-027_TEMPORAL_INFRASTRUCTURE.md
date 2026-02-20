# Design Spec: PL-027 F1 時空連結與事件裁決系統

## 1. Objective
Establish a multi-dimensional racing database that preserves historical context, links recurring events across decades, and integrates news-driven incidents (penalties, DSQs) into the official results timeline.

## 2. Data Models (Schema)

### 2.1 `RaceTemplate` (The Heritage Anchor)
Connects all instances of a specific Grand Prix across years.
- `id`: UUID
- `name`: e.g., "Monaco Grand Prix"
- `slug`: "monaco-gp"
- `first_held_year`: Integer (e.g., 1929)
- `description`: Historical summary of the event.

### 2.2 `IncidentVerdict` (The "News-to-Result" Bridge)
Records incidents that modify session outcomes, linked to rules and news.
- `id`: UUID
- `session`: FK to `Session`
- `entity`: FK to `Entity` (Driver/Team involved)
- `incident_type`: Enum (DSQ, TIME_PENALTY, GRID_DROP, INVESTIGATION)
- `reason_category`: Enum (TECHNICAL_INFRINGEMENT, DRIVING_CONDUCT, ADMINISTRATIVE)
- `description`: Textual detail (e.g., "Plank wear exceeds 10mm").
- **`impact_on_points`**: Float (Points lost or gained)
- **`related_articles`**: ManyToMany to `Article` (Provides the "Why" and "When")
- `regulatory_reference`: String (Link to specific FIA regulation code)

### 2.3 `Race` (Updated Association)
- Add FK `template` -> `RaceTemplate` to allow heritage tracking.

## 3. The State Machine: "Provisional to Official"
To handle post-race checks (like the McLaren plank thickness example):
1. **LIVE**: Real-time data flowing.
2. **PROVISIONAL**: Race ended, results published, but scrutineering in progress.
   - *UI Indicator*: "⚠️ Scrutineering in Progress".
3. **INCIDENT DETECTED**: If a technical infringement news is captured.
   - *Action*: Auto-create `IncidentVerdict` linked to the breaking news article.
4. **COMPLETED**: Investigation closed, `RaceResult` updated with revised positions.
5. **OFFICIAL**: Final validated results after any appeal periods.

## 4. UI/UX Vision (Temporal Navigation)
- **Time Machine Button**: On the 2026 Australian GP page, a sidebar shows "Historic Highlights" powered by the `RaceTemplate` link.
- **Verdict Banner**: If a race has an active `IncidentVerdict`, show a prominent banner linking to the news article explaining the penalty.

## 5. Operations
- **Heritage Seeding**: Create a management command to group existing `Race` objects by `RaceTemplate`.
- **Verdict CLI**: `python manage.py add-verdict --session <id> --driver "HAM" --type "DSQ" --news <id>`

## 6. Future-Proofing
- This structure supports the upcoming **Historical RAG (Issue #015)** by providing the structural links between events and documents.
