# Task: 결과 서술 고도화와 UI 전면 재정리

## Summary
- Title: 결과 서술 고도화와 UI 전면 재정리
- Status: In Progress
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/45
- PRD: `docs/prd/result-narrative-ui-refresh.md`
- Branch: `feat/45-result-narrative-ui-refresh`
- PR:

## Objective
rule-based 결과 생성이 실제 포트폴리오 초안처럼 읽히도록 고도화하고, 최신 UI가 preview/main 배포에 반영되게 한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Refresh design contract
- [ ] Improve deterministic result generation heuristics
- [ ] Rework result view hierarchy and supporting UI
- [ ] Add or update tests for richer result narrative
- [ ] Verify preview/main deployment reflects the latest UI
- [ ] Update docs/contracts affected by the change

## Verification Checklist
- [ ] `npm --prefix apps/frontend run lint`
- [ ] `npm --prefix apps/frontend run typecheck`
- [ ] `npm --prefix apps/frontend run test -- --run`
- [ ] `npm --prefix apps/frontend run build`
- [ ] `cd apps/backend && .venv/bin/python -m pytest tests`
- [ ] `git diff --check`
- [ ] Manual deployed URL verification

## Default Verification Commands
Reference: `docs/playbooks/verification-baseline.md`

```bash
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
npm --prefix apps/frontend run build
cd apps/backend && .venv/bin/python -m pytest tests
git diff --check
```

## Deliverables
- Code: `apps/backend/app/services/results.py`, related backend tests, `apps/frontend/src/app/App.tsx`, `apps/frontend/src/features/result-viewer/*`, `apps/frontend/src/styles.css`
- Docs: `DESIGN.md`, `docs/prd/result-narrative-ui-refresh.md`, `docs/tasks/result-narrative-ui-refresh.md`
- Follow-up: develop/main deploy confirmation and any remaining preview-session diagnosis

## Notes for Codex / OMX
- commit title 나열형 결과를 포트폴리오 가치가 있는 문장형 결과로 바꾸는 것이 1순위다.
- OpenAI 없는 경로를 먼저 강하게 만든다.
- preview URL의 stale UI 여부와 main 반영 여부를 둘 다 확인한다.

## Execution Log
- 2026-06-23: 사용자 보고와 live preview DOM을 기준으로 결과 생성이 지나치게 정적이고 preview 배포에 예전 UI가 남아 있음을 확인했다.
- 2026-06-23: GitHub issue #45와 `feat/45-result-narrative-ui-refresh` worktree/branch를 생성했다.
- 2026-06-23: `DESIGN.md`와 feature PRD/task를 갱신해 narrative-first 결과 문서 방향을 고정했다.

## Completion Notes
- What changed:
- Evidence:
- Remaining risks:
