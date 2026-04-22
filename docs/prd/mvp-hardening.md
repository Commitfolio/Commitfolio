# PRD: Stage 9 — MVP hardening baseline

## Metadata
- Title: Stage 9 — MVP hardening baseline
- Owner: Codex
- Status: Done
- Target milestone: Public MVP / Stage 9 hardening
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/40
- Related roadmap: `docs/prd/mvp-feature-roadmap.md`
- Related task doc: `docs/tasks/mvp-hardening.md`

## Problem
로드맵상 다음 기본 작업은 Stage 9 `mvp-hardening`이지만, 현재 저장소에는 preview smoke·CORS·에러 처리 개선 문서만 흩어져 있고 Stage 9 자체의 baseline 실행 문서와 public MVP 기준 UX/copy/readme 정리가 비어 있다. 앱에는 개발자용 메타 안내가 노출되고, README는 로컬 실행·env·배포 readiness·public/private/org 검증 흐름을 한 번에 설명하지 못한다. Stage 9를 실제 공개 배포 직전의 hardening 단계로 운영하려면 사용자가 보는 copy와 운영자가 보는 실행 문서가 같은 기준을 따라야 한다.

## User
- Primary user: Commitfolio MVP를 공개 가능한 상태로 다듬는 운영자/개발자
- Secondary user: GitHub OAuth로 저장소를 연결해 포트폴리오를 만들려는 최종 사용자
- Trigger: Stage 8 완료 이후 public MVP 직전 hardening baseline을 시작할 때
- Current pain:
  - public/private/org 저장소 지원 범위와 조직 승인 요구사항이 UI/README에 분산되어 있다.
  - local env/setup/deploy readiness를 한 번에 따라갈 기준 문서가 없다.
  - Stage 9 범위와 검증 명세가 `.omx/plans`에 별도 정리되지 않았다.

## Goal
- Stage 9 baseline 범위를 PRD / task / OMX plans로 명시한다.
- public MVP 기준의 empty/error/privacy/setup copy를 앱에 반영한다.
- README를 local setup, env, preview/prod readiness, 샘플 검증 흐름 중심으로 재구성한다.
- 실제 외부 배포 전에 개발자와 운영자가 따라갈 최소 검증 절차를 남긴다.

## Non-goals
- Render/Vercel/Neon/GitHub OAuth 콘솔 리소스를 Codex가 직접 생성하지 않는다.
- develop → main release PR이나 production deploy 실행 자체는 이번 범위에 포함하지 않는다.
- 새로운 인증 방식(GitHub App 전환, 세분화 scope 재설계)을 도입하지 않는다.
- 제품 정보 구조를 대규모로 재설계하거나 라우터/상태 라이브러리를 새로 추가하지 않는다.

## Scope
### In scope
- `docs/prd/mvp-hardening.md`, `docs/tasks/mvp-hardening.md`, `.omx/plans/prd-mvp-hardening.md`, `.omx/plans/test-spec-mvp-hardening.md` 생성
- public MVP 기준 안내 패널과 permission/privacy/setup copy 정리
- raw 개발자용 meta 안내 제거 또는 public-friendly 안내로 교체
- root `README.md`를 실행/환경/검증/데모 중심으로 확장
- public/private/org 샘플 검증 체크리스트 문서화

### Out of scope
- 실제 production env/secrets 입력
- Render/Vercel/Neon/GitHub OAuth 콘솔 작업 수행
- backend API contract 변경
- DB schema migration 추가

## User Flow
1. 사용자가 landing 영역에서 Commitfolio의 지원 범위와 검증 대상(public/private/org repo)을 이해한다.
2. 사용자가 GitHub 로그인 전/후에 권한·개인정보·조직 승인 안내를 확인한다.
3. 사용자가 저장소 선택 단계에서 “메타데이터 먼저 조회 → 선택한 저장소만 분석” 흐름을 이해한다.
4. 운영자는 README를 따라 local setup, env 준비, preview readiness, 샘플 검증을 재현한다.
5. 실제 public deployment는 operator playbook 사용자 액션을 따라 별도 수행한다.

## Functional Requirements
- 앱은 개발자 전용 raw URL 노출 대신 public MVP 기준 안내를 제공해야 한다.
- 로그인/저장소/분석 단계 copy는 권한 범위, 조직 OAuth 승인, 선택 저장소 단일 분석 범위를 설명해야 한다.
- README는 frontend/backend 로컬 실행 순서와 핵심 env 이름을 설명해야 한다.
- README는 preview/prod readiness 및 public/private/org 저장소 검증 시나리오를 설명해야 한다.
- Stage 9 baseline 산출물은 GitHub issue와 브랜치 규칙에 연결돼야 한다.

## UX / UI Notes
- hero 아래에 public MVP readiness 안내 패널을 추가한다.
- signed-out / signed-in / repository selection / analysis state 주변 copy를 hardening 기준으로 다듬는다.
- 지나치게 내부 구현 세부사항을 노출하지 않으면서도 permission/privacy expectation은 분명히 적는다.

## API / Backend Notes
- 새 endpoint 없음.
- 기존 OAuth/session/error contract 유지.
- README와 UI copy는 이미 존재하는 backend env와 preview smoke 체계를 참조한다.

## Data / Domain Notes
- 테이블/엔티티 변경 없음.
- 사용자 데이터 범위 설명은 현재 구현(세션 + 선택 저장소 분석)에 맞춘다.

## Acceptance Criteria
- [x] Stage 9 baseline 문서 4종(PRD/task/OMX plan/test spec)이 생성된다.
- [x] 앱에서 raw auth/backend meta 안내가 public-friendly hardening 안내로 대체된다.
- [x] signed-out / signed-in / repository selection / analysis copy가 permission/privacy/setup 기준을 설명한다.
- [x] `README.md`가 local setup, env, preview readiness, public/private/org validation, demo flow를 설명한다.
- [x] frontend lint/typecheck/test/build와 `git diff --check`가 통과한다.

## Verification Plan
- Regression: `npm --prefix apps/frontend run lint`
- Regression: `npm --prefix apps/frontend run typecheck`
- Regression: `npm --prefix apps/frontend run test -- --run`
- Regression: `npm --prefix apps/frontend run build`
- Regression: `git diff --check`

## Risks
- 실제 public deployment 완료 여부는 외부 콘솔 사용자 액션이 필요하므로 이번 PR만으로 닫히지 않는다.
- UI copy는 public MVP 기준으로 안전하게 축약하지만, 법률 검토 수준의 privacy policy를 대체하지는 않는다.
- README 강화만으로 onboarding friction이 완전히 사라지지 않을 수 있다.

## Open Questions
- Stage 9 후속 slice에서 외부 observability 도입 여부를 별도 PRD로 분리할지 결정해야 한다.
- public MVP에서 OAuth App 유지 여부와 GitHub App 전환 검토 시점을 정해야 한다.

## Approval
- Requested by: User
- Approved by: User request
- Approved at: 2026-04-22
