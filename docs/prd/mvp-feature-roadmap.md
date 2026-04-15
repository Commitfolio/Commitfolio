# Commitfolio MVP Feature Roadmap PRD

## Metadata
- Title: Commitfolio MVP staged feature roadmap
- Owner: Codex
- Status: In Progress
- Target milestone: Public MVP
- Related issue:
- Related task doc: `docs/tasks/mvp-feature-roadmap.md`

## Problem
현재 Commitfolio는 OAuth bootstrap 수직 슬라이스까지는 구현되었지만, 남은 MVP 기능을 어떤 순서로 잘라서 개발할지 저장소 안의 기준 계획서가 아직 없다. 그래서 이후 세션에서 "다음엔 뭘 해야 하는지", "어떤 기능이 선행 조건인지", "각 단계가 어디까지 끝나야 다음 단계로 갈 수 있는지"가 사람 기억이나 외부 노션에 의존하게 된다. 하네스 자동화를 제대로 활용하려면 저장소 내부에도 단계별 개발 순서와 완료 기준이 고정되어 있어야 한다.

## User
- Primary user: Commitfolio 저장소에서 연속적으로 기능 개발을 이어가는 운영자와 Codex/OMX
- Trigger: "다음 단계 진행해줘", "MVP roadmap대로 개발해줘" 같은 요청으로 다음 기능을 자동 선택하고 싶다
- Current pain: 외부 계획표를 계속 참고해야 하고, 세션마다 다음 기능 우선순위가 흔들릴 수 있다

## Goal
- Commitfolio MVP를 단계별로 쪼갠 저장소 내 기준 roadmap을 만든다.
- 각 단계마다 선행 조건, 구현 범위, 완료 조건, 다음 단계 연결점을 명시한다.
- 이후 기능 요청이 구체적이지 않아도 "roadmap의 다음 미완료 단계"를 기준으로 계획/구현을 이어갈 수 있게 한다.

## Non-goals
- 각 단계의 세부 API/스키마까지 이 문서 하나에 모두 고정
- 운영 배포, 요금제, 마케팅 계획 수립
- 모든 future nice-to-have 기능까지 한 번에 포함

## Scope
### In scope
- MVP 단계 정의
- 각 단계별 목적 / 핵심 작업 / 완료 조건 / 후속 단계 정리
- 단계별 추천 slug 및 issue/branch naming 가이드
- 현재 완료된 단계와 아직 남은 단계 구분

### Out of scope
- 각 단계의 실제 구현 코드
- GitHub issue 자동 생성 결과 자체
- 배포 인프라 세부 설정

## User Flow
1. 운영자가 "roadmap 기준으로 다음 기능 진행"을 요청한다.
2. Codex/OMX는 이 문서에서 가장 앞선 미완료 단계를 찾는다.
3. 해당 단계를 위한 issue/branch/doc slug를 만들고 구현을 시작한다.
4. 완료 기준을 충족하면 다음 단계로 넘어간다.

## Functional Requirements
- roadmap은 단계 번호와 의존 순서를 가져야 한다.
- 각 단계는 하나의 좁은 branch/PR 묶음으로 나눌 수 있어야 한다.
- 각 단계는 "done when" 형태의 완료 조건을 가져야 한다.
- 이미 완료된 `github-oauth-bootstrap` 단계는 baseline으로 표시해야 한다.
- 단계별로 추천 feature slug를 제공해야 한다.

## UX / UI Notes
- Entry point: `docs/prd/mvp-feature-roadmap.md`
- Empty / loading / error states: 없음
- Editing constraints: roadmap은 구현 순서와 경계에 집중하고, 상세 설계는 각 feature PRD로 분리한다

## API / Backend Notes
- 이 roadmap 자체는 API를 추가하지 않는다.
- 이후 단계는 아래 순서를 기준으로 API를 확장한다:
  - repositories
  - analysis jobs
  - SSE events
  - results read/update/regenerate/download

## Data / Domain Notes
- 초기 baseline: session-only OAuth slice 완료
- 다음 단계부터 `RepositorySnapshot`, `AnalysisJob`, `AnalysisEvidence`, `PortfolioResult` 중심으로 확장
- persistence 도입은 repository/analysis 단계와 함께 진행

## Acceptance Criteria
- [ ] 저장소 안에 Commitfolio MVP의 단계별 feature roadmap markdown이 존재한다
- [ ] roadmap이 현재 완료 단계와 남은 단계를 구분한다
- [ ] roadmap이 다음 구현 순서를 바로 선택할 수 있을 정도로 구체적이다
- [ ] roadmap이 각 단계의 완료 조건과 추천 slug를 포함한다

## Verification Plan
- Unit: 문서 구조 검토
- Integration: README / architecture docs / existing feature docs와 단계 순서가 모순되지 않는지 검토
- Manual: roadmap만 보고 다음 기능 issue/branch/doc slug를 사람이 선택할 수 있는지 확인

## Risks
- 외부 노션 계획과 저장소 roadmap이 어긋나면 이 문서가 빠르게 낡을 수 있다.
- 단계가 너무 크면 다시 세부 feature PRD에서 재분할이 필요하다.

## Open Questions
- "repository selection"을 단일 단계로 끝낼지, persistence 도입과 분리할지?
- PDF export를 MVP 필수로 볼지 post-MVP로 미룰지?

## Approval
- Requested by: project owner
- Approved by:
- Approved at:

## Staged Roadmap

