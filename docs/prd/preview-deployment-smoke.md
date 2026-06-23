# PRD: Render/Vercel preview deployment smoke 준비

## Metadata
- Title: Render/Vercel preview deployment smoke 준비
- Owner: Codex
- Status: Done
- Target milestone: Public MVP / Preview deployment checkpoint
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/34
- Related task doc: `docs/tasks/preview-deployment-smoke.md`

## Problem
Stage 8까지 핵심 기능은 로컬 기준으로 완성됐지만, Stage 9를 공개 배포 hardening으로 만들려면 그 전에 Render backend와 Vercel frontend가 서로 연결되는지 preview 수준으로 검증해야 한다. 현재 로컬 기본값은 `localhost`와 `SameSite=Lax` 세션 쿠키에 맞춰져 있어, Vercel/Render처럼 서로 다른 도메인에 배포하면 CORS와 session cookie 동작이 실패할 수 있다. 외부 콘솔 생성과 secret 입력은 사용자 권한이 필요하므로, 저장소에는 필요한 env와 자동 smoke 검증 도구를 먼저 준비해야 한다.

## User
- Primary user: Commitfolio preview 배포를 준비하는 운영자
- Trigger: Stage 8 이후 Render/Vercel preview URL을 만들고 OAuth login smoke를 검증하려는 순간
- Current pain: 어떤 env를 바꿔야 하는지, frontend가 Render backend를 바라보는지, OAuth callback/CORS/session이 맞는지 수동으로 확인해야 한다.

## Goal
- split-domain preview 배포에서 필요한 backend session cookie 설정을 env로 제어한다.
- Render backend, Vercel frontend, GitHub OAuth callback, CORS 정합성을 검증할 수 있는 smoke script를 제공한다.
- 외부 콘솔에서 사용자가 해야 하는 작업과 Codex가 검증할 작업을 문서화한다.

## Non-goals
- Codex가 Render/Vercel/Neon/GitHub OAuth 콘솔 리소스를 직접 생성하지 않는다.
- production custom domain, billing, main release는 이번 범위에서 제외한다.
- server-side PDF나 새로운 배포 플랫폼을 추가하지 않는다.
- secret 값을 git에 저장하지 않는다.

## Scope
### In scope
- Backend session cookie `SameSite`/`Secure` env 설정 추가
- `.env.example` preview/prod cookie guidance 추가
- preview deployment smoke Python script 추가
- operator deployment playbook에 script 사용법과 env 이름 반영
- local backend/frontend URL 기준 smoke 실행

### Out of scope
- 실제 Render/Vercel project 생성
- GitHub OAuth App callback 실 변경
- Neon production DB migration 실행
- develop → main release PR

## User Flow
1. 사용자가 Render backend와 Vercel frontend preview project를 만든다.
2. 사용자가 Render env에 backend/GitHub/DB/session 값을 넣고, Vercel env에 `VITE_API_BASE_URL`을 넣는다.
3. 사용자가 GitHub OAuth App callback URL을 Render backend callback으로 설정한다.
4. Codex가 `scripts/deployment/preview_smoke.py`로 backend `/healthz`, OAuth redirect, frontend HTML, CORS, frontend API base bundle 단서를 확인한다.
5. 실패하면 script output을 근거로 env/callback/CORS/cookie 설정을 수정한다.

## Functional Requirements
- Backend는 기본 local 개발에서는 `SameSite=Lax`, `Secure=false`를 유지해야 한다.
- Preview/prod에서는 env로 `SESSION_COOKIE_SAME_SITE=none`, `SESSION_COOKIE_SECURE=true`를 설정할 수 있어야 한다.
- Smoke script는 외부 dependency 없이 실행되어야 한다.
- Smoke script는 backend URL만으로 `/healthz`와 OAuth start redirect를 검증해야 한다.
- Smoke script는 frontend URL이 있으면 frontend HTML과 CORS preflight를 검증해야 한다.
- Smoke script는 expected frontend API base가 주어지면 production bundle에서 해당 URL을 찾고 localhost backend reference 잔존 여부를 확인해야 한다.

## UX / UI Notes
- UI 변경 없음.
- 배포 실패 시 운영자가 copy/paste하기 쉬운 command와 실패 사유를 출력한다.

## API / Backend Notes
- Endpoints: 새 endpoint 없음
- Auth / permissions: OAuth flow 자체는 유지, session cookie attributes만 env 제어
- Background processing: 없음
- SSE / polling behavior: 이번 script는 SSE deep smoke까지는 하지 않고 CORS/API base readiness에 집중한다.

## Data / Domain Notes
- Tables or entities touched: 없음
- External APIs touched: smoke 시 GitHub OAuth authorize redirect URL만 검사한다. GitHub token exchange는 사용자가 실제 OAuth login smoke를 수행할 때 검증한다.
- Stored artifacts: 없음

## Acceptance Criteria
- [x] `.env.example`이 preview/prod session cookie env를 문서화한다.
- [x] backend session middleware가 env 기반 `SameSite`/`Secure` 설정을 사용한다.
- [x] cookie 설정 회귀 테스트가 존재한다.
- [x] preview smoke script가 local backend/frontend URL에서 통과한다.
- [x] operator playbook에 script 사용법과 사용자 액션이 반영된다.
- [x] backend tests와 frontend baseline verification이 통과한다.

## Verification Plan
- Unit: `cd apps/backend && .venv/bin/python -m pytest tests/test_auth.py::test_session_cookie_settings_are_env_configurable_for_split_domain_preview`
- Integration: `scripts/deployment/preview_smoke.py --backend-url http://localhost:8000 --frontend-url http://localhost:5173`
- Regression: `npm --prefix apps/frontend run lint`, `npm --prefix apps/frontend run typecheck`, `npm --prefix apps/frontend run test -- --run`, `npm --prefix apps/frontend run build`, `cd apps/backend && .venv/bin/python -m pytest tests`, `git diff --check`
- Manual: Render/Vercel/GitHub OAuth preview URLs가 준비되면 같은 script를 외부 URL로 재실행한다.

## Risks
- 실제 preview OAuth callback은 GitHub OAuth App 콘솔과 Render env가 일치해야 하므로 사용자 액션 없이는 완료할 수 없다.
- Browser privacy 정책이나 preview platform domain 정책에 따라 cookie behavior는 실제 브라우저 smoke가 추가로 필요하다.
- `SameSite=None; Secure`는 HTTPS preview/prod 전용이며 localhost HTTP 개발에는 맞지 않는다.

## Open Questions
- Stage 9에서 production migration을 Render deploy lifecycle에 넣을지, 별도 one-off command로 유지할지 결정해야 한다.
- Stage 9에서 backend/frontend same-site custom domain을 쓸지, split-domain cookie 설정으로 공개 MVP를 갈지 결정해야 한다.

## Approval
- Requested by: User
- Approved by: User request
- Approved at: 2026-04-17
