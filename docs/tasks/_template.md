# Task Template

## Summary
- Title:
- Status: Draft | Ready | In Progress | Blocked | Done
- Owner:
- Issue:
- PRD:
- Branch:
- PR:

## Objective
State the narrow outcome for this task in 1-2 sentences.

## Preconditions
- [ ] PRD is approved
- [ ] Scope is narrow enough for one branch / PR
- [ ] Verification approach is known

## Implementation Checklist
- [ ] Confirm touched files/modules
- [ ] Add or update tests before risky refactors
- [ ] Implement the smallest working slice
- [ ] Update docs/contracts affected by the change

## Verification Checklist
- [ ] Lint
- [ ] Typecheck
- [ ] Tests
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
- Code:
- Docs:
- Follow-up:

## Notes for Codex / OMX
- Use this file as the execution checklist.
- If scope grows, stop and split the task instead of silently expanding it.
- If implementation diverges from the PRD, update the PRD first.

## Execution Log
- 

## Completion Notes
- What changed:
- Evidence:
- Remaining risks:
