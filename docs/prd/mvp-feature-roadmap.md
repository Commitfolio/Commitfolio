# Commitfolio MVP Feature Roadmap PRD

## Metadata
- Title: Commitfolio MVP staged feature roadmap
- Owner: Codex
- Status: In Progress
- Target milestone: Public MVP
- Target schedule: 2026-04-14 ~ 2026-05-04
- Source alignment: Notion `Commitfolio` page (`https://www.notion.so/342d2f213afe80a69677d469ac885410`), fetched via Notion MCP at 2026-04-14T12:07:31.061Z
- Related issue:
- Related task doc: `docs/tasks/mvp-feature-roadmap.md`

## Problem
현재 Commitfolio는 OAuth bootstrap 수직 슬라이스까지는 구현되었지만, 남은 MVP 기능을 어떤 순서로 잘라서 개발할지 저장소 안의 기준 계획서가 외부 Notion 계획과 완전히 동기화되어 있지 않다. 그래서 이후 세션에서 "다음엔 뭘 해야 하는지", "어떤 기능이 선행 조건인지", "각 단계가 어디까지 끝나야 다음 단계로 갈 수 있는지"가 사람 기억이나 외부 문서에 의존할 수 있다.

하네스 자동화를 제대로 활용하려면 저장소 내부에도 3주 공개 MVP 목표, 제품 범위, 기술 스택, 단계별 개발 순서, 완료 기준이 고정되어 있어야 한다.

## User
- Primary user: Commitfolio 저장소에서 연속적으로 기능 개발을 이어가는 운영자와 Codex/OMX
- Trigger: "다음 단계 진행해줘", "MVP roadmap대로 개발해줘" 같은 요청으로 다음 기능을 자동 선택하고 싶다
- Current pain: 외부 계획표를 계속 참고해야 하고, 세션마다 다음 기능 우선순위가 흔들릴 수 있다

## Goal
- Commitfolio MVP를 단계별로 쪼갠 저장소 내 기준 roadmap을 만든다.
- GitHub OAuth 기반 단일 repository 분석 서비스라는 핵심 제품 방향을 고정한다.
- 2026-05-04까지 포트폴리오에 넣을 수 있을 정도의 공개 MVP를 배포하는 3주 실행 계획을 저장소 문서에 반영한다.
- 각 단계마다 선행 조건, 구현 범위, 완료 조건, 다음 단계 연결점을 명시한다.
- 이후 기능 요청이 구체적이지 않아도 "roadmap의 다음 미완료 단계"를 기준으로 계획/구현을 이어갈 수 있게 한다.

## Product Definition
GitHub OAuth로 사용자가 접근 가능한 public/private/org repository를 불러오고, 사용자가 선택한 **단일 프로젝트**의 활동 데이터를 분석해 포트폴리오 형태의 결과물을 생성하고 수정 및 다운로드할 수 있는 서비스.

## Confirmed Product Direction
- 로그인: **GitHub OAuth 필수**
- 분석 대상: OAuth로 접근 가능한 public/private/org repo
- 분석 단위: 사용자가 선택한 **단일 repository**
- 분석 데이터: `commit`, `PR`, `issue`, `review`, `changed files`
- 결과 저장: 저장 후 최근 결과 다시 보기 및 재분석 가능
- 진행 상태: **SSE** 기반 실시간 상태 표시
- 결과 사용성: 텍스트 직접 수정 가능
- 다운로드: **PDF 포함**
- 결과 섹션: 한 줄 소개, 프로젝트 개요, 담당 역할, 핵심 기여 내용, 기술 스택, 활동/근거 요약, 면접 예상 질문
- 근거 표시: 결과 문장에 PR/commit/issue 근거 링크 표시
- 권한 정책: 최소 권한 요청, 분석 목적 외 재활용 없음 안내

## Portfolio Proof Points
- **자동화 / 하네스 엔지니어링** 중심 개발 시스템 설계
- **백엔드 + 프론트엔드 + 배포**를 혼자 끝까지 만든 end-to-end 구현 능력
- GitHub 활동 데이터를 구조화하고 포트폴리오 문장으로 바꾸는 제품 설계 능력
- 실사용 가능한 UX와 결과물 퀄리티

## Harness / Automation Notes
- 개발 자체보다 `요청 -> 브리핑 -> 문서화 -> 이슈/브랜치 -> 구현 -> 검증 -> PR` 흐름을 시스템화하는 것을 제품의 일부로 취급한다.
- 기능 개발 전에 `AGENTS.md`, PRD/task 템플릿, issue/PR 템플릿, architecture docs, playbooks를 기준 문서로 유지한다.
- 모든 구현 작업은 관련 md 문서와 연결되어야 하며, 완료 기준은 코드 작성이 아니라 테스트 + 문서 + PR 준비 상태까지 포함한다.
- 승인 checkpoint가 명시된 요청은 `docs/playbooks/feature-delivery.md`를 따르고, 기본 기능 흐름은 `docs/playbooks/default-feature-flow.md`와 AGENTS.md의 auto-continue 규칙을 따른다.

## Non-goals
- 각 단계의 세부 API/스키마까지 이 문서 하나에 모두 고정
- 요금제, 결제, 마케팅 계획 수립
- 다중 프로젝트 통합 포트폴리오
- 다국어 지원
- 공개 링크 공유 기능
- 고급 레이아웃 커스터마이징
- OpenAI API 없이는 동작하지 않는 생성 파이프라인

## Scope
### In scope
- MVP 단계 정의
- 각 단계별 목적 / 핵심 작업 / 완료 조건 / 후속 단계 정리
- 단계별 추천 slug 및 issue/branch naming 가이드
- 현재 완료된 단계와 아직 남은 단계 구분
- 3주 공개 MVP 일정의 주차별 목표 반영
- 핵심 기술 스택과 배포 조합의 roadmap 기준화
- 권한/개인정보 안내, 근거 링크, 결과 저장/수정/PDF 같은 필수 MVP 범위 고정

### Out of scope
- 각 단계의 실제 구현 코드
- GitHub issue 자동 생성 결과 자체
- 배포 인프라 세부 설정
- 운영 비용/모니터링/마케팅 세부 계획

## Technical Stack Baseline
| Area | Choice | Why |
| --- | --- | --- |
| Frontend | React + Vite + TypeScript | 3주 MVP에 유리한 개발 속도와 FastAPI 분리 운영 용이성 |
| UI | Tailwind CSS + shadcn/ui | 밝고 깔끔한 MVP UI를 빠르게 구성하기 적합 |
| Server | Python + FastAPI | 비동기 API, GitHub 연동, 분석 파이프라인 구현에 적합 |
| DB | PostgreSQL (Neon) | 분석 결과 저장, 재분석 이력 관리에 적합 |
| ORM / Migration | SQLAlchemy 2.x + Alembic | 정석적인 Python 백엔드 구조와 마이그레이션 관리 |
| Server data fetch | httpx | GitHub API 및 외부 API 호출용 |
| Frontend server-state | TanStack Query | 분석 요청, 상태 조회, 재분석, 결과 캐싱 관리 |
| Routing | React Router | 단순하고 충분한 라우팅 구조 |
| Realtime status | SSE | 분석 진행 상태를 WebSocket보다 단순하게 전달 |
| Deploy | Vercel + Render free + Neon free | 3주 MVP 배포에 맞는 현실적인 무료 조합 |
| AI generation | 초기 규칙 기반 + 후반 OpenAI API 연결 | 초기 리스크를 줄이고 마지막 주에 결과 품질 개선 |

## Product User Flow
1. GitHub OAuth 로그인
2. 사용자가 접근 가능한 repository 목록 조회
3. 포트폴리오를 만들고 싶은 **단일 프로젝트 선택**
4. 권한 및 수집 범위 안내 확인
5. 분석 실행
6. SSE로 진행 상태 표시
7. 포트폴리오 결과 화면 생성
8. 사용자가 텍스트 일부 수정
9. PDF 다운로드 또는 저장된 결과 다시 보기

## Roadmap Operator Flow
1. 운영자가 "roadmap 기준으로 다음 기능 진행"을 요청한다.
2. Codex/OMX는 이 문서에서 가장 앞선 미완료 단계를 찾는다.
3. 해당 단계를 위한 issue/branch/doc slug를 만들고 구현을 시작한다.
4. 완료 기준을 충족하면 다음 단계로 넘어간다.

## Functional Requirements
### Roadmap requirements
- roadmap은 단계 번호와 의존 순서를 가져야 한다.
- 각 단계는 하나의 좁은 branch/PR 묶음으로 나눌 수 있어야 한다.
- 각 단계는 "done when" 형태의 완료 조건을 가져야 한다.
- 이미 완료된 `github-oauth-bootstrap` 단계는 baseline으로 표시해야 한다.
- 단계별로 추천 feature slug를 제공해야 한다.

### MVP product requirements
- GitHub OAuth 로그인과 로그아웃이 가능해야 한다.
- 사용자가 접근 가능한 public/private/org repo 목록을 조회할 수 있어야 한다.
- 사용자는 분석할 단일 repository를 선택할 수 있어야 한다.
- commit / PR / issue / review / changed files 데이터를 수집할 수 있어야 한다.
- analysis job을 생성하고 queued/running/completed/failed 상태를 관리할 수 있어야 한다.
- SSE 기반 진행 상태를 UI에 표시해야 한다.
- 포트폴리오 결과를 생성하고 저장할 수 있어야 한다.
- 최근 결과를 다시 볼 수 있어야 한다.
- 결과 텍스트를 수정할 수 있어야 한다.
- PDF 다운로드가 가능해야 한다.
- 결과 문장에 근거 링크를 표시해야 한다.
- 권한 및 개인정보 안내 문구를 제공해야 한다.

## UX / UI Notes
- Entry point: `docs/prd/mvp-feature-roadmap.md`
- Product UI tone: 어두운 화면보다 **밝은 톤 기반** 우선
- 첫 화면에서 서비스가 무엇을 하는지 바로 이해되어야 한다.
- 분석 중 / 완료 / 수정 가능 상태를 명확히 구분한다.
- 포트폴리오 결과는 "읽기 쉬운 문서"처럼 보여야 한다.
- 결과 화면은 한 줄 소개, 프로젝트 개요, 역할, 기여, 기술 스택, 근거 요약, 면접 질문을 문서형 레이아웃으로 보여준다.
- Empty / loading / error states는 MVP hardening 단계에서 주요 흐름 중심으로 정리한다.
- Editing constraints: roadmap은 구현 순서와 경계에 집중하고, 상세 설계는 각 feature PRD로 분리한다.

## API / Backend Notes
- 이 roadmap 자체는 API를 추가하지 않는다.
- 이후 단계는 아래 순서를 기준으로 API를 확장한다:
  - repositories
  - analysis jobs
  - GitHub evidence ingestion
  - SSE events
  - results read/update/regenerate/download
- 권장 핵심 endpoint:
  - `GET /api/v1/repositories`
  - `POST /api/v1/analysis-jobs`
  - `GET /api/v1/analysis-jobs/{job_id}`
  - `GET /api/v1/analysis-jobs/{job_id}/events`
  - `POST /api/v1/analysis-jobs/{job_id}/result`
  - `GET /api/v1/results`
  - `GET /api/v1/results/{result_id}`
  - `PATCH /api/v1/results/{result_id}`
  - `POST /api/v1/results/{result_id}/regenerate`
  - `GET /api/v1/results/{result_id}/download.pdf`

## Data / Domain Notes
- 초기 baseline: session-only OAuth slice 완료
- 다음 단계부터 `RepositorySnapshot`, `AnalysisJob`, `AnalysisEvidence`, `PortfolioResult` 중심으로 확장
- persistence 도입은 repository snapshot 전략 결정 후 analysis job 단계에서 본격화한다.
- 최소 OAuth 권한으로 시작한다.
- 사용자에게 어떤 데이터를 읽는지 명확히 보여준다.
- 분석 목적 외 데이터 재활용을 하지 않는다는 안내를 제공한다.
- 각 포트폴리오 문장에는 가능한 한 PR, commit, issue 링크를 근거로 붙인다.

## 3-week Delivery Windows
| Week | Dates | Core goal | Main exit criteria |
| --- | --- | --- | --- |
| Week 1 | 2026-04-14 ~ 2026-04-20 | 기반 설계 + 하네스 셋업 + GitHub 연동 + 기본 데이터 수집 | Monorepo, OAuth, repo 조회, 문서/자동화 골격 완성 |
| Week 2 | 2026-04-21 ~ 2026-04-27 | 분석 파이프라인 + 결과 생성 + 결과 화면 완성 | 단일 프로젝트 분석 후 결과 화면까지 연결 |
| Week 3 | 2026-04-28 ~ 2026-05-04 | 수정/다운로드/안정화/배포 | PDF 다운로드, QA, 공개 배포 완료 |

## Schedule Guardrails
- 평일 3시간, 주말 4시간 기준으로 작업량을 제한한다.
- 하루 작업은 반드시 끝나는 단위로 쪼갠다.
- 2주차 종료 이후 신규 기능 추가를 금지한다.
- OpenAI API 연결은 마지막 주로 미뤄 초기 리스크를 줄인다.
- 규칙 기반 결과 구조가 먼저 동작해야 하며, OpenAI 연결은 결과 품질 개선 레이어로 붙인다.
- OAuth, SSE, PDF 다운로드는 필수지만 난이도가 있으므로 일정 버퍼를 확보한다.

## Acceptance Criteria
- [ ] 저장소 안에 Commitfolio MVP의 단계별 feature roadmap markdown이 존재한다
- [ ] roadmap이 현재 완료 단계와 남은 단계를 구분한다
- [ ] roadmap이 다음 구현 순서를 바로 선택할 수 있을 정도로 구체적이다
- [ ] roadmap이 각 단계의 완료 조건과 추천 slug를 포함한다
- [ ] roadmap이 Notion의 3주 MVP 일정, 확정 범위, 기술 스택, 권한 원칙을 반영한다

## MVP Completion Criteria
- [ ] GitHub 로그인 후 repo 목록이 정상 조회된다.
- [ ] 선택한 repo에 대해 analysis job이 생성된다.
- [ ] SSE로 진행 상태가 보인다.
- [ ] 포트폴리오 결과가 화면에 생성된다.
- [ ] 결과를 사용자가 수정할 수 있다.
- [ ] 결과를 PDF로 다운로드할 수 있다.
- [ ] 최근 결과를 다시 볼 수 있다.
- [ ] public/private/org repo 케이스를 최소 샘플로 검증했다.
- [ ] Vercel / Render / Neon 환경에서 공개 배포가 완료되었다.

## Verification Plan
- Unit: 문서 구조 검토
- Integration: README / architecture docs / existing feature docs와 단계 순서가 모순되지 않는지 검토
- Manual: roadmap만 보고 다음 기능 issue/branch/doc slug를 사람이 선택할 수 있는지 확인
- Manual: Notion 원문과 비교해 MVP 필수 기능, 기술 스택, 일정, 리스크가 누락되지 않았는지 확인

## Risks
- 외부 Notion 계획과 저장소 roadmap이 어긋나면 이 문서가 빠르게 낡을 수 있다.
- 단계가 너무 크면 다시 세부 feature PRD에서 재분할이 필요하다.
- GitHub OAuth 및 private/org repo 권한 처리가 예상보다 오래 걸릴 수 있다.
- GitHub API rate limit 및 데이터 수집 복잡도가 분석 품질을 제한할 수 있다.
- PDF 출력 레이아웃 이슈가 마지막 주 QA를 압박할 수 있다.
- LLM 결과 품질 편차 때문에 OpenAI 연결이 일정 대비 효과를 내지 못할 수 있다.
- 1인 개발 기준 일정 초과 가능성이 있다.

## Risk Responses
- 1주차 안에 OAuth와 repo 조회를 끝내지 못하면 즉시 scope를 조정한다.
- LLM 연결 전에도 동작하는 규칙 기반 결과 구조를 먼저 완성한다.
- PDF는 브라우저 print/export 전략을 fallback으로 준비한다.
- 필수 기능 외 추가 실험은 모두 백로그로 이동한다.
- private/org repo 권한 실패는 사용자에게 수집 불가 이유를 명확히 보여준다.

## Resolved Decisions
- `repository selection`은 Stage 1에서 독립 단계로 끝내고, persistence 본격 도입은 Stage 2로 분리한다.
- PDF export는 MVP 필수로 유지한다.
- OpenAI API는 MVP 핵심 경로의 전제 조건이 아니라 마지막 주 결과 품질 개선 레이어로 둔다.

## Open Questions
- OpenAI API 연결을 Stage 7의 필수 완료 조건으로 볼지, 일정 위험 시 optional polish로 둘지?
- PDF 생성 방식을 서버 렌더링으로 둘지, browser print 기반 export로 시작할지?

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
- Status: Done
- Recommended slug: `repository-selector`
- Suggested branch: `feat/<issue>-repository-selector`
- Goal: 로그인한 사용자가 접근 가능한 저장소 목록을 보고 분석 대상을 1개 선택할 수 있어야 한다.
- Includes:
  - backend `GET /api/v1/repositories`
  - GitHub repository listing client
  - public/private/org repository metadata 표시
  - 권한 및 수집 범위 안내 문구
  - frontend repository list + select UI
  - 최소 캐시 또는 snapshot 전략 결정
