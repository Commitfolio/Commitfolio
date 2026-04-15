# GitHub OAuth Bootstrap Task

## Summary
- Title: GitHub OAuth bootstrap vertical slice
- Status: In Progress
- Owner: Codex
- PRD: `docs/prd/github-oauth-bootstrap.md`
- Branch: `feat/github-oauth-bootstrap`
- PR:

## Objective
Create the first exemplar feature contract for Commitfolio so the harness can validate one narrow auth-first slice before broader MVP work begins.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules in `apps/frontend` and `apps/backend`
- [x] Add or update tests before risky auth/session refactors
- [x] Implement the smallest working OAuth login/logout slice
- [x] Update docs/contracts affected by the change

## Verification Checklist
- [x] Lint
- [x] Typecheck
- [x] Tests
- [ ] Manual critical path check

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
- Code: bootstrap OAuth frontend/backend slice
- Docs: PRD/task/test-spec/env + scope notes
- Follow-up: repository selection feature after auth path is stable

## Notes for Codex / OMX
- Use this file as the execution checklist.
- If scope grows into repo selection or persistence hardening, split a new task instead of silently expanding.
- If implementation diverges from the PRD, update the PRD first.

## Execution Log
- 2026-04-15: Selected `github-oauth-bootstrap` as the exemplar feature to validate the repo's document-first harness flow.
- 2026-04-15: Created matching docs + `.omx/plans` artifacts and aligned them to the baseline verification commands.
- 2026-04-15: Bootstrapped a minimal Vite React frontend with session-state UI and a FastAPI backend with GitHub OAuth start/callback/logout/`GET /api/v1/me`.
- 2026-04-15: Added frontend Vitest coverage and backend pytest coverage for the auth-first slice.
- 2026-04-15: Created local `.env.example` files and switched backend verification to the project-managed virtualenv path.

## Completion Notes
- What changed: implemented the bootstrap frontend/backend auth slice, env examples, and automated tests
- Evidence: frontend lint/typecheck/test/build passed; backend pytest passed via `cd apps/backend && .venv/bin/python -m pytest tests`
- Remaining risks: real end-to-end OAuth callback still needs GitHub app credentials for manual verification
