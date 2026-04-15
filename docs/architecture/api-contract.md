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
      }
    }
  ],
  "next_cursor": null
}
```

## Analysis Jobs

### `POST /api/v1/analysis-jobs`
- Purpose: start analysis for one selected repository
- Request example:

```json
{
  "repository_full_name": "owner/repo",
  "branch": "main"
}
```

- Response example:

```json
{
  "job_id": "job_123",
  "status": "queued"
}
```

### `GET /api/v1/analysis-jobs/{job_id}`
- Purpose: fetch current job status and summary
- Response example:

```json
{
  "job_id": "job_123",
  "status": "running",
  "progress": {
    "stage": "collecting_pull_requests",
    "percent": 45
  },
  "result_id": null
}
```

### `GET /api/v1/analysis-jobs/{job_id}/events`
- Purpose: stream progress events over SSE
- Content type: `text/event-stream`
- Event examples:
  - `job_started`
  - `progress`
  - `job_failed`
  - `job_completed`

## Portfolio Results

### `GET /api/v1/results`
- Purpose: list saved analysis results for the current user

### `GET /api/v1/results/{result_id}`
- Purpose: fetch one stored portfolio result with evidence links

### `PATCH /api/v1/results/{result_id}`
- Purpose: persist user edits to generated text
- Request example:

```json
{
  "headline": "Backend-focused engineer who shipped repository-driven portfolio generation",
  "project_overview": "..."
}
```

### `POST /api/v1/results/{result_id}/regenerate`
- Purpose: rerun generation using stored evidence

### `GET /api/v1/results/{result_id}/download.pdf`
- Purpose: return a PDF export

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
