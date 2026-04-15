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

## Stage 1 API

- `GET /api/v1/repositories?visibility=all|public|private`
  - Requires a signed-in session.
  - Uses a server-side in-memory token map keyed by the signed session cookie.
  - Returns repository metadata only; deeper commit/PR/issue/review/changed-file collection belongs
    to later analysis stages.
