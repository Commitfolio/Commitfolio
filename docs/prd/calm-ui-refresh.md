# PRD: 차분한 UI와 명확한 액션 계층을 위한 프런트 refresh

## Metadata
- Title: 차분한 UI와 명확한 액션 계층을 위한 프런트 refresh
- Owner: Codex
- Status: Done
- Target milestone: Public MVP UI polish
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/42
- Related task doc: `docs/tasks/calm-ui-refresh.md`

## Problem
현재 배포된 Commitfolio 프런트는 기능 흐름은 갖춰져 있지만, 첫 화면의 타이포 스케일이 과도하고 패널 간 역할 차이가 약해 사용자가 한 번에 읽기 어렵다. 특히 signed-out 진입 상태에서 핵심 CTA가 명확하게 떠오르지 않고, signed-in 이후에도 “지금 무엇을 눌러야 하는지”가 버튼 계층만으로 잘 드러나지 않는다. 추가로 환경/운영용 안내 문구가 메인 제품 흐름과 섞여 있어 프로덕트 신뢰감을 떨어뜨린다.

## User
- Primary user: GitHub 저장소 활동을 포트폴리오 초안으로 만들고 싶은 개발자
- Trigger: 배포된 첫 화면을 보고 로그인/저장소 선택/분석 실행으로 진입하려는 순간
- Current pain: 글자 크기와 카드 밀도가 뒤섞여 있고, 버튼 우선순위가 모호해 다음 행동 판단에 불필요한 인지 비용이 든다.

## Goal
- landing부터 result까지 차분하고 안정적인 visual hierarchy를 만든다.
- signed-out / signed-in / analysis / result 각 상태에서 primary action이 한눈에 보이게 한다.
- 운영/디버그성 문구를 일반 사용자 화면에서 분리해 제품 경험을 더 깔끔하게 만든다.

## Non-goals
- 새로운 기능 플로우 추가
- backend API, OAuth scope, DB, deployment infra 수정
- 라우터 도입이나 상태관리 재설계
- 새 이미지/아이콘 asset 추가

## Scope
### In scope
- `apps/frontend/src/app/App.tsx`의 hero, workflow, info shell hierarchy 조정
- `apps/frontend/src/features/github-auth/SessionPanel.tsx`의 signed-out/signed-in action emphasis 개선
- `apps/frontend/src/features/analysis-job/AnalysisJobPanel.tsx`의 action group과 상태 요약 hierarchy 개선
- `apps/frontend/src/features/result-viewer/ResultExportActions.tsx`, `RecentResults.tsx`, `ResultEditor.tsx`, `ResultDocument.tsx`의 action/readability polish
- `apps/frontend/src/styles.css`의 token/button/panel/type scale/layout 정리
- production 사용자에게 불필요한 환경 안내 block 비노출 처리

### Out of scope
- backend endpoint 변경
- OAuth callback/env 문서 개편
- PDF 엔진/print pipeline 변경
- multi-route 정보구조 개편

## User Flow
1. 사용자는 첫 화면에서 Commitfolio가 무엇을 해주는지 과장 없이 빠르게 이해한다.
2. signed-out 상태에서는 GitHub 연결이 가장 중요한 다음 행동으로 보인다.
3. signed-in 후에는 저장소 선택, 분석 실행, 결과 생성이 순서대로 드러난다.
4. 결과 문서와 편집/내보내기 액션은 서로 경쟁하지 않고 읽기와 수정 역할이 분리된다.

## Functional Requirements
- 기존 GitHub OAuth 로그인/로그아웃 동작은 유지되어야 한다.
- repository list/lookup/load-more/select 흐름은 유지되어야 한다.
- analysis job create/run/refresh/result generation 흐름은 유지되어야 한다.
- result load/regenerate/save/print 동작은 유지되어야 한다.
- 기존 critical-path test가 찾는 주요 버튼/문구(`GitHub로 계속하기`, `저장소 더 불러오기`, `포트폴리오 결과 생성`)는 유지한다.
- production UI에서 환경 디버그 문구는 상시 노출하지 않는다.

## UX / UI Notes
- Entry point: 과도한 hero scale을 줄이고, 제품 설명과 바로 이어지는 CTA/support zone을 만든다.
- Empty / loading / error states: notice는 유지하되 각 패널 안에서 시선 분산이 적게 보이도록 정렬한다.
- Editing constraints: calm neutral base + restrained blue accent. 버튼은 역할별로 색/테두리/배경이 구분되어야 한다.
- Reference contract: `DESIGN.md`

## API / Backend Notes
- Endpoints: 변경 없음
- Auth / permissions: 변경 없음
- Background processing: 변경 없음
- SSE / polling behavior: 변경 없음

## Data / Domain Notes
- Tables or entities touched: 없음
- External APIs touched: 없음
- Stored artifacts: 없음

## Acceptance Criteria
- [ ] first viewport에서 headline, 설명, 핵심 CTA, preview panel hierarchy가 현재보다 차분하게 정리된다.
- [ ] 주요 버튼 역할이 primary/secondary/utility 수준으로 구분된다.
- [ ] signed-out, repository selection, analysis, result 패널 모두에서 읽기 밀도가 줄어든다.
- [ ] production 사용자를 위한 화면에서 환경/디버그 안내가 상시 노출되지 않는다.
- [ ] frontend lint/typecheck/test/build와 `git diff --check`가 통과한다.

## Verification Plan
- Unit: `npm --prefix apps/frontend run test -- --run`
- Integration: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run build`, `git diff --check`
- Manual: deployed UI screenshot 확인, local screenshot 확인, signed-out CTA hierarchy와 signed-in action hierarchy 수동 검토

## Risks
- CSS 변경 폭이 넓어 일부 패널 spacing이 mobile에서 추가 조정이 필요할 수 있다.
- production deploy는 release branch/merge 여부에 따라 이 turn 안에 완결되지 않을 수 있다.

## Open Questions
- release PR를 즉시 main까지 머지할지, develop PR까지만 준비할지는 원격 상태와 권한에 따라 결정된다.

## Approval
- Requested by: User
- Approved by: User request
- Approved at: 2026-06-23
