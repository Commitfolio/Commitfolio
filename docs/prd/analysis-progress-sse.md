# Analysis Progress SSE PRD

## Metadata
- Title: Analysis progress SSE
- Owner: Codex
- Status: Done
- Target milestone: Public MVP / Stage 4
- Related issue: #8
- Related task doc: `docs/tasks/analysis-progress-sse.md`

## Problem
Commitfolio now writes durable job events during GitHub evidence ingestion, but the frontend still relies on request/response updates rather than realtime progress. Users need visible analysis progress, and the system must tolerate dropped SSE connections by replaying events from the database.

## User
- Primary user: A signed-in Commitfolio user running analysis for a selected repository.
- Trigger: The user starts analysis and expects progress/status feedback.
- Current pain: Analysis completion can be shown only after the run request returns; missed realtime updates have no UI channel.

## Goal
- Backend exposes an SSE endpoint that streams current job snapshot, replayed missed events, and live events.
- Frontend subscribes with EventSource, stores last seen sequence per job, and reconnects with `?after=`.
- Completed/failed events update the visible job state.
- `analysis_jobs` and `analysis_job_events` remain the source of truth.

## Non-goals
- Replacing the database event log with in-memory pub/sub.
- Background worker architecture.
- Portfolio result generation.
- Redis/WebSocket infrastructure.

## Scope
### In scope
- `GET /api/v1/analysis-jobs/{job_id}/events?after=<sequence>`.
- `Last-Event-ID` support when `after` is absent.
- SSE formatting with `id`, `event`, and JSON `data` lines.
- Snapshot event on connect.
- Replay events after the requested sequence.
- Short live polling loop for new DB events until terminal state or idle timeout.
- Frontend EventSource subscription using credentials.
- Frontend last-sequence persistence in sessionStorage.
- Tests for backend replay and frontend subscription handling.

### Out of scope
- Infinite worker-grade streaming loop.
- Redis Streams or fanout optimization.
- Multi-tab synchronization beyond sessionStorage.

## User Flow
1. User creates an analysis job.
2. Frontend opens the SSE progress stream for that job.
3. Backend sends a `snapshot` event.
4. Frontend starts analysis.
5. Backend persists events while analysis runs.
6. SSE stream replays/streams events and frontend updates status/progress.
7. If the connection drops, frontend reconnects with the last seen sequence.
8. On `job_completed` or `job_failed`, frontend closes the stream and fetches evidence summary when relevant.

## Functional Requirements
- The backend must require authentication and job ownership.
- The backend must send `snapshot` first without advancing event sequence.
- The backend must replay `AnalysisJobEvent.sequence > after`.
- The backend must use `Last-Event-ID` when `after` is not supplied.
- The backend must return `text/event-stream` with no-cache headers.
- The frontend must store last sequence under a job-specific key.
- The frontend must use `withCredentials: true` for EventSource.
- The frontend must update progress/status from `progress`, `job_completed`, and `job_failed` events.
- The frontend must not treat SSE as source of truth; refresh/status APIs remain recovery path.

## UX / UI Notes
- Entry point: analysis job card in `apps/frontend/src/App.tsx`.
- Empty/loading/error states: disconnected, connecting, streaming, closed, error.
- Editing constraints: keep UI minimal and status-focused; result rendering belongs to later stages.

## API / Backend Notes
- Endpoint: `GET /api/v1/analysis-jobs/{job_id}/events?after=<sequence>`.
- Auth / permissions: active session and job owner required.
- Background processing: none; streams events already persisted by Stage 3 run.
- SSE / polling behavior: DB replay plus bounded polling for live inserts.

## Data / Domain Notes
- Tables or entities touched:
  - `analysis_jobs`
  - `analysis_job_events`
- External APIs touched: none directly.
- Stored artifacts: no new tables; consumes Stage 3 event log.

## Acceptance Criteria
- [ ] SSE endpoint streams snapshot and replayed events.
- [ ] `after` and `Last-Event-ID` both work for replay.
- [ ] Frontend stores last seen sequence per job.
- [ ] Frontend updates status/progress on completed/failed events.
- [ ] Stage 4 docs and roadmap are updated.
- [ ] Frontend and backend verification commands pass.

## Verification Plan
- Unit: backend pytest for snapshot/replay/ownership; frontend vitest for EventSource handling.
- Integration: frontend lint/typecheck/build; backend compileall.
- Manual: With local OAuth credentials, create job, subscribe, run analysis, confirm progress and replay.

## Risks
- EventSource behavior in tests differs from real browsers.
- Synchronous ingestion can finish quickly, so most MVP streams may appear as replay rather than long-lived live updates.
- Browser manual test still depends on local OAuth credentials.

## Open Questions
- Should future worker execution push events through an in-process notifier or keep DB polling until scale requires Redis?
- How long should `analysis_job_events` be retained after completion?

## Approval
- Requested by: project owner via `$ralph Stage 4 끝까지 구현하고 검증까지 해줘`
- Approved by: Ralph execution request
- Approved at: 2026-04-15
