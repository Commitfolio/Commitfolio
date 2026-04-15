# Repository Selector Task

## Summary
- Title: Repository access and selection
- Status: Done
- Owner: Codex
- Issue: #1
- PRD: `docs/prd/repository-selector.md`
- Branch: `feat/1-repository-selector`
- PR: #2 (`https://github.com/Commitfolio/Commitfolio/pull/2`)

## Objective
Implement the narrow Stage 1 slice that lets a signed-in GitHub user list accessible repositories and select one repository as the input for the future analysis job stage.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Add or update tests before risky refactors
- [x] Implement backend repository listing endpoint
- [x] Implement frontend repository selector UI
- [x] Update docs/contracts affected by the change

## Verification Checklist
- [x] Lint
- [x] Typecheck
- [x] Tests
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
- Code: backend GitHub repository endpoint and frontend selector UI.
- Docs: PRD, task, API contract, env/readme notes, OMX plans.
- Follow-up: Stage 2 analysis job bootstrap should consume the selected repository.

## Notes for Codex / OMX
- Use this file as the execution checklist.
- If scope grows, stop and split the task instead of silently expanding it.
- If implementation diverges from the PRD, update the PRD first.
- Do not add new dependencies in this slice.

## Execution Log
- 2026-04-15: Created GitHub issue #1 and branch `feat/1-repository-selector`.
- 2026-04-15: Created PRD/task artifacts from Stage 1 roadmap.
- 2026-04-15: Implemented backend repository listing endpoint with server-side in-memory token lookup.
- 2026-04-15: Implemented frontend repository selector with loading/empty/error/success states and single repo selection.
- 2026-04-15: Updated API contract and backend env/README scope notes for repository access.
- 2026-04-15: Full verification baseline and frontend production build passed.
- 2026-04-15: Marked Stage 1 done in the roadmap and set Stage 2 as the next default stage.
- 2026-04-15: Pushed branch and opened draft PR #2.

## Completion Notes
- What changed: Backend `GET /api/v1/repositories`, GitHub repo client, frontend repository selector UI, docs/contracts.
- Evidence: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `cd apps/backend && .venv/bin/python -m pytest tests`, and `npm --prefix apps/frontend run build` passed.
- Remaining risks: Browser-based OAuth repo-list smoke check still requires local GitHub OAuth credentials; private repo access uses broad OAuth App `repo` scope until a later GitHub App/fine-grained-token hardening pass.
