# Task: 차분한 UI와 명확한 액션 계층을 위한 프런트 refresh

## Summary
- Title: 차분한 UI와 명확한 액션 계층을 위한 프런트 refresh
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/42
- PRD: `docs/prd/calm-ui-refresh.md`
- Branch: `feat/42-calm-ui-refresh`
- PR:

## Objective
배포된 Commitfolio UI의 읽기 피로를 줄이고, signed-out/signed-in/analysis/result 상태별 핵심 버튼 역할을 더 명확하게 드러내는 프런트 refresh를 완료한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Create or refresh design contract
- [x] Update app shell hierarchy and CTA emphasis
- [x] Update panel/button variants and readability-focused CSS
- [x] Hide production debug/env copy from the main surface
- [x] Verify critical-path labels remain intact
- [x] Update docs/contracts affected by the change

## Verification Checklist
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `git diff --check`
- [x] Manual screenshot review

## Default Verification Commands
Reference: `docs/playbooks/verification-baseline.md`

```bash
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
npm --prefix apps/frontend run build
git diff --check
```

## Deliverables
- Code: `apps/frontend/src/app/App.tsx`, `apps/frontend/src/styles.css`, `apps/frontend/src/features/github-auth/SessionPanel.tsx`, `apps/frontend/src/features/analysis-job/AnalysisJobPanel.tsx`, `apps/frontend/src/features/result-viewer/ResultExportActions.tsx`, `apps/frontend/src/features/result-viewer/RecentResults.tsx`, `apps/frontend/src/features/result-editor/ResultEditor.tsx`, `apps/frontend/src/features/result-viewer/ResultDocument.tsx`
- Docs: `DESIGN.md`, `docs/prd/calm-ui-refresh.md`, `docs/tasks/calm-ui-refresh.md`, `.omx/plans/prd-calm-ui-refresh.md`, `.omx/plans/test-spec-calm-ui-refresh.md`
- Follow-up: develop PR merge 후 release/main deploy 경로 확인

## Notes for Codex / OMX
- 기존 critical text label은 함부로 바꾸지 않는다.
- 새 dependency 없이 CSS/markup 중심으로 해결한다.
- 배포 사용자에게 불필요한 debug/env 정보는 숨긴다.

## Execution Log
- 2026-06-23: 배포된 `https://commitfolio.vercel.app/` 화면을 검토하고 타이포 과밀, CTA 계층 부족, debug copy 노출을 주요 문제로 확인했다.
- 2026-06-23: GitHub issue #42를 생성하고 `feat/42-calm-ui-refresh` 별도 worktree/branch를 열었다.
- 2026-06-23: `DESIGN.md`와 feature PRD/task/OMX plans를 생성해 refresh 기준을 고정했다.
- 2026-06-23: hero/action/panel/result UI refresh를 구현하고, `lint`, `typecheck`, `test`, `build`, `git diff --check`를 통과했다.
- 2026-06-23: 로컬 정적 preview 스크린샷과 기존 배포 스크린샷을 비교해 hero 밀도 축소, CTA 분리, debug copy 비노출을 확인했다.

## Completion Notes
- What changed: hero CTA/support zone, workflow cards, session panel, analysis action hierarchy, result history/export/editor, global CSS token system을 차분한 톤으로 재정렬했다. production에서는 env/debug copy를 숨기고 네트워크 에러를 한국어 안내로 정리했다.
- Evidence: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `git diff --check`, deployed/local screenshot review
- Remaining risks: 실제 배포 반영은 feature PR merge와 release/main deploy 경로에 달려 있다.
