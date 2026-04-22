# Task: Stage 9 — MVP hardening baseline

## Summary
- Title: Stage 9 — MVP hardening baseline
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/40
- PRD: `docs/prd/mvp-hardening.md`
- Branch: `feat/40-mvp-hardening`
- PR:

## Objective
public MVP 직전 baseline으로서 Stage 9 문서 체계, public-facing UX copy, README/env/setup 안내를 정리한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] GitHub issue 생성 및 branch 규칙 연결
- [x] Stage 9 baseline PRD / task / OMX plans 생성
- [x] public MVP 안내 패널 및 permission/privacy/setup copy 정리
- [x] raw 개발자용 meta 안내 제거
- [x] `README.md` 실행/환경/검증/데모 문서화
- [x] frontend 검증 실행
- [x] completion notes 업데이트

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
- Code: `apps/frontend/src/app/App.tsx`, `apps/frontend/src/features/github-auth/SessionPanel.tsx`, `apps/frontend/src/features/repository-selector/RepositorySelector.tsx`, `apps/frontend/src/features/analysis-job/AnalysisJobPanel.tsx`, `apps/frontend/src/features/mvp-readiness/PublicMvpGuidePanel.tsx`, `apps/frontend/src/styles.css`, `apps/frontend/src/App.test.tsx`
- Docs: `README.md`, `docs/prd/mvp-hardening.md`, `docs/tasks/mvp-hardening.md`, `.omx/plans/prd-mvp-hardening.md`, `.omx/plans/test-spec-mvp-hardening.md`

## Notes for Codex / OMX
- `.codex/skills/ralph/SKILL.md`의 기존 수정사항은 이번 작업 범위가 아니므로 건드리지 않는다.
- 실제 Render/Vercel/Neon/OAuth 콘솔 작업은 사용자 액션으로 남긴다.
- 기존 사용자-visible 텍스트를 바꾸는 만큼 frontend 테스트를 함께 갱신한다.

## Execution Log
- 2026-04-22: roadmap 기준 다음 단계가 Stage 9 `mvp-hardening`임을 확인했다.
- 2026-04-22: GitHub issue #40과 `feat/40-mvp-hardening` 브랜치를 만들었다.
- 2026-04-22: public MVP readiness 안내 패널, permission/privacy copy, README baseline 문서를 추가했다.
- 2026-04-22: frontend lint/typecheck/test/build와 `git diff --check`를 통과했다.

## Completion Notes
- What changed: Stage 9 전용 PRD/task/OMX plan을 만들고, 앱에서 raw 개발자용 meta 안내를 제거한 뒤 public MVP readiness 패널과 권한/개인정보 copy를 추가했다. 또한 README를 local setup, env, preview readiness, 샘플 검증, 데모 흐름 중심으로 재작성했다.
- Evidence: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `git diff --check`
- Remaining risks: 실제 Render/Vercel/Neon/GitHub OAuth 공개 배포와 secret 반영은 여전히 사용자 액션이 필요하다.
