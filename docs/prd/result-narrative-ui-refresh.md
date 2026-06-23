# PRD: 결과 서술 고도화와 UI 전면 재정리

## Metadata
- Title: 결과 서술 고도화와 UI 전면 재정리
- Owner: Codex
- Status: In Progress
- Target milestone: Public MVP hardening
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/45
- Related task doc: `docs/tasks/result-narrative-ui-refresh.md`

## Problem
현재 Commitfolio는 핵심 플로우는 동작하지만 결과물이 포트폴리오 문서로 읽히지 않는다. rule-based 결과는 commit/PR title을 거의 그대로 나열하고, 핵심 기여를 "근거를 남겼습니다" 수준으로만 표현해 사용자가 실제로 어떤 기능을 만들고 어떤 기술 판단을 했는지 전달하지 못한다. 동시에 배포 UI는 일부 preview URL에서 예전 디자인이 남아 있고, 결과 화면도 raw evidence 나열에 비해 서술 구조가 약하다.

## User
- Primary user: GitHub 활동을 바탕으로 실제 포트폴리오 설명을 만들고 싶은 개발자
- Trigger: 분석 후 결과 화면을 열었는데 커밋 로그 요약 이상을 얻지 못하는 순간
- Current pain: 어떤 기능을 만들었고 어떤 기술을 사용했는지가 문장형으로 드러나지 않아 포트폴리오 초안으로 바로 쓰기 어렵다.

## Goal
- OpenAI key 없이도 rule-based 결과가 "기능 + 기술 + 맥락"을 담은 포트폴리오 문장으로 읽히게 만든다.
- repo evidence에서 feature cluster를 추론해 더 구체적인 핵심 기여, 역할, 기술 스택을 생성한다.
- 결과 화면 UI를 raw evidence보다 narrative가 먼저 보이도록 재정렬한다.
- 최신 UI와 결과 로직이 develop/main 배포에 실제 반영되게 한다.

## Non-goals
- 다중 repository 통합 포트폴리오
- 완전한 자연어 생성 품질을 LLM 수준으로 끌어올리기
- 백엔드 권한 모델/OAuth scope 자체 변경
- 새로운 route 구조 도입

## Scope
### In scope
- `apps/backend/app/services/results.py`의 deterministic draft generation 전면 개선
- evidence 기반 feature/theme clustering, tech stack inference, role summary 강화
- 결과 문서 headline/summary/section ordering 및 evidence presentation 보강
- landing/result UI polish 보강 및 preview/main 재배포
- 관련 테스트/문서 업데이트

### Out of scope
- GitHub evidence 수집 source type 추가
- PDF 엔진 교체
- OpenAI enhancer prompt 대수술
- account/session storage 구조 개편

## User Flow
1. 사용자가 repo 분석을 실행한다.
2. 결과 생성 시 raw evidence를 기반으로 기능군/기술군/기여 맥락이 추론된다.
3. 결과 화면에서 핵심 기여가 commit 제목 나열이 아니라 기능 단위 문장으로 먼저 보인다.
4. 필요하면 사용자가 텍스트를 다듬고 PDF 저장으로 이어간다.

## Functional Requirements
- rule-based 결과는 핵심 기여에서 최소 3개 이상 구체적 기능/구현 문장을 생성해야 한다.
- role summary는 일반론 대신 저장소 evidence 유형과 변경 범위 기반으로 더 구체화되어야 한다.
- tech stack은 파일 확장자 나열보다 framework/language/domain 추론을 우선해야 한다.
- evidence links는 narrative를 보조하는 위치에 남아야 하며 제거하지 않는다.
- UI는 결과 narrative를 first-class로 보여주고, raw evidence는 secondary surface로 내려야 한다.
- preview/main 배포 후 최신 UI와 결과 생성 로직이 실제 URL에서 확인 가능해야 한다.

## UX / UI Notes
- Entry point: `apps/frontend/src/app/App.tsx`, `apps/frontend/src/features/result-viewer/ResultDocument.tsx`
- Empty / loading / error states: 결과 생성 실패/세션 오류는 한국어로 명확하게 안내하고, loading은 stuck처럼 보이지 않게 한다.
- Editing constraints: result view는 "문서 읽기" 경험을 우선하고, evidence chip/list는 보조 표식으로 남긴다.
- Reference contract: `DESIGN.md`

## API / Backend Notes
- Endpoints: 결과 생성/read/update/regenerate endpoint 자체는 유지
- Auth / permissions: 변경 없음
- Background processing: 변경 없음
- SSE / polling behavior: 변경 없음

## Data / Domain Notes
- Tables or entities touched: `PortfolioResult` 생성 내용, evidence link selection 기준
- External APIs touched: 없음
- Stored artifacts: 없음

## Acceptance Criteria
- [ ] OpenAI key 없이 생성한 결과가 commit title 나열보다 구체적인 기능/기술 중심 서술을 제공한다.
- [ ] tech stack이 Markdown/YAML 같은 저가치 출력에 머물지 않고 repo 맥락에 맞는 기술명을 우선한다.
- [ ] 결과 화면에서 narrative hierarchy가 evidence chip/list보다 먼저 읽힌다.
- [ ] preview/main 배포 URL에서 최신 UI가 반영된다.
- [ ] frontend/backend 검증이 통과한다.

## Verification Plan
- Unit: backend result generation tests, frontend result rendering tests
- Integration: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `cd apps/backend && .venv/bin/python -m pytest tests`, `git diff --check`
- Manual: target repo로 분석 실행 후 핵심 기여/기술 스택/역할 요약이 실제 포트폴리오 초안처럼 읽히는지 확인, preview/main 배포 DOM 확인

## Risks
- deterministic heuristic이 특정 repo에 과적합될 수 있다.
- preview URL 세션 문제와 결과 서술 문제를 한 번에 다루는 만큼 verification 범위가 넓다.

## Open Questions
- feature clustering을 PR title 중심으로 할지 commit title + changed file path 조합 중심으로 할지 구현 중 최적화가 필요하다.

## Approval
- Requested by: User
- Approved by: User request
- Approved at: 2026-06-23
