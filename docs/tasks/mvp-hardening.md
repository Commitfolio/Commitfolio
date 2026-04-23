# Task: Stage 9 — MVP hardening baseline

## Summary
- Title: Stage 9 — MVP hardening baseline
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/40
- PRD: `docs/prd/mvp-hardening.md`
- Branch: `feat/40-mvp-hardening`
- PR: https://github.com/Commitfolio/Commitfolio/pull/41

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
- [x] release smoke mode / JSON report artifact 추가
- [x] operator playbook / README를 release smoke 흐름에 맞게 보강
- [x] smoke script 검증 실행
- [x] completion notes 업데이트

## Verification Checklist
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `python3 -m unittest discover -s scripts/deployment -p 'test_*.py'`
- [x] `git diff --check`

## Default Verification Commands
Reference: `docs/playbooks/verification-baseline.md`

```bash
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
npm --prefix apps/frontend run build
python3 -m unittest discover -s scripts/deployment -p 'test_*.py'
git diff --check
```

## Deliverables
- Code: `apps/frontend/src/app/App.tsx`, `apps/frontend/src/features/github-auth/SessionPanel.tsx`, `apps/frontend/src/features/repository-selector/RepositorySelector.tsx`, `apps/frontend/src/features/analysis-job/AnalysisJobPanel.tsx`, `apps/frontend/src/features/mvp-readiness/PublicMvpGuidePanel.tsx`, `apps/frontend/src/styles.css`, `apps/frontend/src/App.test.tsx`, `scripts/deployment/preview_smoke.py`, `scripts/deployment/test_preview_smoke.py`
- Docs: `README.md`, `docs/prd/mvp-hardening.md`, `docs/tasks/mvp-hardening.md`, `.omx/plans/prd-mvp-hardening.md`, `.omx/plans/test-spec-mvp-hardening.md`, `docs/playbooks/operator-deployment-actions.md`

## Notes for Codex / OMX
- `.codex/skills/ralph/SKILL.md`의 기존 수정사항은 이번 작업 범위가 아니므로 건드리지 않는다.
- 실제 Render/Vercel/Neon/OAuth 콘솔 작업은 사용자 액션으로 남긴다.
- 기존 사용자-visible 텍스트를 바꾸는 만큼 frontend 테스트를 함께 갱신한다.

## Execution Log
- 2026-04-22: roadmap 기준 다음 단계가 Stage 9 `mvp-hardening`임을 확인했다.
- 2026-04-22: GitHub issue #40과 `feat/40-mvp-hardening` 브랜치를 만들었다.
- 2026-04-22: public MVP readiness 안내 패널, permission/privacy copy, README baseline 문서를 추가했다.
- 2026-04-22: frontend lint/typecheck/test/build와 `git diff --check`를 통과했다.
- 2026-04-22: draft PR #41을 열어 develop 기준 검토 상태로 전환했다.
- 2026-04-23: Stage 9 후속 slice로 release smoke/report artifact 강화를 같은 PR 범위에서 진행하기로 정했다.
- 2026-04-23: `preview_smoke.py`에 backend/preview/release mode, unauthenticated `/api/v1/me` contract 체크, JSON report 출력을 추가했다.
- 2026-04-23: operator playbook/README에 release smoke artifact 절차를 반영하고, frontend/script 검증을 다시 통과했다.
- 2026-04-23: 실제 배포 URL을 GitHub/Vercel 단서에서 자동 탐색해 backend `https://commitfolio.onrender.com`, production frontend `https://commitfolio.vercel.app`, Vercel environment URL `https://commitfolio-k264n7ust-dongguli08s-projects.vercel.app`를 확인했다.
- 2026-04-23: release smoke는 production/custom domain과 Vercel environment URL에서 모두 통과했고, branch preview URL `https://commitfolio-git-feat-40-mvp-hardening-dongguli08s-projects.vercel.app`는 CORS preflight 400으로 실패했다.

## Completion Notes
- What changed: Stage 9 baseline 위에 release smoke/report artifact slice를 추가해 `preview_smoke.py`가 mode별 검증과 JSON report 출력을 지원하도록 확장했다. 또한 operator playbook, README, roadmap 상태를 새 증적 흐름에 맞게 정리했다.
- Evidence: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `python3 -m unittest discover -s scripts/deployment -p 'test_*.py'`, `python3 scripts/deployment/preview_smoke.py --help`, `python3 scripts/deployment/preview_smoke.py --mode preview --backend-url https://commitfolio.onrender.com --frontend-url https://commitfolio-git-feat-40-mvp-hardening-dongguli08s-projects.vercel.app --expected-frontend-api-base https://commitfolio.onrender.com --report-json .omx/reports/preview-smoke-2026-04-23.json`, `python3 scripts/deployment/preview_smoke.py --mode release --backend-url https://commitfolio.onrender.com --frontend-url https://commitfolio.vercel.app --expected-frontend-api-base https://commitfolio.onrender.com --report-json .omx/reports/release-smoke-commitfolio-vercel-2026-04-23.json`, `python3 scripts/deployment/preview_smoke.py --mode release --backend-url https://commitfolio.onrender.com --frontend-url https://commitfolio-k264n7ust-dongguli08s-projects.vercel.app --expected-frontend-api-base https://commitfolio.onrender.com --report-json .omx/reports/release-smoke-vercel-envurl-2026-04-23.json`, `git diff --check`
- Remaining risks: Render CORS 허용 목록에 PR branch preview alias가 포함되지 않아 branch preview URL에서는 로그인/세션 흐름이 실패할 수 있다. 또한 실제 public/private/org 저장소 사용자 시나리오 smoke와 secret rotation은 여전히 사용자 액션이 필요하다.
