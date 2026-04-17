# Task: 조직 저장소 직접 검색

## Summary
- Title: 조직 저장소 직접 검색
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/28
- PRD: `docs/prd/repository-direct-lookup.md`
- Branch: `기능/이슈-28-조직-저장소-직접검색`
- PR:

## Objective
목록에 안 뜨는 조직 저장소를 full name/URL로 직접 조회해 선택할 수 있게 한다.

## Implementation Checklist
- [x] Backend direct repo lookup service 추가
- [x] Backend `/repositories/lookup` endpoint 추가
- [x] Frontend API client 추가
- [x] RepositorySelector 검색 form 추가
- [x] Hook state/test 추가

## Verification Checklist
- [x] `cd apps/backend && .venv/bin/python -m pytest -q -p no:cacheprovider`
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `git diff --check`

## Completion Notes
- What changed: `owner/repo` 또는 GitHub URL로 저장소를 직접 조회하는 backend endpoint와 frontend 검색 form을 추가했다. 조회 성공 시 목록에 추가하고 자동 선택한다.
- Evidence: backend pytest 30 passed, frontend lint/typecheck/test 11 passed/build, compileall, git diff --check 통과.
- Remaining risks: GitHub 조직이 OAuth App access를 막으면 직접 조회도 404/403이 날 수 있다. 이 경우 조직 owner가 OAuth App을 승인해야 한다.
