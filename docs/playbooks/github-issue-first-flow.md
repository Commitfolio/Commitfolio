# GitHub Issue-First Feature Flow

이 문서는 Commitfolio에서 **기능 요청 → issue → branch → 구현 → 검증 → PR** 로 이어지는 기본 GitHub 협업 흐름을 정리한다.

## Principle

- net-new feature work 는 가능한 한 **issue-first** 로 진행한다.
- 문서 우선 규칙은 유지한다. 즉, issue를 만든 뒤에도 구현 전에 PRD/task/plan 문서를 맞춘다.
- GitHub 권한이 아직 준비되지 않았으면 로컬 문서화와 구현은 계속할 수 있지만, issue/PR 단계는 blocker 로 명시한다.

## Prerequisites

```bash
gh auth login
scripts/github/check-flow.sh --strict
```

이 두 단계가 통과해야 issue 생성, push, PR 생성까지 한 번에 진행할 수 있다.

## Standard flow

1. 기능 요청을 받는다.
2. slug 를 정한다.
3. GitHub issue 를 만든다.
4. `feat/<issue>-<slug>` 브랜치를 만든다.
5. `docs/prd/<slug>.md`, `docs/tasks/<slug>.md`, `.omx/plans/*` 를 정리한다.
6. 구현한다.
7. 검증한다.
8. 커밋한다.
9. push 한다.
10. PR 또는 draft PR 을 연다.

## Helper scripts

### 1) GitHub flow 점검

```bash
scripts/github/check-flow.sh --strict
```

확인 항목:
- gh 설치 여부
- gh auth 상태
- 현재 repo 접근 가능 여부
- `git push --dry-run origin HEAD`
- `gh pr list`

### 2) issue 생성 + branch 생성

```bash
scripts/github/start-feature.sh \
  --title "Repository selector MVP" \
  --slug repo-selector
```

기존 issue 가 있으면:

```bash
scripts/github/start-feature.sh \
  --issue-number 123 \
  --slug repo-selector
```

### 3) PR 열기

```bash
scripts/github/create-pr.sh --draft
```

정식 PR 로 열고 싶으면:

```bash
scripts/github/create-pr.sh
```

## Branch rules

- Feature: `feat/<issue>-<slug>`
- Fix: `fix/<issue>-<slug>`
- Chore/refactor 는 가능하면 관련 issue 를 붙인다

issue 번호가 있으면 commit subject 도 `(#<issue>)` prefix 규칙을 따른다.

## Fallback when GitHub auth is blocked

다음 중 하나가 실패하면:
- `gh auth status`
- `gh repo view`
- `git push --dry-run origin HEAD`
- `gh pr list`

처리 원칙:
- 로컬 branch / docs / implementation / verification / commit 까지는 계속 진행 가능
- issue / push / PR 단계는 **blocked by GitHub auth or repo permission** 으로 보고한다
- 권한이 풀리면 `scripts/github/check-flow.sh --strict` 부터 다시 시작한다

## Manual smoke test after auth is fixed

1. `gh auth login`
2. `scripts/github/check-flow.sh --strict`
3. `scripts/github/start-feature.sh --title "Smoke test" --slug smoke-test`
4. 문서/코드 없이 바로 되돌릴 테스트라면 빈 커밋 대신 dry-run 으로 확인
5. 실제 작업 후 `scripts/github/create-pr.sh --draft`

## Notes for Codex / OMX

- 기능 요청이 들어오면 auth 가 준비된 경우 issue-first 를 기본값으로 본다.
- auth 가 안 되어 있으면 issue-first 규칙을 무시하는 게 아니라, **blocked 상태를 명시하고 로컬 단계만 진행**한다.
- PR 본문에는 PRD / task / issue 링크와 verification evidence 를 반드시 남긴다.
