# Commitfolio MVP Feature Roadmap Task

## Summary
- Title: Commitfolio MVP staged feature roadmap
- Status: In Progress
- Owner: Codex
- Issue:
- PRD: `docs/prd/mvp-feature-roadmap.md`
- Branch:
- PR:

## Objective
외부 계획표를 저장소 안의 기준 문서로 옮겨서, 이후 기능 요청이 들어올 때 단계별 우선순위를 바로 선택할 수 있게 한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] 현재 구현 상태를 baseline으로 정리한다
- [x] 남은 MVP 기능을 단계별로 분리한다
- [x] 각 단계의 recommended slug / done 조건을 적는다
- [x] 다음 기본 실행 단계를 명시한다

## Verification Checklist
- [x] Lint
- [x] Typecheck
- [x] Tests
- [x] Manual critical path check

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
- Code: none
- Docs: roadmap PRD/task
- Follow-up: `repository-selector` 단계부터 순차 개발

## Notes for Codex / OMX
- 이 roadmap은 feature 우선순위 기준 문서다.
- 세부 구현은 각 stage마다 별도 feature PRD/task로 다시 쪼갠다.
- "다음 단계 진행" 요청이 오면 roadmap의 가장 앞선 미완료 단계를 택한다.

## Execution Log
- 2026-04-15: 외부 노션 계획표를 저장소 내부 markdown roadmap으로 고정하기로 결정했다.
- 2026-04-15: README, architecture docs, existing OAuth bootstrap slice를 기준으로 staged roadmap을 작성했다.

## Completion Notes
- What changed: 저장소 내부 기준 roadmap 문서를 추가해 이후 feature sequencing의 기준점을 만들었다.
- Evidence: roadmap 문서가 현재 완료 단계/다음 단계/후속 단계와 추천 slug를 모두 포함한다.
- Remaining risks: 외부 노션 계획과 차이가 있으면 이후 동기화가 필요하다.
