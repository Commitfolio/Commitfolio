# PRD: 한국어 UI와 예외 처리/로깅 체계 정리

## Metadata
- Title: 한국어 UI와 예외 처리/로깅 체계 정리
- Owner: Codex
- Status: Done
- Target milestone: Public MVP hardening pre-check
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/22
- Related task doc: `docs/tasks/error-handling-and-korean-ui.md`

## Problem
로컬 메인 페이지가 `?auth_error=backend_not_configured` 같은 내부 코드를 그대로 사용자에게 보여주고, 화면 문구가 영어 중심이라 현재 MVP 사용자가 흐름을 이해하기 어렵다. 요청/응답 로그는 uvicorn 기본 access log에 의존하고 있어, 앱 레벨에서 어떤 request id로 어떤 예외가 발생했는지 추적하기 어렵다. 기능이 늘어나기 전에 예외 처리와 로깅 규칙을 문서화하고, 한국어 기본 UI와 가독성 있는 화면 톤을 맞춰야 한다.

## User
- Primary user: Commitfolio 로컬/preview 사용자를 포함한 MVP 사용자와 개발자
- Trigger: 로그인, 저장소 조회, 분석 실행, 결과 생성 중 오류가 발생할 때
- Current pain: 내부 에러 코드/영어 문구/낮은 대비 때문에 다음 행동을 알기 어렵고 로그 추적 기준이 약하다

## Goal
- 사용자-facing UI 기본 언어를 한국어로 정리한다.
- OAuth/API 에러를 한국어 안내와 다음 액션으로 보여준다.
- backend request/response/exception 로그를 앱 레벨에서 남긴다.
- 예상하지 못한 backend 예외도 공통 JSON envelope로 반환한다.
- 메인 화면 가독성과 대비를 개선한다.

## Non-goals
- 다국어 전환 시스템
- 외부 로그 수집 서비스 연동
- Sentry/Datadog 같은 vendor 도입
- 인증/권한 정책 자체 변경
- GitHub OAuth credential 발급 자동화

## Exception / Logging Policy

### Backend request logging
- 모든 HTTP 요청에 `request_id`를 부여한다.
- 요청 시작/종료 로그에는 method, path, status_code, duration_ms, request_id를 남긴다.
- 예상하지 못한 예외는 stack trace와 request_id를 error log로 남긴다.
- response header에 `X-Request-ID`를 넣어 frontend/사용자 보고와 backend log를 연결할 수 있게 한다.

### Backend error envelope
- 기존 error envelope는 유지한다.
- 예상 가능한 business error는 기존 `build_error_response(status, code, message)`를 사용한다.
- 예상하지 못한 예외는 `internal_server_error` code와 한국어 일반 메시지를 반환한다.
- secret, token, raw stack trace는 response에 넣지 않는다.

### Frontend error mapping
- URL의 `auth_error` code와 API error code는 한국어 사용자 메시지로 변환한다.
- 알 수 없는 오류는 “잠시 후 다시 시도”와 “서버 로그 확인”을 안내한다.
- 개발자가 확인해야 하는 값은 화면에 내부 코드 대신 `요청 ID`/일반 안내 중심으로 보여준다.

## Scope
### In scope
- backend logging middleware
- backend global exception handler
- frontend auth/API error Korean mapping
- frontend major copy Korean translation
- main page readability/color contrast polish
- docs/task/test updates

### Out of scope
- external observability SaaS
- production cookie/CORS hardening
- GitHub OAuth credential provisioning
- full visual redesign

## User Flow
1. 사용자가 `/`에 접속한다.
2. GitHub OAuth 미설정이면 한국어 안내로 “백엔드 환경변수가 필요함”을 본다.
3. 사용자가 로그인/저장소/분석 요청을 수행한다.
4. 요청 실패 시 한국어 오류와 복구 안내를 본다.
5. 개발자는 backend log의 request_id로 실패 원인을 추적한다.

## Functional Requirements
- backend는 request id 기반 request log를 출력한다.
- backend는 예상치 못한 예외를 공통 JSON으로 반환한다.
- frontend는 `backend_not_configured`를 한국어 설정 안내로 표시한다.
- frontend 주요 화면 문구는 한국어다.
- frontend API error fallback 메시지는 한국어다.
- 메인 card/panel/텍스트 대비가 이전보다 선명해야 한다.

## UX / UI Notes
- Entry point: root `App.tsx`
- Empty / loading / error states: 한국어로 표시
- Editing constraints: code identifier/API/env 이름은 영어 그대로 허용

## API / Backend Notes
- Endpoints: 기존 API 유지
- Auth / permissions: 변경 없음
- Background processing: 없음
- SSE / polling behavior: 기존 흐름 유지

## Data / Domain Notes
- Tables or entities touched: 없음
- External APIs touched: 없음
- Stored artifacts: 없음

## Acceptance Criteria
- [ ] `auth_error=backend_not_configured`가 한국어 안내로 표시된다.
- [ ] backend request log에 method/path/status/duration/request_id가 남는다.
- [ ] backend unexpected exception response가 `{ error: { code, message } }` 형태다.
- [ ] 주요 UI 문구가 한국어로 바뀐다.
- [ ] 메인 화면 대비/가독성이 개선된다.
- [ ] frontend/backend tests와 build가 통과한다.

## Verification Plan
- Unit: frontend auth error mapping/API error mapping test
- Integration: backend request middleware/exception handler test
- Manual: `http://localhost:5173/?auth_error=backend_not_configured` 확인
- Manual: backend log에서 request id 확인

## Risks
- 모든 영어 technical term을 억지로 번역하면 개발자 가독성이 떨어질 수 있다.
- logging middleware가 streaming response를 방해하면 안 된다.
- 너무 많은 로그는 local dev noise가 될 수 있다.

## Open Questions
- Stage 9에서 production log level과 external observability를 별도 도입할지 결정한다.
