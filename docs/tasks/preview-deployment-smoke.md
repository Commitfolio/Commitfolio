# Task: Render/Vercel preview deployment smoke 준비

## Summary
- Title: Render/Vercel preview deployment smoke 준비
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/34
- PRD: `docs/prd/preview-deployment-smoke.md`
- Branch: `feat/34-preview-deployment-smoke`
- PR:

## Objective
Stage 9 진입 전에 Render/Vercel preview 배포를 검증할 수 있도록 env 기반 session cookie 설정과 smoke tooling/documentation을 준비한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Backend session cookie SameSite/Secure env 설정 추가
- [x] `.env.example` preview/prod cookie guidance 추가
- [x] preview smoke script 추가
- [x] operator deployment playbook 업데이트
- [x] 테스트/검증 실행
- [x] Docs completion notes 업데이트

## Verification Checklist
- [x] Backend targeted cookie test
- [x] Local preview smoke script
- [x] Backend full tests
- [x] Frontend lint/typecheck/test/build
- [x] `git diff --check`

## Default Verification Commands
Reference: `docs/playbooks/verification-baseline.md`

```bash
cd apps/backend && .venv/bin/python -m pytest tests/test_auth.py::test_session_cookie_settings_are_env_configurable_for_split_domain_preview
scripts/deployment/preview_smoke.py --backend-url http://localhost:8000 --frontend-url http://localhost:5173
cd apps/backend && .venv/bin/python -m pytest tests
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
npm --prefix apps/frontend run build
git diff --check
```

## Deliverables
- Code: `apps/backend/app/config.py`, `apps/backend/app/main.py`, `apps/backend/tests/test_auth.py`, `scripts/deployment/preview_smoke.py`
- Docs: `apps/backend/.env.example`, `docs/playbooks/operator-deployment-actions.md`, `docs/prd/preview-deployment-smoke.md`, `docs/tasks/preview-deployment-smoke.md`
- Follow-up: 사용자가 Render/Vercel/GitHub OAuth preview URL/env를 준비하면 외부 URL로 smoke 실행

## Notes for Codex / OMX
- Secret 값을 출력하거나 커밋하지 않는다.
- 실제 외부 콘솔 생성은 사용자 액션으로 남긴다.
- Local smoke가 통과해도 external preview smoke는 URL/env가 준비된 뒤 별도 확인해야 한다.

## Execution Log
- 2026-04-17: roadmap상 Stage 8 이후 checkpoint가 Render/Vercel preview deployment smoke임을 확인했다.
- 2026-04-17: GitHub issue #34와 `feat/34-preview-deployment-smoke` 브랜치를 만들었다.
- 2026-04-17: local frontend/backend 기준 `scripts/deployment/preview_smoke.py --backend-url http://localhost:8000 --frontend-url http://localhost:5173` 통과.

## Completion Notes
- What changed: split-domain preview 배포에 필요한 backend session cookie SameSite/Secure env 설정을 추가하고, Render/Vercel/OAuth/CORS 정합성을 확인하는 stdlib 기반 preview smoke script와 operator playbook 절차를 추가했다.
- Evidence: targeted backend cookie test, local preview smoke, backend full pytest, frontend lint/typecheck/test/build, `git diff --check` 통과.
- Remaining risks: 실제 Render/Vercel/GitHub OAuth preview smoke는 사용자가 외부 콘솔에서 URL/env/callback을 준비한 뒤 실행해야 한다.
