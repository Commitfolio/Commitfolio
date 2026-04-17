# Task: Stitch 디자인 시스템 기반 프론트 UI 구현

## Summary
- Title: Stitch 디자인 시스템 기반 프론트 UI 구현
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/32
- PRD: `docs/prd/stitch-frontend-ui.md`
- Branch: `feat/32-stitch-frontend-ui`
- PR:

## Objective
Stitch MCP 디자인 시스템과 화면 시안을 기준으로 Commitfolio 프론트의 앱 shell, 저장소 선택, 분석 진행, 결과 문서 UI를 재정렬한다. 기존 기능 동작과 테스트 문구는 유지한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Stitch project/screens/design tokens 조회
- [x] App shell/hero/preview markup 보강
- [x] CSS token과 component 스타일을 Stitch 방향으로 정리
- [x] 기존 문구/label 회귀 확인
- [x] Docs/contracts affected by the change 업데이트

## Verification Checklist
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `git diff --check`

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
- Code: `apps/frontend/src/app/App.tsx`, `apps/frontend/src/styles.css`
- Docs: `docs/prd/stitch-frontend-ui.md`, `docs/tasks/stitch-frontend-ui.md`, `.omx/plans/prd-stitch-frontend-ui.md`, `.omx/plans/test-spec-stitch-frontend-ui.md`
- Follow-up: 실제 브라우저 visual QA 피드백 반영

## Notes for Codex / OMX
- Stitch HTML은 참고용이며 Tailwind class나 mock content를 그대로 복사하지 않는다.
- 신규 dependency 없이 현재 React/Vite/TypeScript 구조를 유지한다.
- 기존 테스트가 찾는 사용자-visible text는 유지한다.

## Execution Log
- 2026-04-17: Stitch MCP 연결 확인, `Commitfolio MVP` project와 4개 주요 화면(Landing, Repository Selection, Analysis Progress, Portfolio Editor)을 확인했다.
- 2026-04-17: GitHub issue #32를 만들고 `feat/32-stitch-frontend-ui` 브랜치에서 작업을 시작했다.

## Completion Notes
- What changed: Stitch 디자인 시스템의 tonal surface, no-line sectioning, indigo gradient CTA, ambient hover shadow, commit stream motif를 App shell과 주요 feature panel CSS에 반영했다.
- Evidence: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `git diff --check` 통과.
- Remaining risks: 실제 브라우저/디바이스 visual QA는 후속 피드백으로 추가 조정할 수 있다. Manrope/Inter web font를 외부에서 강제 로드하지 않아 환경에 따라 system fallback이 사용된다.
