# Analysis Job Bootstrap PRD

## Metadata
- Title: Analysis job creation baseline
- Owner: Codex
- Status: Done
- Target milestone: Public MVP / Stage 2
- Related issue: #3
- Related task doc: `docs/tasks/analysis-job-bootstrap.md`

## Problem
Commitfolio can list and select a GitHub repository, but there is no persisted analysis job boundary yet. Downstream evidence ingestion, SSE progress, and portfolio result generation need a durable `AnalysisJob` record with a known repository target and status lifecycle. Without this baseline, the app cannot distinguish selected UI state from a server-side analysis request.

## User
- Primary user: A signed-in Commitfolio user who selected one repository in Stage 1.
- Trigger: The user chooses a repository and wants to start portfolio analysis.
- Current pain: Selecting a repo does not create a server-side job or status URL.

## Goal
- A selected repository can create a queued `AnalysisJob`.
- The backend persists a minimal `RepositorySnapshot` and `AnalysisJob` using the Stage 2 database baseline.
- The frontend can show the created job id and query current status.

## Non-goals
- Running GitHub evidence ingestion.
- Background workers or external queues.
- SSE streaming.
- Portfolio result generation.
- Full user/account persistence; the current OAuth session identity remains the owner key for this slice.

## Scope
### In scope
- SQLAlchemy 2.x persistence baseline.
- Alembic migration baseline.
- PostgreSQL/Neon-ready `DATABASE_URL` env documentation with SQLite local/test fallback.
- `repository_snapshots` and `analysis_jobs` models.
- `POST /api/v1/analysis-jobs` endpoint.
- `GET /api/v1/analysis-jobs/{job_id}` endpoint.
- Frontend job creation/status card after repository selection.
- Tests for job creation, lookup, ownership, and validation.

### Out of scope
- Stage 3 GitHub evidence collection.
- Stage 4 SSE progress stream.
- Analysis result rows.
- Production-grade background execution.

## User Flow
1. User signs in and selects a repository.
2. User clicks “Create analysis job”.
3. Frontend posts selected repository metadata to `POST /api/v1/analysis-jobs`.
4. Backend stores/updates the repository snapshot and creates a queued job.
5. Frontend displays the job id, status, repository, branch, and failure reason if any.
6. Frontend can refresh the job status with `GET /api/v1/analysis-jobs/{job_id}`.

## Functional Requirements
- The backend must require authentication for all analysis job endpoints.
- `POST /api/v1/analysis-jobs` must accept exactly one repository target.
- The backend must persist a repository snapshot for the authenticated session owner.
- The backend must create an analysis job with status `queued`.
- `GET /api/v1/analysis-jobs/{job_id}` must return status, repository target, branch, progress, result id, and failure reason.
- Jobs must be scoped to the current authenticated session owner.
- Unknown job ids must return a standard `analysis_job_not_found` error envelope.
- The frontend must create a job from the selected repository and show status without requiring evidence ingestion.

## UX / UI Notes
- Entry point: selected repository summary in `apps/frontend/src/App.tsx`.
- Empty / loading / error states: pending job creation, job creation error, job status refresh error.
- Editing constraints: keep this as a baseline control surface; detailed progress belongs to Stage 4.

## API / Backend Notes
- Endpoints:
  - `POST /api/v1/analysis-jobs`
  - `GET /api/v1/analysis-jobs/{job_id}`
- Auth / permissions: requires active session; job ownership uses current session user id.
- Background processing: none in this slice; jobs remain `queued` until later stages update lifecycle.
- SSE / polling behavior: simple status fetch only.

## Data / Domain Notes
- Tables or entities touched:
  - `repository_snapshots`
  - `analysis_jobs`
- External APIs touched: none during job creation.
- Stored artifacts: repository metadata snapshot and analysis job metadata.

## Acceptance Criteria
- [ ] `DATABASE_URL` exists in backend settings/env example.
- [ ] SQLAlchemy models and Alembic initial migration exist.
- [ ] A signed-in user can create a queued job for the selected repository.
- [ ] A signed-in user can fetch the created job status.
- [ ] Missing jobs and unauthenticated requests return standard errors.
- [ ] Frontend shows created job status from the backend.
- [ ] PRD/task/.omx plan artifacts exist and point to issue #3.
- [ ] Frontend and backend verification commands pass.

## Verification Plan
- Unit: `cd apps/backend && .venv/bin/python -m pytest tests`; `npm --prefix apps/frontend run test -- --run`.
- Integration: `npm --prefix apps/frontend run lint`; `npm --prefix apps/frontend run typecheck`; Alembic migration file import/render smoke where practical.
- Manual: Select a repository, create a job, refresh status, verify queued response and next-stage copy.

## Risks
- Adding persistence dependencies can break the lightweight bootstrap environment if the venv is not refreshed.
- SQLite fallback and PostgreSQL production URL can diverge if model types are not conservative.
- Job lifecycle is intentionally queued-only until Stage 3/4, which must be obvious in UI copy.

## Open Questions
- Should Stage 3 update jobs synchronously in-process or introduce a background worker boundary?
- Should Stage 2 PR be stacked on Stage 1 until the repository selector PR merges?

## Approval
- Requested by: project owner
- Approved by: implicit roadmap execution request
- Approved at: 2026-04-15
