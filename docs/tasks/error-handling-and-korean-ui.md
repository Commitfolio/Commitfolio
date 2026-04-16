# Task: 한국어 UI와 예외 처리/로깅 체계 정리

## Summary
- Title: 한국어 UI와 예외 처리/로깅 체계 정리
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/22
- PRD: `docs/prd/error-handling-and-korean-ui.md`
- Branch: `기능/이슈-22-한국어-ui-예외-로깅`
- PR:

## Objective
요청/예외 로그와 공통 예외 응답을 구축하고, 로컬 메인 UI를 한국어/고대비 중심으로 정리한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Backend request logging middleware 추가
- [x] Backend unexpected exception handler 추가
- [x] Frontend auth/API error mapping 한국어화
- [x] Frontend 주요 UI 문구 한국어화
- [x] 메인 화면 대비/가독성 CSS 개선
- [x] Tests 업데이트
- [x] Docs/roadmap 필요 시 업데이트

## Verification Checklist
- [x] `cd apps/backend && .venv/bin/python -m pytest -q -p no:cacheprovider`
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `git diff --check`

## Deliverables
- Code: backend logging/exception handling, Korean UI copy, readability CSS
- Docs: PRD/task, exception/logging policy
- Follow-up: production observability vendor 여부는 Stage 9에서 결정

## Notes for Codex / OMX
- 사용자-facing 문구는 한국어를 기본으로 한다.
- env/API/code identifier는 영어 그대로 둔다.
- secret/token/raw stack trace를 사용자 response에 노출하지 않는다.

## Execution Log
- 2026-04-16: local `auth_error=backend_not_configured` 재현과 backend request log 확인 후 작업 시작.

## Completion Notes
- What changed: backend request id logging middleware와 unexpected exception handler를 추가하고, frontend auth/API error mapping과 주요 UI copy를 한국어로 정리했다. 메인 화면 대비와 card/panel 가독성을 개선했다.
- Evidence: backend pytest 29 passed, frontend lint/typecheck/test/build 통과, compileall 및 git diff --check 통과.
- Remaining risks: 실제 GitHub OAuth 로그인은 GITHUB_CLIENT_ID/SECRET이 없어 아직 smoke하지 않았다. 운영 로그 수집 SaaS는 Stage 9 이후 별도 판단이 필요하다.
