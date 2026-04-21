# Task: Preview CORS 하드닝

## Summary
- Title: Preview CORS 하드닝
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/36
- PRD: `docs/prd/preview-cors-hardening.md`
- Branch: `feat/36-preview-cors-hardening`
- PR:

## Objective
Preview/prod 전환에서 Render backend가 Vercel alias URL과 deployment URL을 함께 허용할 수 있도록 CORS origin 설정을 하드닝한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Touched files 확인
- [x] CSV origin parsing 추가
- [x] preflight 테스트 추가
- [x] README/playbook env 예시 갱신
- [x] 검증 실행

## Verification Checklist
- [x] backend tests
- [x] local preview smoke
- [x] `git diff --check`

## Completion Notes
- What changed: backend가 comma-separated `BACKEND_CORS_ORIGIN` 값을 파싱해 Vercel alias와 deployment URL을 함께 허용할 수 있게 했고, preflight 회귀 테스트와 관련 문서를 업데이트했다.
- Evidence: `cd apps/backend && .venv/bin/python -m pytest tests`, `scripts/deployment/preview_smoke.py --backend-url http://localhost:8000 --frontend-url http://localhost:5173`, `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `git diff --check` 통과.
- Remaining risks: production alias가 최신 frontend bundle을 서빙하도록 Vercel 재배포/alias 전환은 여전히 외부 콘솔 작업이 필요하다.
