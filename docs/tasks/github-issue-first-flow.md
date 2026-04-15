# GitHub Issue-First Delivery Flow Task

## Summary
- Title: GitHub issue-first delivery flow
- Status: Blocked
- Owner: Codex
- Issue:
- PRD: `docs/prd/github-issue-first-flow.md`
- Branch:
- PR:

## Objective
기능 요청이 들어오면 Commitfolio 저장소 안에서 issue 생성, 브랜치 생성, 검증, PR 오픈까지 이어지는 반복 가능한 GitHub 운영 경로를 만든다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] GitHub auth / repo access / push / PR readiness 점검 스크립트 추가
- [x] issue-first branch helper 추가
- [x] PR 생성 helper 추가
- [x] AGENTS.md / playbooks / templates 에 운영 규칙 반영

## Verification Checklist
- [x] Lint
- [x] Typecheck
- [x] Tests
- [ ] Manual critical path check

## Default Verification Commands
Reference: `docs/playbooks/verification-baseline.md`

```bash
test -f apps/frontend/package.json || { echo "missing apps/frontend/package.json"; exit 1; }
test -f apps/backend/pyproject.toml || { echo "missing apps/backend/pyproject.toml"; exit 1; }
test -x apps/backend/.venv/bin/python || { echo "missing apps/backend/.venv/bin/python"; exit 1; }
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
cd apps/backend && .venv/bin/python -m pytest tests
```

## Deliverables
- Code: `scripts/github/*`
- Docs: AGENTS/playbooks/templates update
- Follow-up: 실제 GitHub auth 완료 후 real issue → branch → PR smoke test

## Notes for Codex / OMX
- 기능 요청이 들어오면 GitHub auth가 준비된 경우 issue 먼저 만들고 브랜치를 판다.
- 권한이 준비되지 않았으면 로컬 구현은 계속하되, issue/PR 단계가 blocked 임을 명시한다.
- 브랜치명은 기본적으로 `feat/<issue>-<slug>` 규칙을 따른다.

## Execution Log
- 2026-04-15: GitHub CLI auth 상태가 invalid token 이라는 점을 확인했고, repo-local scripts/docs 로 자동화 경로를 보강하기로 결정했다.
- 2026-04-15: issue-first flow 전용 PRD/task/plans 를 생성했다.
- 2026-04-15: `scripts/github/check-flow.sh`, `scripts/github/start-feature.sh`, `scripts/github/create-pr.sh` 를 추가했다.
- 2026-04-15: AGENTS, playbooks, GitHub templates 에 issue-first 규칙과 fallback 규칙을 반영했다.

## Completion Notes
- What changed: GitHub auth 점검 스크립트, issue-first branch helper, PR helper, issue-first 운영 문서를 추가했다.
- Evidence: `bash -n scripts/github/*.sh`, `bash scripts/github/check-flow.sh`, `bash scripts/github/start-feature.sh --title 'Repository selector MVP' --slug repo-selector --dry-run`, `bash scripts/github/create-pr.sh --dry-run --draft`
- Remaining risks: `gh auth status` 가 아직 invalid token 이고 sandbox 환경에서는 GitHub 네트워크 호출이 제한되어 real issue/push/PR smoke test 는 미완료다.