- Done when:
  - 사용자에게 accessible repositories 목록이 보인다
  - public/private/org repo 구분이 가능하다
  - 하나의 repo를 선택해 다음 단계 입력으로 넘길 수 있다
  - 어떤 GitHub 데이터를 읽는지 사용자에게 안내된다

### Stage 2 — Analysis job creation baseline
- Status: Done
- Recommended slug: `analysis-job-bootstrap`
- Suggested branch: `feat/<issue>-analysis-job-bootstrap`
- Goal: 선택한 저장소에 대해 서버가 `AnalysisJob` 을 만들고 queued/running/completed/failed 상태를 가질 수 있어야 한다.
- Includes:
  - PostgreSQL persistence baseline 도입
  - SQLAlchemy 2.x + Alembic migration baseline
  - repository snapshot 저장 전략
  - `POST /api/v1/analysis-jobs`
  - `GET /api/v1/analysis-jobs/{job_id}`
  - 최소 job lifecycle 모델
- Done when:
  - repo 선택 후 job row가 생성된다
  - 상태 조회 API가 동작한다
  - 실패 이유를 저장/반환할 수 있다
  - Neon/PostgreSQL 기준 env/setup 문서가 최신이다

### Stage 3 — GitHub evidence ingestion
- Status: Done
- Recommended slug: `github-evidence-ingestion`
- Suggested branch: `feat/<issue>-github-evidence-ingestion`
- Goal: 하나의 analysis job이 commits / PRs / issues / reviews / changed files 근거를 수집할 수 있어야 한다.
- Includes:
  - GitHub API client 확장 (`httpx`)
  - commits / PRs / issues / reviews / changed files 수집
  - evidence normalization
  - `AnalysisEvidence` 저장 구조
  - 최소 rate-limit / permission failure handling
- Done when:
  - 한 저장소에서 근거 데이터가 수집/저장된다
  - evidence type별 최소 payload shape가 정해진다
  - 재생성 가능한 근거 보존이 가능하다
  - 권한 부족, rate limit, 빈 repository 케이스가 실패 이유로 구분된다

### Stage 4 — SSE progress stream
- Status: Done
- Recommended slug: `analysis-progress-sse`
- Suggested branch: `feat/<issue>-analysis-progress-sse`
- Goal: 분석 진행 상황을 프론트에서 실시간으로 볼 수 있어야 한다.
- Includes:
  - `GET /api/v1/analysis-jobs/{job_id}/events`
  - backend progress publisher
  - frontend progress subscription UI
  - TanStack Query와 SSE 상태 동기화
- Done when:
  - stage/percent 단위 progress가 보인다
  - completed/failed 이벤트를 UI가 반영한다
  - 분석 중 / 완료 / 실패 상태가 사용자에게 명확히 구분된다

### Stage 5 — Portfolio result generation + view
- Status: Done
- Recommended slug: `portfolio-result-viewer`
- Suggested branch: `feat/<issue>-portfolio-result-viewer`
- Goal: 수집한 evidence를 바탕으로 editable result 초안을 생성하고 볼 수 있어야 한다.
- Includes:
  - deterministic section builder
  - headline / overview / role / contributions / tech stack / evidence summary / interview questions section shape
  - evidence link attachment
  - `PortfolioResult` 저장
  - `GET /api/v1/results` / `GET /api/v1/results/{result_id}`
  - frontend result view
- Done when:
  - 한 줄 소개 / 프로젝트 개요 / 담당 역할 / 핵심 기여 내용 / 기술 스택 / 활동·근거 요약 / 면접 예상 질문이 표시된다
  - result와 evidence 링크 구조가 보인다
  - 최근 결과 목록의 최소 조회 경로가 존재한다

### Stage 6 — Result editing + save/regenerate
- Status: Done
- Recommended slug: `result-edit-and-regenerate`
- Suggested branch: `feat/<issue>-result-edit-and-regenerate`
- Goal: 사용자가 생성 결과를 수정/저장하고, 저장된 근거로 다시 생성할 수 있어야 한다.
- Includes:
  - `PATCH /api/v1/results/{result_id}`
  - `POST /api/v1/results/{result_id}/regenerate`
  - frontend editor
  - saved result history / recent result revisit flow
- Done when:
  - 수정 저장이 가능하다
  - regenerate 후 새 버전을 확인할 수 있다
  - 저장된 결과를 다시 열 수 있다