### Stage 0 — Harness baseline
- Status: Done
- Canonical feature: `github-oauth-bootstrap`
- Why first: 인증 경계와 문서/검증 하네스의 최소 vertical slice를 먼저 검증해야 이후 기능이 안정된다.
- Done when:
  - GitHub OAuth start/callback/logout/`GET /api/v1/me` 동작
  - frontend session shell 존재
  - env example / tests / verification baseline 정리

### Stage 1 — Repository access + selection
- Status: Next
- Recommended slug: `repository-selector`
- Suggested branch: `feat/<issue>-repository-selector`
- Goal: 로그인한 사용자가 접근 가능한 저장소 목록을 보고 분석 대상을 1개 선택할 수 있어야 한다.
- Includes:
  - backend `GET /api/v1/repositories`
  - GitHub repository listing client
  - frontend repository list + select UI
  - 최소 캐시 또는 snapshot 전략 결정
- Done when:
  - 사용자에게 accessible repositories 목록이 보인다
  - public/private/org repo 구분이 가능하다
  - 하나의 repo를 선택해 다음 단계 입력으로 넘길 수 있다

### Stage 2 — Analysis job creation baseline
- Status: Planned
- Recommended slug: `analysis-job-bootstrap`
- Suggested branch: `feat/<issue>-analysis-job-bootstrap`
- Goal: 선택한 저장소에 대해 서버가 `AnalysisJob` 을 만들고 queued/running/completed/failed 상태를 가질 수 있어야 한다.
- Includes:
  - database/persistence baseline 도입
  - `POST /api/v1/analysis-jobs`
  - `GET /api/v1/analysis-jobs/{job_id}`
  - 최소 job lifecycle 모델
- Done when:
  - repo 선택 후 job row가 생성된다
  - 상태 조회 API가 동작한다
  - 실패 이유를 저장/반환할 수 있다

### Stage 3 — GitHub evidence ingestion
- Status: Planned
- Recommended slug: `github-evidence-ingestion`
- Suggested branch: `feat/<issue>-github-evidence-ingestion`
- Goal: 하나의 analysis job이 commits / PRs / issues / reviews / changed files 근거를 수집할 수 있어야 한다.
- Includes:
  - GitHub API client 확장
  - evidence normalization
  - `AnalysisEvidence` 저장 구조
  - 최소 rate-limit / permission failure handling
- Done when:
  - 한 저장소에서 근거 데이터가 수집/저장된다
  - evidence type별 최소 payload shape가 정해진다
  - 재생성 가능한 근거 보존이 가능하다

### Stage 4 — SSE progress stream
- Status: Planned
- Recommended slug: `analysis-progress-sse`
- Suggested branch: `feat/<issue>-analysis-progress-sse`
- Goal: 분석 진행 상황을 프론트에서 실시간으로 볼 수 있어야 한다.
- Includes:
  - `GET /api/v1/analysis-jobs/{job_id}/events`
  - backend progress publisher
  - frontend progress subscription UI
- Done when:
  - stage/percent 단위 progress가 보인다
  - completed/failed 이벤트를 UI가 반영한다

### Stage 5 — Portfolio result generation + view
- Status: Planned
- Recommended slug: `portfolio-result-viewer`
- Suggested branch: `feat/<issue>-portfolio-result-viewer`
- Goal: 수집한 evidence를 바탕으로 editable result 초안을 생성하고 볼 수 있어야 한다.
- Includes:
  - deterministic section builder
  - `PortfolioResult` 저장
  - `GET /api/v1/results` / `GET /api/v1/results/{result_id}`
  - frontend result view
- Done when:
  - headline / overview / contributions / tech stack / evidence summary / interview questions가 표시된다
  - result와 evidence 링크 구조가 보인다

### Stage 6 — Result editing + save/regenerate
- Status: Planned
- Recommended slug: `result-edit-and-regenerate`
- Suggested branch: `feat/<issue>-result-edit-and-regenerate`
- Goal: 사용자가 생성 결과를 수정/저장하고, 저장된 근거로 다시 생성할 수 있어야 한다.
- Includes:
  - `PATCH /api/v1/results/{result_id}`
  - `POST /api/v1/results/{result_id}/regenerate`
  - frontend editor
- Done when:
  - 수정 저장이 가능하다
  - regenerate 후 새 버전을 확인할 수 있다

### Stage 7 — PDF export
- Status: Planned
- Recommended slug: `pdf-export`
- Suggested branch: `feat/<issue>-pdf-export`
- Goal: 편집된 결과를 제출 가능한 PDF로 내보낼 수 있어야 한다.
- Includes:
  - print/export rendering strategy
  - `GET /api/v1/results/{result_id}/download.pdf`
  - frontend export trigger
- Done when:
  - PDF 다운로드가 가능하다
  - 기본 레이아웃이 읽을 수 있는 수준으로 정리된다

### Stage 8 — MVP hardening
- Status: Planned
- Recommended slug: `mvp-hardening`
- Suggested branch: `feat/<issue>-mvp-hardening`
- Goal: public MVP 공개 전 안정성, env, docs, error handling을 정리한다.
- Includes:
  - empty/error states polish
  - env/setup docs
  - auth/session/security pass
  - deployment readiness notes
- Done when:
  - 주요 happy/failure path 문서와 검증 절차가 있다
  - MVP 공개에 필요한 최소 운영 문서가 존재한다

## Default execution rule

- 기능 요청이 구체적이지 않고 "다음 단계 진행" 류의 요청이면, **가장 앞선 미완료 단계**를 다음 작업으로 간주한다.
- 현재 기준 기본 next stage는 **Stage 1 — Repository access + selection** 이다.
