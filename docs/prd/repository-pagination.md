# PRD: 저장소 목록 페이지네이션

## Metadata
- Title: 저장소 목록 페이지네이션
- Owner: Codex
- Status: Done
- Target milestone: MVP usability
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/26
- Related task doc: `docs/tasks/repository-pagination.md`

## Problem
GitHub repository list API는 첫 페이지 30개와 next cursor를 반환하지만 frontend는 첫 페이지 목록만 보여준다. 사용자가 접근 권한을 가진 조직 repository가 첫 페이지 밖에 있으면 목록에 나타나지 않아 분석 대상으로 선택할 수 없다.

## Goal
- `next_cursor`가 있으면 저장소 목록에서 다음 페이지를 불러올 수 있게 한다.
- 추가 페이지는 기존 목록 뒤에 append한다.
- visibility filter가 바뀌면 목록과 cursor를 초기화한다.
- 한국어 에러/로딩 UX를 유지한다.

## Non-goals
- repository name search API
- GitHub organization OAuth approval 자동화
- 무한 스크롤

## Acceptance Criteria
- [ ] 첫 응답에 `next_cursor`가 있으면 더 보기 버튼이 보인다.
- [ ] 더 보기 클릭 시 다음 페이지 repository가 append된다.
- [ ] 더 보기 실패 시 기존 목록은 유지하고 한국어 오류를 보여준다.
- [ ] visibility filter 변경 시 첫 페이지부터 다시 로드한다.

## Verification Plan
- Frontend test: first page + next page append
- Frontend lint/typecheck/test/build
- Manual: org repository가 첫 페이지 밖일 때 더 보기로 찾기

## Risks
- org OAuth App access restriction이면 pagination만으로는 해결되지 않을 수 있다.
