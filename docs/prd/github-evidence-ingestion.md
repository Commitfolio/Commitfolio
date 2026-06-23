# GitHub Evidence Ingestion PRD

## Metadata
- Title: GitHub evidence ingestion
- Owner: Codex
- Status: Done
- Target milestone: Public MVP / Stage 3
- Related issue: #6
- Related task doc: `docs/tasks/github-evidence-ingestion.md`

## Problem
Commitfolio can create a queued analysis job for a selected repository, but the job does not yet collect any GitHub evidence. Portfolio generation needs durable normalized records for commits, PRs, issues, reviews, and changed files. Stage 4 SSE also needs a replayable progress/event log so realtime delivery is not the source of truth.

## User
- Primary user: A signed-in Commitfolio user who created an analysis job for a selected repository.
- Trigger: The user wants to run analysis for that repository.
- Current pain: Jobs remain queued forever and no reusable evidence exists for later portfolio result generation.

## Goal
- A queued `AnalysisJob` can be executed synchronously for the MVP baseline.
- GitHub evidence is collected and stored in a stable `AnalysisEvidence` shape.
- Job status transitions and failure reasons are persisted.
- `AnalysisJobEvent` records are appended with monotonic sequence numbers for later SSE replay.

## Non-goals
- SSE endpoint implementation.
- Background worker/queue infrastructure.
- Portfolio text generation.
- Exhaustive GitHub history ingestion. Stage 3 collects bounded, recent evidence for MVP speed.
- LLM summarization.

## Scope
### In scope
- `analysis_evidence` model and migration.
- `analysis_job_events` model and migration.
- `POST /api/v1/analysis-jobs/{job_id}/run` endpoint.
- `GET /api/v1/analysis-jobs/{job_id}/evidence` endpoint for verification/UI summary.
- GitHub REST calls for recent commits, pull requests, issues, reviews, and changed files.
- Evidence normalization with `source_type`, `source_id`, `url`, and `payload_json`.
- Job status updates: `queued -> running -> completed` or `failed`.
- Event log entries for snapshot/progress/completed/failed events.
- Frontend run-analysis button and evidence count/status summary.

### Out of scope
- SSE streaming/replay endpoint.
- Pagination beyond bounded MVP limits.
- Portfolio result generation.
- Long-running async worker architecture.

## User Flow
1. User signs in, selects a repository, and creates an analysis job.
2. User clicks “Run analysis”.
3. Backend transitions the job to `running` and appends a `job_started` event.
4. Backend collects bounded GitHub evidence for commits, PRs, issues, reviews, and changed files.
5. Backend stores normalized evidence and progress events.
6. Backend marks the job `completed`, or `failed` with a failure reason.
7. Frontend shows job status, evidence counts, and the latest event summary.

## Functional Requirements
- The backend must require authentication for run/evidence endpoints.
- Only the owner of an analysis job may run or inspect it.
- Running an already completed job should be idempotent enough for MVP: clear old evidence/events and rerun from stored repository snapshot.
- GitHub API failures must transition the job to `failed` and store `failure_reason`.
- Permission/rate limit/empty repository cases must be distinguishable in event/failure payloads where possible.
- Evidence payloads must be JSON-serializable and bounded.
- Event sequences must be monotonic per job and start at 1 after each run.
- The frontend must not rely on SSE; it should use the run response and evidence summary endpoint.

## UX / UI Notes
- Entry point: Stage 2 analysis job card in `apps/frontend/src/App.tsx`.
- Empty / loading / error states: no job selected, analysis running, analysis failed, no evidence collected.
- Editing constraints: keep Stage 3 as a status/summary UI; detailed progress streaming belongs to Stage 4.

## API / Backend Notes
- Endpoints:
  - `POST /api/v1/analysis-jobs/{job_id}/run`
  - `GET /api/v1/analysis-jobs/{job_id}/evidence`
- Auth / permissions: active session and job owner required.
- Background processing: synchronous bounded ingestion in this slice.
- SSE / polling behavior: none; event log exists for Stage 4.

## Data / Domain Notes
- Tables or entities touched:
  - `analysis_jobs`
  - `analysis_evidence`
  - `analysis_job_events`
- External APIs touched:
  - GitHub REST commits/list
  - GitHub REST pulls/list
  - GitHub REST issues/list
  - GitHub REST pull reviews/list
  - GitHub REST pull files/list
- Stored artifacts: normalized evidence and replayable job events.

## Acceptance Criteria
- [ ] A queued job can be run and transitions to completed with evidence rows.
- [ ] Commit/PR/issue/review/changed-file evidence types are represented.
- [ ] Job failure persists `failure_reason` and a failed event.
- [ ] Event log sequences are monotonic per job.
- [ ] Evidence summary endpoint returns counts and recent events.
- [ ] Frontend can trigger analysis and show evidence summary.
- [ ] PRD/task/.omx plan artifacts exist and point to issue #6.
- [ ] Frontend and backend verification commands pass.

## Verification Plan
- Unit: backend pytest for run/evidence success and failure paths; frontend vitest for run-analysis UI.
- Integration: frontend lint/typecheck/build; Alembic migration smoke against SQLite.
- Manual: With local OAuth credentials, create job, run analysis, confirm status/evidence counts.

## Risks
- GitHub rate limits or repository permissions can cause partial/failed ingestion.
- Synchronous ingestion is acceptable for bounded MVP data but not a final long-running architecture.
- GitHub REST response shapes may differ for private/org repos.

## Open Questions
- Should Stage 4 stream directly from `analysis_job_events` or include a separate live publisher abstraction?
- What bounded limits are enough for portfolio quality before pagination expansion?

## Approval
- Requested by: project owner
- Approved by: implicit roadmap execution request
- Approved at: 2026-04-15
