# GitHub Evidence Ingestion Task

## Summary
- Title: GitHub evidence ingestion
- Status: Done
- Owner: Codex
- Issue: #6
- PRD: `docs/prd/github-evidence-ingestion.md`
- Branch: `feat/6-github-evidence-ingestion`
- PR:

## Objective
Implement Stage 3 so an analysis job can collect bounded GitHub evidence, persist normalized records, and append replayable job events for the future SSE stage.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known
- [x] Branch was created from latest `develop`

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Add `AnalysisEvidence` and `AnalysisJobEvent` models/migration
- [x] Extend GitHub integration for bounded evidence collection
- [x] Implement job run and evidence summary endpoints
- [x] Implement frontend run-analysis/evidence summary UI
- [x] Update docs/contracts affected by the change

## Verification Checklist
- [x] Lint
- [x] Typecheck
- [x] Tests
- [x] Build
- [x] Alembic migration smoke
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
- Code: models/migration, GitHub evidence ingestion, run/evidence APIs, frontend run UI.
- Docs: PRD, task, API contract, domain model, roadmap, OMX plans.
- Follow-up: Stage 4 should expose `analysis_job_events` through SSE with replay support.

## Notes for Codex / OMX
- Use this file as the execution checklist.
- Keep evidence ingestion bounded and deterministic.
- If implementation diverges from the PRD, update the PRD first.

## Execution Log
- 2026-04-15: Created GitHub issue #6 and branch `feat/6-github-evidence-ingestion` from latest `develop`.
- 2026-04-15: Created PRD/task artifacts from Stage 3 roadmap.
- 2026-04-15: Added evidence/event data model and Alembic migration.
- 2026-04-15: Implemented bounded GitHub evidence collection and job run/evidence endpoints.
- 2026-04-15: Connected frontend run-analysis control and evidence summary UI.
- 2026-04-15: Verification baseline, Alembic smoke migration, compileall, and frontend build passed.
- 2026-04-15: Marked Stage 3 done in the roadmap and set Stage 4 as the next default stage.

## Completion Notes
- What changed: Added `AnalysisEvidence` and `AnalysisJobEvent`, migration 0002, bounded GitHub evidence collection, job run/evidence summary APIs, and frontend run-analysis evidence summary UI.
- Evidence: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `cd apps/backend && .venv/bin/python -m pytest tests`, `DATABASE_URL=sqlite:////tmp/commitfolio-alembic-smoke-stage3.db .venv/bin/alembic upgrade head`, and `PYTHONPYCACHEPREFIX=/tmp/commitfolio-pycache-stage3 .venv/bin/python -m compileall app migrations` passed.
- Remaining risks: Browser-based OAuth + real GitHub ingestion smoke check still requires local GitHub OAuth credentials; ingestion is synchronous and bounded for MVP, not final long-running worker architecture.
