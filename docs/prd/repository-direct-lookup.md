# PRD: 조직 저장소 직접 검색

## Metadata
- Title: 조직 저장소 직접 검색
- Owner: Codex
- Status: Done
- Target milestone: MVP repository selection usability
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/28
- Related task doc: `docs/tasks/repository-direct-lookup.md`

## Problem
`/user/repos` 목록에 조직 저장소가 보이지 않는 경우 사용자는 접근 가능한 repo라도 선택할 수 없다. 특히 사용자가 정확한 GitHub URL이나 `owner/repo` 이름을 알고 있는데도 목록 기반 UI만 제공하면 분석 대상 선택이 막힌다.

## Goal
- 사용자가 `owner/repo` 또는 GitHub repo URL로 저장소를 직접 조회할 수 있다.
- GitHub token이 접근 가능한 repo면 기존 목록에 추가하고 선택할 수 있다.
- 접근 불가/조직 OAuth 제한이면 한국어로 원인을 안내한다.

## Non-goals
- 모든 기여 repo 자동 탐색
- GitHub organization OAuth policy 자동 승인
- repository full-text search

## Acceptance Criteria
- [ ] 직접 검색 입력과 버튼이 있다.
- [ ] `SERVICE-MOHAENG/Mohaeng-BE` 형식 입력을 지원한다.
- [ ] `https://github.com/SERVICE-MOHAENG/Mohaeng-BE` URL 입력을 지원한다.
- [ ] 조회 성공 시 목록에 append되고 자동 선택된다.
- [ ] 조회 실패 시 기존 목록은 유지하고 한국어 안내를 표시한다.

## Risks
- 조직 OAuth App access restriction이면 직접 조회도 404/403이 날 수 있다.
- 사용자가 repo 이름을 잘못 입력할 수 있다.

## References
- GitHub REST get repository endpoint: https://docs.github.com/en/rest/repos/repos#get-a-repository
- GitHub REST list repositories for authenticated user: https://docs.github.com/en/rest/repos/repos#list-repositories-for-the-authenticated-user