### Stage 7 — Result quality polish + optional OpenAI
- Status: Done
- Recommended slug: `result-quality-polish`
- Suggested branch: `feat/<issue>-result-quality-polish`
- Goal: 규칙 기반 결과를 유지하면서, 일정이 허용하면 OpenAI API 후처리로 문장 품질과 면접 질문 품질을 높인다.
- Includes:
  - deterministic generator fallback 유지
  - OpenAI API 연결을 선택형 enhancement로 분리
  - 면접 예상 질문 품질 조정
  - LLM 실패/미설정 시 graceful fallback
- Done when:
  - OpenAI 키가 없어도 기본 결과 생성이 동작한다
  - OpenAI 키가 있으면 더 자연스러운 포트폴리오 문장으로 개선된다
  - LLM 결과와 기존 근거 링크 구조가 분리되지 않는다

### Operational checkpoint — Neon DB connection smoke
- Status: Recommended before or immediately after Stage 8
- Reference: `docs/playbooks/operator-deployment-actions.md`
- Goal: 공개 배포 전에 Neon/PostgreSQL `DATABASE_URL`로 Alembic migration과 최소 backend smoke를 검증한다.
- Includes:
  - 사용자가 Neon project/database/role 생성
  - 사용자가 connection string을 확보하고 로컬 또는 Render env에 입력
  - Codex/OMX가 `alembic upgrade head`, DB `select 1`, `/healthz` smoke 확인
- Done when:
  - Neon DB에서 migration이 성공한다
  - backend가 Neon DB URL로 시작된다
  - secret을 Git에 남기지 않고 검증 evidence만 task/PR에 기록된다

### Stage 8 — PDF export
- Status: Done
- Recommended slug: `pdf-export`
- Suggested branch: `feat/<issue>-pdf-export`
- Goal: 편집된 결과를 제출 가능한 PDF로 내보낼 수 있어야 한다.
- Includes:
  - print/export rendering strategy
  - browser print fallback 또는 server-side PDF strategy 결정
  - browser print/save-as-PDF fallback
  - frontend export trigger
- Done when:
  - PDF 다운로드가 가능하다
  - 기본 레이아웃이 읽을 수 있는 수준으로 정리된다
  - 실패 시 사용자에게 fallback 안내가 보인다

### Operational checkpoint — Render/Vercel preview deployment smoke
- Status: Next recommended before Stage 9 public release
- Reference: `docs/playbooks/operator-deployment-actions.md`
- Goal: Stage 9를 첫 배포가 아니라 hardening/release 단계로 만들기 위해 preview backend/frontend를 먼저 연결한다.
- Includes:
  - 사용자가 Render backend service 생성 및 env 입력
  - 사용자가 Vercel frontend project 생성 및 `VITE_API_BASE_URL` 입력
  - 사용자가 GitHub OAuth App callback URL을 Render backend callback으로 설정
  - Codex/OMX가 `/healthz`, frontend API URL, OAuth start/callback, SSE 가능성을 smoke 확인
- Done when:
  - Render backend URL과 Vercel frontend URL이 존재한다
  - frontend가 localhost가 아니라 Render backend를 호출한다
  - OAuth callback URL/env가 서로 일치한다

### Stage 9 — MVP hardening + public deployment
- Status: Planned
- Recommended slug: `mvp-hardening`
- Suggested branch: `feat/<issue>-mvp-hardening`
- Goal: public MVP 공개 전 안정성, env, docs, error handling, 배포를 정리한다.
- Includes:
  - empty/error states polish
  - env/setup docs
  - auth/session/security pass
  - permission/privacy copy review
  - Vercel / Render / Neon deployment readiness
  - README/demo explanation
  - public/private/org repo sample validation
- Done when:
  - 주요 happy/failure path 문서와 검증 절차가 있다
  - 권한 안내, 데이터 부족, API 실패, 빈 결과 대응이 정리된다
  - Vercel / Render / Neon 환경에서 공개 배포가 완료된다
  - MVP 공개에 필요한 최소 운영 문서가 존재한다

## Post-MVP Backlog
- 다중 프로젝트 통합 포트폴리오
- 다국어 지원
- 공개 링크 공유 기능
- 고급 레이아웃 커스터마이징

## Default execution rule

- 기능 요청이 구체적이지 않고 "다음 단계 진행" 류의 요청이면, **가장 앞선 미완료 단계**를 다음 작업으로 간주한다.
- 현재 기준 기본 next checkpoint는 **Render/Vercel preview deployment smoke** 이고, 다음 feature stage는 **Stage 9 — MVP hardening + public deployment** 이다.
