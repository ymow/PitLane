# F1 Data Strategy: Hybrid Architecture (2025)

To support the 2025 season with both historical accuracy and real-time engagement, PitLane employs a hybrid data strategy integrating three specialized sources.

## 1. Architecture Overview

| Layer | Source | Purpose | Key Data |
| :--- | :--- | :--- | :--- |
| **Core / Truth** | **Jolpica (Ergast)** | Official Records & Schedule | Calendar, Results, Standings, Laps (Summary) |
| **Live (Frontend)** | **OpenF1** | Real-time Fan Engagement | Live Speed, RPM, Gear, Throttle, Gaps |
| **Analysis (Backend)** | **FastF1** | Deep Post-Race Insights | Telemetry Charts, Tyre Strategy, Pace Analysis |

## 2. Data Flow

### A. Core Pipeline (Jolpica)
*   **Frequency**: Post-session (Static).
*   **Mechanism**: `apps.fetcher.jolpica` fetches JSON -> `apps.processor.f1_normalizer` updates DB.
*   **Models**: `Race`, `Session`, `RaceResult`, `DriverStanding`.
*   **Trigger**: Management command or periodic Celery task.

### B. Live Pipeline (OpenF1)
*   **Frequency**: Real-time (~4Hz).
*   **Mechanism**: Direct Frontend-to-API connection (React Hook `useOpenF1`).
*   **Integration**: The backend `Session` model stores an `openf1_session_key`. The frontend uses this key to poll `api.openf1.org` only when a session is active.
*   **Storage**: Ephemeral (Frontend state only). No heavy database writes.

### C. Analysis Pipeline (FastF1)
*   **Frequency**: Post-race (One-off).
*   **Mechanism**: `apps.analysis.fastf1_service` downloads full session cache.
*   **Output**: Generates static chart images (e.g., "Verstappen vs Hamilton Pace") and saves them to `RaceResult.telemetry_chart`.
*   **Trigger**: Automatically triggered by `F1DataNormalizer` when Jolpica marks a race as "Completed".

## 3. Implementation Status

### ✅ Completed
- [x] **Jolpica Client**: Fetcher and Normalizer implemented.
- [x] **Hybrid Models**: `Session` updated with `openf1_session_key`; `RaceResult` updated with `telemetry_chart`.
- [x] **FastF1 Service**: Comparison chart generation implemented (`backend/apps/analysis`).
- [x] **Live Widget**: React component `LiveTelemetryWidget` connected to OpenF1.
- [x] **Orchestration**: Automated analysis trigger after result sync.

### 🔜 Future Work
- [ ] **Predictive AI**: Use FastF1 historical data to train race strategy models.
- [ ] **Enhanced Live**: WebSocket proxy for OpenF1 to reduce client-side polling.
