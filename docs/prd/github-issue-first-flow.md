# GitHub Issue-First Delivery Flow PRD

## Metadata
- Title: GitHub issue-first delivery flow
- Owner: Codex
- Status: In Progress
- Target milestone: Harness hardening
- Related issue:
- Related task doc: `docs/tasks/github-issue-first-flow.md`

## Problem
Commitfolio의 문서 우선 개발 플로우는 이제 동작하지만, GitHub issue 생성, 브랜치 파생, push, PR 생성까지 이어지는 운영 규칙이 저장소 안에 명확히 고정되어 있지 않다. 그 결과 기능 요청이 들어와도 "문서부터 만들지", "issue를 먼저 팔지", "브랜치 이름은 어떻게 할지", "PR은 언제 여는지"가 세션마다 달라질 수 있다. 로컬 검증과 GitHub 협업 사이의 마지막 연결 고리가 아직 수동이다.

## User
- Primary user: Commitfolio 저장소에서 기능을 구현하는 Codex/OMX 운영자
- Trigger: 기능 개발 요청을 받았고, issue → branch → verify → PR 경로를 일관되게 실행하고 싶다
- Current pain: GitHub 인증 상태와 repo 권한 상태를 즉시 확인하기 어렵고, issue-first 규칙과 PR 오픈 규칙이 문서/스크립트로 고정되어 있지 않다

## Goal
- 기능 요청이 오면 GitHub 권한이 준비된 환경에서 issue 생성, 브랜치 파생, 검증, PR 생성까지 이어지는 표준 경로를 저장소에 내장한다.
- 인증이 아직 준비되지 않았을 때도 어디가 막혔는지 즉시 알 수 있는 점검 스크립트와 fallback 규칙을 제공한다.

## Non-goals
- GitHub Projects, labels, milestones, assignees까지 전부 자동화
- PR merge 또는 auto-merge 정책 강제
- 서버 측 봇이나 GitHub Actions 워크플로우 추가

## Scope
### In scope
- GitHub flow 점검 스크립트 추가 (`gh auth`, repo access, push/pr 가능성 확인)
- issue-first 브랜치/PR 보조 스크립트 추가
- AGENTS.md 및 플레이북에 issue → branch → PR 규칙 반영
- 기능 문서 템플릿에 issue/branch 연결 정보 보강

### Out of scope
- 조직 차원의 GitHub App 설치 자동화
- 원격 저장소 보호 규칙 변경
- PR 리뷰어 자동 지정

## User Flow
1. 운영자가 기능 요청을 받는다.
2. 저장소 스크립트로 GitHub auth / repo access 상태를 점검한다.
3. issue-first 규칙에 따라 issue를 만들고 `feat/<issue>-<slug>` 브랜치를 만든다.
4. PRD / task / `.omx/plans` 문서를 만들고 구현/검증을 수행한다.
5. push 후 PR 또는 draft PR을 연다.

## Functional Requirements
- 저장소는 `gh auth`, repo access, push 가능 여부, PR 생성 가능 여부를 확인하는 스크립트를 제공해야 한다.
- 저장소는 title/slug 기반으로 issue 생성 후 브랜치를 파는 스크립트를 제공해야 한다.
- 저장소는 현재 브랜치를 push하고 PR을 여는 스크립트를 제공해야 한다.
- GitHub 권한이 없으면 로컬 구현은 계속할 수 있어야 하지만, issue/PR 단계가 왜 막혔는지 분명히 보여야 한다.
- AGENTS.md 와 플레이북은 net-new feature work 에 issue-first 규칙을 명시해야 한다.

## UX / UI Notes
- Entry point: CLI helpers under `scripts/github`
- Empty / loading / error states: gh 미설치, 토큰 만료, repo 미접근, 잘못된 브랜치 명명은 명시적 오류 메시지로 안내
- Editing constraints: 브랜치명과 issue 번호 추론 규칙은 단순하고 사람이 읽기 쉬워야 한다

## API / Backend Notes
- Endpoints: 없음
- Auth / permissions: GitHub CLI auth (`gh auth login`) 와 저장소 push / PR 권한 필요
- Background processing: 없음
- SSE / polling behavior: 없음

## Data / Domain Notes
- Tables or entities touched: 없음
- External APIs touched: GitHub CLI가 호출하는 GitHub Issues / Pull Requests API
- Stored artifacts: GitHub issue, git branch, GitHub PR

## Acceptance Criteria
- [ ] GitHub flow 점검 스크립트가 현재 auth / repo access / push / PR readiness를 요약한다
- [ ] issue-first 브랜치 생성 스크립트가 `feat/<issue>-<slug>` 규칙을 따르는 브랜치를 준비한다
- [ ] PR 생성 스크립트가 현재 브랜치와 issue/doc 링크를 사용해 PR 또는 draft PR을 열 수 있다
- [ ] AGENTS.md / playbooks / templates 에 issue-first 규칙이 반영된다
- [ ] GitHub 권한이 없을 때의 fallback 경로가 문서화된다

## Verification Plan
- Unit: `scripts/github/check-flow.sh`, `scripts/github/start-feature.sh --dry-run`, `scripts/github/create-pr.sh --dry-run`
- Integration: `gh auth status`, `gh repo view`, `git push --dry-run origin HEAD`, `gh pr create` 경로를 권한이 준비된 환경에서 검증
- Manual: 실제 issue 생성 → 브랜치 생성 → 구현 후 push → PR 생성까지 1회 수행

## Risks
- GitHub 권한이 org/repo에 연결되지 않으면 자동화가 부분적으로만 동작한다.
- 브랜치명에서 issue/slug를 추론하는 규칙이 느슨하면 PR 자동화가 깨질 수 있다.

## Open Questions
- feature 외 fix/chore 타입도 같은 issue-first 강제를 적용할지?

## Approval
- Requested by: project owner
- Approved by:
- Approved at:
