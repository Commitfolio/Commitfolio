# PRD: PDF 내보내기

## Metadata
- Title: PDF 내보내기
- Owner: Codex
- Status: In Progress
- Target milestone: Public MVP Stage 8
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/20
- Related task doc: `docs/tasks/pdf-export.md`

## Problem
Commitfolio는 포트폴리오 결과를 생성, 조회, 편집, 재생성할 수 있지만 아직 제출 가능한 파일 형태로 저장하는 흐름이 없다. 사용자는 결과 화면을 그대로 포트폴리오/지원 자료로 보관하거나 공유하기 위해 PDF 저장 경로가 필요하다. 서버-side PDF 렌더링은 dependency와 배포 리스크가 크므로 MVP에서는 브라우저 print/save-as-PDF fallback으로 먼저 닫는다.

## User
- Primary user: GitHub repository 활동을 포트폴리오 문서로 저장하려는 Commitfolio 사용자
- Trigger: 생성/편집한 결과를 파일로 저장하고 싶을 때
- Current pain: 결과 화면을 복사하거나 스크린샷으로 보관해야 한다

## Goal
- 결과 detail 화면에서 PDF 저장/출력 액션을 제공한다.
- 브라우저 print dialog를 통해 Save as PDF가 가능하다.
- 출력용 CSS에서 포트폴리오 문서만 읽기 좋게 남긴다.
- 기존 결과 조회/편집/재생성 흐름을 깨지 않는다.

## Non-goals
- 서버-side PDF binary 생성
- PDF layout 고급 편집기
- PDF 파일 서버 저장
- 이메일/공유 링크 전송
- 신규 PDF dependency 추가

## Scope
### In scope
- 결과가 있을 때 PDF 저장/출력 버튼 표시
- 브라우저 `window.print()` 기반 export trigger
- 사용자 안내 문구
- print media CSS 정리
- frontend test 보강
- roadmap/task 문서 갱신

### Out of scope
- `GET /api/v1/results/{result_id}/download.pdf` 실제 PDF binary endpoint
- 서버 렌더링/Playwright/wkhtmltopdf 연동
- 배포 환경 PDF rendering worker

## User Flow
1. 사용자가 분석 결과를 생성하거나 최근 결과를 연다.
2. 결과 문서 상단 액션에서 `PDF로 저장/출력`을 누른다.
3. 브라우저 print dialog에서 `Save as PDF`를 선택한다.
4. 출력물에는 결과 문서와 근거 링크가 중심으로 표시된다.

## Functional Requirements
- 결과가 없는 상태에서는 PDF 액션을 표시하지 않는다.
- 결과가 있는 상태에서는 PDF 저장/출력 버튼과 짧은 안내 문구를 표시한다.
- 버튼 클릭 시 `window.print()`를 호출한다.
- print media에서 auth/repo/analysis/editor/action UI는 숨기고 결과 문서를 출력한다.
- evidence link 텍스트와 URL은 출력물에서 읽을 수 있어야 한다.

## UX / UI Notes
- Entry point: result panel actions
- Empty / loading / error states: 결과가 없으면 기존 empty state 유지
- Editing constraints: 편집 UI는 출력하지 않고 저장된 결과 문서만 출력한다

## API / Backend Notes
- Endpoints: 없음. MVP Stage 8은 browser print fallback으로 구현한다.
- Auth / permissions: 기존 result 조회 권한을 그대로 사용한다.
- Background processing: 없음
- SSE / polling behavior: 없음

## Data / Domain Notes
- Tables or entities touched: 없음
- External APIs touched: 없음
- Stored artifacts: 없음

## Acceptance Criteria
- [ ] 결과 생성 후 PDF 저장/출력 버튼이 보인다.
- [ ] 버튼 클릭 시 `window.print()`가 호출된다.
- [ ] print media에서 결과 문서 중심으로 출력 레이아웃이 정리된다.
- [ ] 기존 edit/save/regenerate 흐름이 유지된다.
- [ ] 관련 frontend tests와 build/lint/typecheck가 통과한다.

## Verification Plan
- Unit: frontend test에서 print button과 `window.print()` 호출 확인
- Integration: 기존 result generation/edit/regenerate test 유지
- Manual: 브라우저에서 결과 생성 후 print preview에서 문서 영역만 보이는지 확인

## Risks
- 브라우저별 print dialog/Save as PDF UX가 다를 수 있다.
- URL 출력 방식은 브라우저/프린터 설정에 따라 다르게 보일 수 있다.
- 실제 PDF binary download가 필요한 경우 후속 서버-side PDF 전략이 필요하다.

## Open Questions
- Stage 9 전에 server-side PDF endpoint가 꼭 필요한지, browser fallback으로 공개 MVP를 충분히 닫을 수 있는지 확인한다.

## Approval
- Requested by: User roadmap continuation
- Approved by: Default feature flow auto-continue
- Approved at: 2026-04-16
