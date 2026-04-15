# Repository Selector PRD

## Metadata
- Title: Repository access and selection
- Owner: Codex
- Status: In Progress
- Target milestone: Public MVP / Stage 1
- Related issue: #1
- Related task doc: `docs/tasks/repository-selector.md`

## Problem
Commitfolio can create a GitHub OAuth session, but the user cannot yet choose which repository should become the input for portfolio generation. Every downstream MVP step depends on a stable single-repository selection boundary. Without this slice, analysis jobs, evidence ingestion, progress tracking, and result generation have no concrete target.

## User
- Primary user: A signed-in Commitfolio user with access to one or more GitHub repositories.
- Trigger: After GitHub OAuth login, the user wants to select one project to analyze.
- Current pain: The app confirms login but does not show accessible repositories or explain what repository data will be read.

## Goal
- A signed-in user can see GitHub repositories available to the OAuth token and select exactly one repository as the next-stage analysis target.
- The API returns enough repository metadata for the frontend to distinguish public/private and user/org-owned repositories.
- The UI clearly explains the Stage 1 data-access boundary before analysis begins.

## Non-goals
- Creating analysis jobs.
- Persisting repository snapshots to PostgreSQL.
- Collecting commits, PRs, issues, reviews, or changed files.
- Multi-repository selection.
- Adding a new UI dependency or full shadcn/Tailwind setup in this slice.

## Scope
### In scope
- `GET /api/v1/repositories` backend endpoint.
- GitHub `/user/repos` API integration using the active OAuth session token.
- Visibility filter support for `all`, `public`, and `private`.
- Minimal pagination cursor support.
- Frontend loading/empty/error states for the repository list.
- Frontend single repository selection state.
- Permission/data-access copy for repository metadata.
- Tests for backend endpoint behavior and frontend repository selector behavior.

### Out of scope
- Database persistence.
- Analysis job APIs.
- SSE.
- PDF/result workflows.
- Fine-grained GitHub App migration.

## User Flow
1. User signs in with GitHub.
2. App loads the current session via `GET /api/v1/me`.
3. App loads repositories via `GET /api/v1/repositories?visibility=all`.
4. User reviews repository metadata and selects one repository.
5. App shows the selected repository as ready for the next Stage 2 analysis job flow.

## Functional Requirements
- The backend must reject unauthenticated repository list requests with the existing error envelope shape.
- The backend must use a server-side session token lookup instead of exposing the GitHub access token to the frontend.
- The backend must map GitHub repository payloads to stable response fields: `id`, `full_name`, `private`, `owner_type`, `default_branch`, `permissions`, `html_url`, `description`, `updated_at`.
- The backend must support `visibility=all|public|private`; invalid values should return a 422 validation error.
- The frontend must fetch repositories only after the user is signed in.
- The frontend must render loading, empty, failure, and success states.
- The frontend must allow one selected repository at a time.
- The frontend must display whether a repository is public/private and user/org-owned.
- The UI must explain that Stage 1 reads repository metadata only; deeper activity evidence collection belongs to later stages.

## UX / UI Notes
- Entry point: signed-in panel on `apps/frontend/src/App.tsx`.
- Empty / loading / error states: inline within the repository selector card.
- Editing constraints: no new design-system dependency in this slice; reuse existing CSS and keep the UI clear.

## API / Backend Notes
- Endpoints: `GET /api/v1/repositories`.
- Auth / permissions: requires active session and server-side GitHub token for that session.
- Background processing: none.
- SSE / polling behavior: none.
- GitHub API: `GET https://api.github.com/user/repos` with `affiliation=owner,collaborator,organization_member`, `sort=updated`, `per_page=30`.
- OAuth scope note: private repositories require GitHub OAuth App `repo` scope; this is broad and should be revisited in a later GitHub App/fine-grained-token hardening pass.

## Data / Domain Notes
- Tables or entities touched: no database tables in this slice.
- External APIs touched: GitHub REST `/user/repos`.
- Stored artifacts: short-lived server-side in-memory token map keyed by session token id until persistence is introduced.

## Acceptance Criteria
- [ ] A signed-in user sees accessible repositories from GitHub.
- [ ] public/private and user/org ownership are visible.
- [ ] One repository can be selected.
- [ ] Unauthenticated users receive the standard unauthenticated error response.
- [ ] GitHub API errors are normalized into the standard error envelope.
- [ ] PRD/task/.omx plan artifacts exist and point to issue #1.
- [ ] Frontend and backend verification commands pass.

## Verification Plan
- Unit: `cd apps/backend && .venv/bin/python -m pytest tests`; `npm --prefix apps/frontend run test -- --run`.
- Integration: `npm --prefix apps/frontend run lint`; `npm --prefix apps/frontend run typecheck`.
- Manual: Sign in, confirm repositories load, select one, confirm data-access copy and failure states are understandable.

## Risks
- GitHub OAuth App private repository access requires broad `repo` scope.
- The in-memory token store is acceptable for this pre-persistence slice but not deploy-hardened.
- GitHub API pagination is intentionally minimal in this stage.

## Open Questions
- Should Stage 2 persist repository snapshots before or during analysis job creation?
- Should the long-term GitHub integration move from OAuth App scopes to GitHub App installation permissions for tighter private repo access?

## Approval
- Requested by: project owner
- Approved by: implicit roadmap execution request
- Approved at: 2026-04-15
