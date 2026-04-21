# PRD: Preview CORS 하드닝

## Metadata
- Title: Preview CORS 하드닝
- Owner: Codex
- Status: Done
- Target milestone: Public MVP / Stage 9 hardening
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/36
- Related task doc: `docs/tasks/preview-cors-hardening.md`

## Problem
Preview 배포에서 Render backend는 정상 동작하지만, `BACKEND_CORS_ORIGIN`이 단일 origin 문자열만 허용해 Vercel production alias와 deployment URL 전환에 취약하다. Vercel production alias가 갱신되기 전이나 특정 smoke 단계에서 deployment URL을 함께 써야 할 수 있는데, 현재 구현은 origin 하나만 허용하므로 preflight가 실패한다.

## Goal
- backend가 comma-separated origin 목록을 허용하도록 하드닝한다.
- preview/prod 문서에서 alias URL과 deployment URL을 함께 넣을 수 있게 안내한다.
- CORS preflight 회귀 테스트를 추가한다.

## Non-goals
- wildcard `*` + credentials 허용
- Vercel 배포 전략 자체 변경
- OAuth/DB schema 변경

## Scope
### In scope
- `BACKEND_CORS_ORIGIN`의 CSV parsing 지원
- FastAPI CORSMiddleware에 다중 origin 전달
- 관련 테스트 추가
- preview deployment 문서 업데이트

### Out of scope
- 프론트 코드 변경
- 새로운 배포 플랫폼 추가

## Acceptance Criteria
- [x] `BACKEND_CORS_ORIGIN`에 `https://a,https://b` 형태를 넣을 수 있다.
- [x] preflight가 허용된 origin에는 200/허용 헤더로 응답한다.
- [x] 허용되지 않은 origin은 계속 차단된다.
- [x] backend tests와 local preview smoke가 통과한다.

## Verification Plan
- `cd apps/backend && .venv/bin/python -m pytest tests/test_auth.py`
- `scripts/deployment/preview_smoke.py --backend-url http://localhost:8000 --frontend-url http://localhost:5173`
- `git diff --check`

## Risks
- env value 공백/쉼표 처리 실수로 의도치 않은 origin이 빠질 수 있다.
- 실제 stale frontend bundle 문제는 별도 재배포가 필요하다.
