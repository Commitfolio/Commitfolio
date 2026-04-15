# Analysis Job Bootstrap Task

## Summary
- Title: Analysis job creation baseline
- Status: Done
- Owner: Codex
- Issue: #3
- PRD: `docs/prd/analysis-job-bootstrap.md`
- Branch: `feat/3-analysis-job-bootstrap`
- PR: #4 stacked (`https://github.com/Commitfolio/Commitfolio/pull/4`), #5 to develop (`https://github.com/Commitfolio/Commitfolio/pull/5`)

## Objective
Implement Stage 2 so a selected repository becomes a persisted queued analysis job with a status lookup endpoint and minimal frontend status UI.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known
- [x] Stage 1 branch exists; this Stage 2 branch is stacked on `feat/1-repository-selector` until Stage 1 merges

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Add SQLAlchemy/Alembic persistence baseline
- [x] Add repository snapshot and analysis job models
- [x] Implement job create/status APIs
- [x] Implement frontend create/status UI
- [x] Update docs/contracts affected by the change

## Verification Checklist
- [x] Lint
- [x] Typecheck
- [x] Tests
- [x] Build
- [ ] Manual browser OAuth critical path check

## Default Verification Commands
Reference: `docs/playbooks/verification-baseline.md`

```bash
test -f apps/frontend/package.json || { echo "missing apps/frontend/package.json"; exit 1; }
test -f apps/backend/pyproject.toml || { echo "missing apps/backend/pyproject.toml"; exit 1; }
test -x apps/backend/.venv/bin/python || { echo "missing apps/backend/.venv/bin/python"; exit 1; }
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
cd apps/backend && .venv/bin/python -m pytest tests
```

## Deliverables
- Code: persistence baseline, analysis job endpoints, frontend create/status UI.
- Docs: PRD, task, API contract, domain model, backend env/readme notes, OMX plans.
- Follow-up: Stage 3 GitHub evidence ingestion should transition jobs beyond queued.

## Notes for Codex / OMX
- Use this file as the execution checklist.
- If scope grows, stop and split the task instead of silently expanding it.
- If implementation diverges from the PRD, update the PRD first.

## Execution Log
- 2026-04-15: Created GitHub issue #3 and branch `feat/3-analysis-job-bootstrap` stacked on Stage 1.
- 2026-04-15: Created PRD/task artifacts from Stage 2 roadmap.
- 2026-04-15: Added SQLAlchemy/Alembic baseline and initial repository/job migration.
- 2026-04-15: Implemented `POST /api/v1/analysis-jobs` and `GET /api/v1/analysis-jobs/{job_id}`.
- 2026-04-15: Connected selected repository UI to job creation and status refresh.
- 2026-04-15: Verification baseline, Alembic smoke migration, compileall, and frontend build passed.
- 2026-04-15: Pushed branch and opened stacked draft PR #4 with base `feat/1-repository-selector`.
- 2026-04-15: After #4 merged into the feature branch rather than `develop`, opened corrective draft PR #5 from `feat/3-analysis-job-bootstrap` to `develop`.

## Completion Notes
- What changed: Added SQLAlchemy/Alembic persistence baseline, repository snapshot and analysis job models, create/status APIs, and frontend job creation/status UI.
- Evidence: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `cd apps/backend && .venv/bin/python -m pytest tests`, `DATABASE_URL=sqlite:////tmp/commitfolio-alembic-smoke-stage2.db .venv/bin/alembic upgrade head`, and `PYTHONPYCACHEPREFIX=/tmp/commitfolio-pycache .venv/bin/python -m compileall app migrations` passed.
- Remaining risks: Browser-based OAuth + job creation smoke check still requires local GitHub OAuth credentials; branch is stacked on Stage 1 until PR #2 merges.
