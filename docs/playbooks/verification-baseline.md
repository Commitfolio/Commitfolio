# Verification Baseline

This repo is still in the harness-first stage, so verification should fail loudly when a service has not been scaffolded yet.

Use these commands as the default baseline for new feature work unless the feature PRD or task doc says otherwise.

## Frontend (`apps/frontend`)

```bash
test -f apps/frontend/package.json || { echo "missing apps/frontend/package.json"; exit 1; }
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
```

## Backend (`apps/backend`)

```bash
test -f apps/backend/pyproject.toml || { echo "missing apps/backend/pyproject.toml"; exit 1; }
test -x apps/backend/.venv/bin/python || { echo "missing apps/backend/.venv/bin/python"; exit 1; }
cd apps/backend && .venv/bin/python -m pytest tests
```

## Full feature baseline

```bash
test -f apps/frontend/package.json || { echo "missing apps/frontend/package.json"; exit 1; }
test -f apps/backend/pyproject.toml || { echo "missing apps/backend/pyproject.toml"; exit 1; }
test -x apps/backend/.venv/bin/python || { echo "missing apps/backend/.venv/bin/python"; exit 1; }
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
cd apps/backend && .venv/bin/python -m pytest tests
```

## Manual critical path baseline

1. Start the frontend locally and confirm the requested feature entry point renders.
2. Start the backend locally and confirm the feature's primary API path returns the expected success response.
3. Exercise the user-visible happy path plus at least one failure case from the matching test spec.

## Notes

- If the repo later standardizes on a different frontend or Python package manager, update this file first and then update the templates that reference it.
- Do not replace these commands with soft-skips; missing scaffold should be a visible failure until the app is bootstrapped.
- Backend verification assumes a local virtualenv at `apps/backend/.venv`; create it with `python3 -m venv apps/backend/.venv && apps/backend/.venv/bin/pip install 'apps/backend[dev]'`.
