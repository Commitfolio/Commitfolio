# API Contract

This document defines the first-pass API shape for the FastAPI backend. Route names can change, but the resource boundaries should stay stable unless the PRD changes.

## Auth

### `GET /api/v1/auth/github/start`
- Purpose: start GitHub OAuth flow
- Response: redirect to GitHub authorize URL

### `GET /api/v1/auth/github/callback`
- Purpose: complete OAuth flow
- Input: GitHub `code`, optional `state`
- Side effects: store linked account / session
- Response: redirect back to frontend app

### `POST /api/v1/auth/logout`
- Purpose: end current session
- Response: `204 No Content`

### `GET /api/v1/me`
- Purpose: return current authenticated user summary
- Response example:

```json
{
  "id": "usr_123",
  "github_login": "example",
  "connected": true
}
```

- Unauthenticated response example:

```json
{
  "error": {
    "code": "unauthenticated",
    "message": "Authentication required."
  }
}
```

## Repositories

### `GET /api/v1/repositories`
- Purpose: list accessible repositories for the signed-in user
- Query params:
  - `visibility`: `all|public|private`
  - `cursor`: optional pagination cursor
- Response example:

```json
{
  "items": [
    {
      "id": 123,
      "full_name": "owner/repo",
      "private": true,
      "owner_type": "User",
      "default_branch": "main",
      "permissions": {
        "admin": false,
        "push": true,
        "pull": true
      },
      "html_url": "https://github.com/owner/repo",
      "description": "Example repository",
      "updated_at": "2026-04-15T00:00:00Z"
    }
  ],
  "next_cursor": null
}
```

- Auth / permissions:
  - Requires the current session created by GitHub OAuth.
  - Stage 1 keeps the GitHub access token in a server-side in-memory map keyed by a signed session
    token id. This is a pre-persistence bridge, not the final production storage model.
  - GitHub OAuth Apps require broad `repo` scope to include private repositories; keep this visible
    until a tighter GitHub App/fine-grained permission strategy is implemented.
- Error examples:

```json
{
  "error": {
    "code": "github_token_missing",
    "message": "GitHub session token is missing. Sign in again."
  }
}
```

## Analysis Jobs

### `POST /api/v1/analysis-jobs`
- Purpose: start analysis for one selected repository
- Request example:

```json
{
  "repository_full_name": "owner/repo",
  "branch": "main",
  "github_repo_id": 123,
  "private": true,
  "owner_type": "Organization",
  "default_branch": "main",
  "html_url": "https://github.com/owner/repo",
  "description": "Example repository"
}
```

- Response example:

```json
{
  "job_id": "job_123",
  "status": "queued",
  "repository_full_name": "owner/repo",
  "branch": "main",
  "progress": {
    "stage": "queued",
    "percent": 0
  },
  "result_id": null,
  "failure_reason": null
}
```

- Side effects:
  - Upserts a `RepositorySnapshot` for the current user/session owner.
  - Creates one `AnalysisJob` row in `queued` state.
  - Does not collect GitHub evidence yet.

### `GET /api/v1/analysis-jobs/{job_id}`
- Purpose: fetch current job status and summary
- Response example:

```json
{
  "job_id": "job_123",
  "status": "running",
  "repository_full_name": "owner/repo",
  "branch": "main",
  "progress": {
    "stage": "collecting_pull_requests",
    "percent": 45
  },
  "result_id": null,
  "failure_reason": null
}
```

- Not found response example:

```json
{
  "error": {
    "code": "analysis_job_not_found",
    "message": "Analysis job was not found."
  }
}
```

### `POST /api/v1/analysis-jobs/{job_id}/run`
- Purpose: run bounded GitHub evidence ingestion for one queued/existing job
- Behavior:
  - Clears previous evidence/events for the job before rerun.
  - Transitions the job to `running`.
  - Collects commits, pull requests, issues, reviews, and changed files.
  - Stores normalized `AnalysisEvidence` rows.
  - Appends `AnalysisJobEvent` rows with monotonic per-job `sequence`.
  - Marks the job `completed`, or `failed` with `failure_reason`.
- Response example:

```json
{
  "job": {
    "job_id": "job_123",
    "status": "completed",
    "repository_full_name": "owner/repo",
    "branch": "main",
    "progress": {
      "stage": "completed",
      "percent": 100
    },
    "result_id": null,
    "failure_reason": null
  },
  "evidence": {
    "job_id": "job_123",
    "total_count": 25,
    "counts": {
      "commit": 10,
      "pull_request": 5,
      "issue": 3,
      "review": 2,
      "changed_file": 5
    },
    "latest_events": [
      {
        "sequence": 7,
        "event_type": "job_completed",
        "stage": "completed",
        "percent": 100,
        "message": "Analysis evidence ingestion completed.",
        "payload_json": {
          "total_count": 25
        },
        "created_at": "2026-04-15T00:00:00+00:00"
      }
    ]
  }
}
```

### `GET /api/v1/analysis-jobs/{job_id}/evidence`
- Purpose: return evidence counts and recent job events for the current user
- Response: same `evidence` shape from the run response.

### `GET /api/v1/analysis-jobs/{job_id}/events`
- Purpose: stream progress events over SSE
- Content type: `text/event-stream`
- Query params:
  - `after`: optional last seen `analysis_job_events.sequence`; only events with greater sequence are replayed
- Header support:
  - `Last-Event-ID`: used as the replay cursor when `after` is absent
- Stream behavior:
  - Sends a `snapshot` event first with the current job response shape.
  - Replays durable `analysis_job_events` after the requested cursor.
  - Polls the database briefly for new events and emits `heartbeat` while waiting.
  - Closes after `job_completed` or `job_failed`, or after the bounded MVP stream window.
- Event examples:
  - `snapshot`
  - `job_started`
  - `progress`
  - `job_failed`
  - `job_completed`
  - `heartbeat`
- Event format example:

```text
id: 7
event: job_completed
data: {"job_id":"job_123","sequence":7,"stage":"completed","percent":100}
```

## Portfolio Results

### `POST /api/v1/analysis-jobs/{job_id}/result`
- Purpose: generate and store a deterministic portfolio result for a completed analysis job
- Behavior:
  - Requires the current user to own the completed job.
  - Reads stored `AnalysisEvidence`.
  - Stores `PortfolioResult` and section-level evidence links.
  - Updates `analysis_jobs.result_id` to the latest generated result.
- Response example:

```json
{
  "result_id": "res_123",
  "analysis_job_id": "job_123",
  "repository_full_name": "owner/repo",
  "version": 1,
  "headline": "owner/repo에서 근거 기반 개발 흐름을 완성한 프로젝트 경험",
  "project_overview": "...",
  "role_summary": "...",
  "key_contributions": ["..."],
  "tech_stack": ["Python", "React"],
  "evidence_summary": "commit 10개, pull_request 5개",
  "interview_questions": ["..."],
  "evidence_links": [
    {
      "section_key": "key_contributions",
      "label": "pull_request: Add API",
      "url": "https://github.com/owner/repo/pull/1",
      "evidence_id": "ev_123"
    }
  ],
  "created_at": "2026-04-15T00:00:00+00:00",
  "updated_at": "2026-04-15T00:00:00+00:00"
}
```

### `GET /api/v1/results`
- Purpose: list recent saved portfolio results for the current user
- Response example:

```json
{
  "items": [
    {
      "result_id": "res_123",
      "analysis_job_id": "job_123",
      "repository_full_name": "owner/repo",
      "headline": "owner/repo에서 근거 기반 개발 흐름을 완성한 프로젝트 경험",
      "version": 1,
      "created_at": "2026-04-15T00:00:00+00:00",
      "updated_at": "2026-04-15T00:00:00+00:00"
    }
  ]
}
```

### `GET /api/v1/results/{result_id}`
- Purpose: fetch one stored portfolio result with evidence links
- Response: same result shape from the generation response.

### `PATCH /api/v1/results/{result_id}`
- Purpose: persist user edits to generated text
- Status: planned for Stage 6
- Request example:

```json
{
  "headline": "Backend-focused engineer who shipped repository-driven portfolio generation",
  "project_overview": "..."
}
```

### `POST /api/v1/results/{result_id}/regenerate`
- Purpose: rerun generation using stored evidence
- Status: planned for Stage 6

### `GET /api/v1/results/{result_id}/download.pdf`
- Purpose: return a PDF export
- Status: planned for PDF export stage

## Error Shape

```json
{
  "error": {
    "code": "repository_access_denied",
    "message": "The selected repository is not accessible with the current token."
  }
}
```

## Contract Rules
- All write endpoints require authentication.
- Analysis targets exactly one repository per job.
- Result text is editable after generation.
- Evidence links should be stored at the sentence or section level when possible.
- Breaking API changes should update this file before implementation.
