# PRD: Stitch 디자인 시스템 기반 프론트 UI 구현

## Metadata
- Title: Stitch 디자인 시스템 기반 프론트 UI 구현
- Owner: Codex
- Status: Done
- Target milestone: Public MVP UI polish
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/32
- Related task doc: `docs/tasks/stitch-frontend-ui.md`

## Problem
Stitch MCP의 `Commitfolio MVP` 디자인은 Commitfolio를 단순 SaaS 폼이 아니라 개발자의 작업 증거를 큐레이션하는 고급 포트폴리오 문서 경험으로 정의한다. 현재 프론트엔드는 GitHub Primer 톤으로 기능 흐름은 명확하지만, Stitch가 제시한 editorial surface, no-line sectioning, tonal depth, commit stream 감성이 반영되어 있지 않다. MVP의 첫인상이 “저장소 분석 도구”에서 “근거 기반 포트폴리오 갤러리”로 이어지려면 기존 기능은 유지하되 시각 언어를 Stitch 기준에 맞춰 재정렬해야 한다.

## User
- Primary user: 자신의 GitHub 저장소 활동을 포트폴리오 문서로 만들려는 개발자
- Trigger: GitHub 로그인 후 저장소를 선택하고 분석 결과를 확인·편집하려는 순간
- Current pain: 기능은 동작하지만 포트폴리오 산출물의 프리미엄/문서형 인상이 약하다.

## Goal
- Stitch 디자인 시스템의 색상, 타이포그래피, tonal surface, no-line rule을 프론트에 반영한다.
- 저장소 선택, 분석 진행, 결과 문서가 하나의 “Curated Architect” 경험처럼 보이게 한다.
- 기존 GitHub OAuth → 저장소 선택 → 분석 실행 → 결과 생성/편집/PDF 흐름과 한국어 UI 문구를 유지한다.

## Non-goals
- Stitch HTML을 그대로 복사하거나 Tailwind dependency를 추가하지 않는다.
- 백엔드 API, OAuth scope, DB, 배포 설정은 변경하지 않는다.
- 라우터/상태관리 라이브러리 등 신규 dependency는 추가하지 않는다.
- 실제 이미지/아이콘 asset을 새로 추가하지 않는다.

## Scope
### In scope
- `apps/frontend/src/app/App.tsx`의 앱 shell/hero/preview markup 보강
- `apps/frontend/src/styles.css`의 디자인 토큰, panel/card/button/badge/input/result 스타일 전면 정렬
- 기존 component class를 활용한 저장소 카드, 분석 진행, result document polish
- 기존 App 테스트가 의존하는 critical text 유지

### Out of scope
- Backend/API 변경
- OpenAI 생성 품질 로직 변경
- PDF 엔진 변경
- visual snapshot tooling 추가

## User Flow
1. 사용자는 첫 화면에서 Commitfolio가 GitHub 활동을 포트폴리오 문서로 바꾸는 제품임을 이해한다.
2. 로그인 후 접근 가능한 저장소를 card형 리스트에서 선택한다.
3. 분석 작업 진행 상태와 evidence stream을 tonal depth가 있는 패널에서 확인한다.
4. 생성된 포트폴리오 결과를 editorial document layout으로 읽고 직접 수정하거나 PDF로 저장한다.

## Functional Requirements
- 기존 세션 로딩/로그인/로그아웃 상태가 그대로 표시되어야 한다.
- 저장소 목록, 직접 검색, 공개 범위 필터, 더 불러오기 동작이 유지되어야 한다.
- 분석 작업 생성/실행/새로고침/결과 생성 버튼과 상태 메시지가 유지되어야 한다.
- 결과 목록, 결과 문서, 직접 수정, PDF 저장 동작이 유지되어야 한다.
- 테스트가 찾는 기존 사용자-visible 문구와 접근성 label은 제거하지 않는다.

## UX / UI Notes
- Entry point: glass-like topbar와 editorial hero로 제품 정체성을 보여준다.
- Empty / loading / error states: 기존 문구를 유지하되 notice와 empty state를 tonal surface로 정리한다.
- Editing constraints: ResultEditor는 기존 form 동작을 유지하고 input focus는 Stitch ghost border 규칙을 따른다.
- Design reference: Stitch project `13874972523934894510` / screens `Landing Page`, `Repository Selection`, `Analysis Progress`, `Portfolio Editor`.
- Design principles: hard divider 최소화, `surface` 계열 tonal layering, primary indigo gradient CTA, ambient shadow on hover, commit stream motif.

## API / Backend Notes
- Endpoints: 변경 없음
- Auth / permissions: 변경 없음
- Background processing: 변경 없음
- SSE / polling behavior: 변경 없음

## Data / Domain Notes
- Tables or entities touched: 없음
- External APIs touched: Stitch MCP는 디자인 조회 용도로만 사용
- Stored artifacts: 없음

## Acceptance Criteria
- [x] 첫 화면이 Stitch의 “Curated Architect”/editorial portfolio 방향을 따른다.
- [x] repository card, progress panel, result document가 Stitch surface hierarchy를 사용한다.
- [x] 기존 기능 흐름과 한국어 문구가 유지된다.
- [x] 신규 package dependency가 없다.
- [x] frontend lint/typecheck/test/build와 `git diff --check`가 통과한다.

## Verification Plan
- Unit: `npm --prefix apps/frontend run test -- --run`
- Integration/static: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run build`
- Manual: Stitch HTML/screen summary와 주요 UI class 적용점을 대조하고 기존 critical path 문구가 남아 있는지 확인한다.

## Risks
- CSS 변경 폭이 커져 일부 responsive spacing이 실제 브라우저에서 추가 조정될 수 있다.
- 외부 web font를 불러오지 않으므로 Manrope/Inter가 설치되지 않은 환경에서는 system fallback으로 표시된다.

## Open Questions
- 없음. 이번 iteration은 Stitch 디자인 방향을 기존 MVP 단일 화면에 적용하는 범위로 제한한다.

## Approval
- Requested by: User
- Approved by: User request
- Approved at: 2026-04-17
