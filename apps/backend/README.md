# Commitfolio Backend

FastAPI backend for Commitfolio's auth and repository-selection MVP slices.

## Local development

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/uvicorn app.main:app --reload
```

## GitHub OAuth scopes

Stage 1 lists repositories the signed-in user can access. GitHub OAuth Apps require the broad
`repo` scope to include private repositories, so the local `.env.example` uses:

```bash
GITHUB_SCOPE="read:user repo read:org"
```

This is intentionally documented as a tradeoff. A later hardening pass should evaluate a GitHub App
or another fine-grained permission model before public launch.

## Request logging and error handling

Commitfolio logs application-level request lifecycle events with a request id:

- `request_started request_id=... method=... path=...`
- `request_finished request_id=... method=... path=... status_code=... duration_ms=...`
- unexpected exceptions include `unhandled_exception request_id=...` and return a safe Korean error envelope.

Optional logging level:

```bash
LOG_LEVEL=INFO
```

Responses include `X-Request-ID` so frontend/user reports can be matched with backend logs.

## Stage 1 API

- `GET /api/v1/repositories?visibility=all|public|private`
  - Requires a signed-in session.
  - Uses a server-side in-memory token map keyed by the signed session cookie.
  - Returns repository metadata only; deeper commit/PR/issue/review/changed-file collection belongs
    to later analysis stages.

## Stage 2 persistence and analysis jobs

Local development defaults to SQLite:

```bash
DATABASE_URL=sqlite:///./commitfolio.db
```

For Neon/PostgreSQL, use a SQLAlchemy-compatible psycopg URL:

```bash
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

Run migrations from `apps/backend`:

```bash
.venv/bin/alembic upgrade head
```

Stage 2 endpoints:

- `POST /api/v1/analysis-jobs`
  - Requires a signed-in session.
  - Stores/updates a `RepositorySnapshot`.
  - Creates a queued `AnalysisJob`.
- `GET /api/v1/analysis-jobs/{job_id}`
  - Returns current job status, progress placeholder, result id, and failure reason.
  - Jobs remain `queued` until later stages add evidence ingestion and progress updates.

## Stage 3 evidence ingestion

Stage 3 runs bounded GitHub evidence ingestion synchronously for the MVP baseline:

- `POST /api/v1/analysis-jobs/{job_id}/run`
  - Requires a signed-in session and active server-side GitHub token.
  - Clears prior evidence/events for that job before rerun.
  - Collects recent commits, pull requests, issues, reviews, and changed files.
  - Stores normalized `AnalysisEvidence` rows.
  - Appends ordered `AnalysisJobEvent` rows for future SSE replay.
- `GET /api/v1/analysis-jobs/{job_id}/evidence`
  - Returns evidence counts plus recent event log entries.

Jobs transition from `queued` to `running` and then `completed` or `failed`. Stage 4 should expose
the durable event log through SSE; the event log, not the live SSE connection, is the source of truth
for replay.

## Stage 7 optional OpenAI result enhancement

Result generation remains deterministic by default. To enable optional OpenAI post-processing, set:

```bash
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_TIMEOUT_SECONDS=8
```

If `OPENAI_API_KEY` is absent, invalid, times out, or returns an invalid response, Commitfolio stores the rule-based result and marks the response as fallback/non-configured instead of failing the result flow.

## Stage 4 SSE progress replay

Stage 4 exposes the durable event log over SSE:

- `GET /api/v1/analysis-jobs/{job_id}/events?after=<sequence>`
  - Requires a signed-in session.
  - Sends a `snapshot` event first.
  - Replays `analysis_job_events` with `sequence > after`.
  - Uses `Last-Event-ID` when `after` is absent.
  - Emits heartbeat events while waiting for new DB events.
  - Closes on `job_completed` or `job_failed`.

SSE is a delivery channel only. `analysis_jobs` remains the current-state snapshot and
`analysis_job_events` remains the replay source of truth.

## Stage 5 portfolio results

Stage 5 generates a deterministic portfolio draft from stored analysis evidence:

- `POST /api/v1/analysis-jobs/{job_id}/result`
  - Requires a signed-in session.
  - Requires the job to be owned by the current user and completed.
  - Generates and stores a rule-based `PortfolioResult` without OpenAI.
  - Updates `analysis_jobs.result_id` to the latest generated result.
- `GET /api/v1/results`
  - Returns recent portfolio results for the current user.
- `GET /api/v1/results/{result_id}`
  - Returns a stored result, sections, and evidence links.

The result shape includes headline, project overview, role summary, key contributions, tech stack,
evidence summary, interview questions, and section-level evidence links. Editing, regenerate, and PDF
export belong to later stages.
