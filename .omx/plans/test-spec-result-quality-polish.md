# OMX Test Spec: result-quality-polish

## Backend
- Unit/service test: no OpenAI key skips enhancement and result creation succeeds.
- Unit/service test: deterministic fallback reflects README/language/structure evidence in generated sections.
- Unit/service test: fake successful enhancer returns modified sections while preserving evidence link ids.
- Unit/service test: fake failed enhancer returns fallback sections and marks fallback status.
- API test: result detail includes enhancement status fields.
- Regenerate test: regenerated result receives status for its own generation path.
- Unit/service test: Flutter/mobile evidence produces stack and contribution wording that is not generic placeholder text.

## Frontend
- Type/API test: result shape includes enhancement status.
- UI test: detail page renders neutral status badge for fallback/no-key state.
- UI test: existing edit/save/regenerate interactions still pass.
- UI test: generated result is revealed after a short rendering delay rather than immediately.

## Verification Commands
```bash
cd apps/backend && .venv/bin/python -m pytest -q -p no:cacheprovider
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
npm --prefix apps/frontend run build
git diff --check
```

## Manual Evidence
- Confirm optional OpenAI env documentation exists.
- Confirm UI status language does not present no-key fallback as an error.
