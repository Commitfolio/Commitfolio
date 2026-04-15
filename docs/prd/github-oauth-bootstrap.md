# GitHub OAuth Bootstrap PRD

## Metadata
- Title: GitHub OAuth bootstrap vertical slice
- Owner: Codex
- Status: In Progress
- Target milestone: MVP foundation
- Related issue:
- Related task doc: `docs/tasks/github-oauth-bootstrap.md`

## Problem
Commitfolio has architecture, playbooks, and planning templates, but no exemplar feature that proves the harness can carry one request from planning artifacts into a real implementation slice. Without an auth-first exemplar, later work on repository selection and analysis jobs will lack a validated entry point and session boundary. GitHub OAuth is the narrowest product-critical slice that exercises frontend, backend, auth policy, and verification flow together.

## User
- Primary user: Commitfolio builder validating the MVP harness
- Trigger: The builder wants the first end-to-end feature lane that unlocks signed-in product use
- Current pain: The repo has strong process scaffolding but no agreed exemplar feature contract

## Goal
- Establish one narrow vertical slice that validates the repo's default feature flow and becomes the reference feature for future delivery.
- Observable success is a user being able to start GitHub OAuth, complete the callback, and see authenticated session state through a minimal frontend + backend path.

## Non-goals
- Repository selection UI beyond a placeholder authenticated state
- Analysis job creation, SSE progress, result editing, or PDF export
- Multi-provider auth
- Production deployment hardening beyond documented risks

## Scope
### In scope
- Backend GitHub OAuth start / callback / logout / `GET /api/v1/me` endpoints
- Minimal secure session persistence for local development
- Frontend landing/auth state shell with a "Continue with GitHub" entry point
- Explicit documentation of GitHub scopes, env vars, and local verification steps

### Out of scope
- Repository list fetching UI
- Database-backed account persistence beyond the minimum needed for the bootstrap slice
- Background jobs
- OpenAI-assisted portfolio generation

## User Flow
1. Visitor opens the frontend landing page and sees a GitHub login CTA.
2. Visitor starts GitHub OAuth and is redirected through the backend callback.
3. After callback, the frontend confirms the authenticated session with `GET /api/v1/me`.
4. Visitor can log out and return to the signed-out state.

## Functional Requirements
- Frontend must expose a clear GitHub OAuth start action.
- Backend must redirect to GitHub with the minimum documented scope set.
- Backend callback must validate state, exchange the code, and establish a local authenticated session.
- `GET /api/v1/me` must return a stable authenticated payload for the signed-in user and an unauthenticated response when logged out.
- `POST /api/v1/auth/logout` must clear the local session.
- Feature docs must record local env requirements and verification commands.

## UX / UI Notes
- Entry point: frontend landing screen in `apps/frontend`
- Empty / loading / error states: show signed-out, loading-auth-check, and auth-failed states
- Editing constraints: bootstrap slice can stay visually minimal; clarity beats polish

## API / Backend Notes
- Endpoints: `GET /api/v1/auth/github/start`, `GET /api/v1/auth/github/callback`, `GET /api/v1/me`, `POST /api/v1/auth/logout`
- Auth / permissions: GitHub OAuth with minimal read-only identity scope and secure local session handling
- Background processing: none for this slice
- SSE / polling behavior: none for this slice
- Local env:
  - Backend: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_CALLBACK_URL`, `GITHUB_SCOPE`, `FRONTEND_APP_URL`, `BACKEND_CORS_ORIGIN`, `SESSION_SECRET`
  - Frontend: `VITE_API_BASE_URL`
- Bootstrap decision: use signed cookie session storage first, defer PostgreSQL-backed account persistence to a later feature

## Data / Domain Notes
- Tables or entities touched: `User`, `ConnectedGitHubAccount` (or a documented temporary bootstrap equivalent)
- External APIs touched: GitHub OAuth authorize + token exchange + current user API
- Stored artifacts: local session state, documented env vars, optional bootstrap persistence notes

## Acceptance Criteria
- [ ] Planning artifacts exist for the same slug across `docs/` and `.omx/plans/`
- [ ] Signed-out frontend state renders a GitHub login CTA
- [ ] OAuth callback establishes a local authenticated session and `GET /api/v1/me` reflects that state
- [ ] Logout clears the session and returns the UI to signed-out state
- [ ] Feature docs capture required env vars, GitHub scopes, and verification evidence

## Verification Plan
- Unit: backend auth service/state validation tests; frontend auth-state rendering tests; see `docs/playbooks/verification-baseline.md`
- Integration: local OAuth route flow with mocked GitHub exchange and authenticated `GET /api/v1/me`
- Manual: complete the local login/logout path and record the success/failure-state observations

## Risks
- OAuth callback handling is security-sensitive and easy to over-scope.
- Local session strategy may change once persistence and deployment choices are finalized.
- GitHub app setup can block implementation if callback URLs and env vars are not documented precisely.

## Open Questions
- Which session mechanism will the repo standardize on for the frontend/backend boundary?

## Approval
- Requested by: project owner
- Approved by:
- Approved at:
