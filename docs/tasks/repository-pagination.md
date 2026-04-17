# Task: 저장소 목록 페이지네이션

## Summary
- Title: 저장소 목록 페이지네이션
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/26
- PRD: `docs/prd/repository-pagination.md`
- Branch: `기능/이슈-26-저장소-목록-더보기`
- PR:

## Objective
GitHub repository 목록 첫 페이지 밖 저장소를 선택할 수 있도록 cursor 기반 더 보기 기능을 추가한다.

## Implementation Checklist
- [x] API client cursor parameter 추가
- [x] repository selector hook에 nextCursor/loadMore 상태 추가
- [x] RepositorySelector에 더 보기 버튼/오류 표시 추가
- [x] frontend test 추가

## Verification Checklist
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `git diff --check`

## Completion Notes
- What changed: backend가 이미 제공하던 `next_cursor`를 frontend가 저장하고, `저장소 더 불러오기` 버튼으로 다음 repository page를 append한다.
- Evidence: frontend lint/typecheck/test/build 및 git diff --check 통과.
- Remaining risks: GitHub 조직에서 OAuth App access를 제한한 경우 페이지네이션으로도 org private repo가 안 보일 수 있다. 그 경우 org owner가 OAuth App을 승인해야 한다.
