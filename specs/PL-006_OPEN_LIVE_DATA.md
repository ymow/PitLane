# Design Spec: PL-006 Open Live Data Integration

## 1. Objective
Maintain a functional real-time telemetry dashboard using the open-source OpenF1 API.

## 2. Integration Architecture
- **Source**: `api.openf1.org`
- **Backend Role**: Provide `session_key` via `/api/v1/f1/live/` endpoint.
- **Frontend Role**: React hook `useOpenF1` polls the API every 2s with incremental time filters.

## 3. Data Flow
1. API provides active `session_key`.
2. Frontend fetches `car_data` starting from `now - 10 minutes`.
3. `LiveTelemetryWidget` renders Speed, RPM, Gear, and Throttle data.

## 4. Known Constraints
- Polling-based (not WebSocket).
- Latency typically 2-5 seconds behind live F1 TV broadcast.
