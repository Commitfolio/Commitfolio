# System Overview

## Product Summary
Commitfolio analyzes activity from one GitHub repository that a signed-in user can access and turns that evidence into an editable portfolio-style result.

## Default Stack
- Frontend: React + Vite + TypeScript
- Backend: FastAPI
- Database: PostgreSQL
- ORM / migrations: SQLAlchemy 2.x + Alembic
- Realtime progress: SSE
- Deployment target: Vercel + Render + Neon

## High-Level Architecture
1. The frontend starts a GitHub OAuth login flow.
2. The backend exchanges the OAuth code, stores the minimal account linkage, and fetches the user's accessible repositories.
3. The user selects one repository for analysis.
4. The frontend requests an analysis job.
5. The backend creates an `analysis_job`, collects GitHub evidence, derives structured summaries, and stores the generated portfolio result.
6. The frontend subscribes to job progress through SSE.
7. The user reviews, edits, saves, and downloads the generated result.

## Main Boundaries

### Frontend (`apps/frontend`)
- Login and repository selection UI
- Analysis start / progress UI
- Portfolio result viewer and editor
- Download UI

### Backend (`apps/backend`)
- OAuth callback and session endpoints
- GitHub repository listing endpoints
- Analysis job creation and job status endpoints
- SSE progress stream
- Portfolio result read / update endpoints

### Database
- User and GitHub linkage
- Analysis jobs and status history
- Stored normalized evidence and generated results

### External Systems
- GitHub OAuth
- GitHub REST / GraphQL APIs
- OpenAI API in later quality-improvement phase

## Backend Module Direction
- `api/`: FastAPI routers and request/response schemas
- `services/`: orchestration and business use cases
- `integrations/github/`: OAuth + GitHub API client code
- `analysis/`: evidence collection, heuristics, summarization pipeline
- `db/`: SQLAlchemy models, sessions, migrations
- `domain/`: entity and value-object level rules where needed

## Request Flow

### Authentication
1. Frontend redirects to GitHub.
2. Backend handles callback.
3. Backend stores the linked GitHub account and session state.

### Repository Selection
1. Frontend asks for accessible repositories.
2. Backend calls GitHub APIs with the stored token.
3. Frontend shows public / private / org repositories the user can access.

### Analysis
1. Frontend posts a selected repository.
2. Backend creates a job row.
3. Backend collects commits, PRs, issues, reviews, and changed-file evidence.
4. Backend derives structured output sections.
5. Backend emits progress events over SSE.
6. Backend stores the final result and evidence references.

## Non-Functional Goals
- Favor deterministic, rule-based generation before LLM refinement.
- Keep OAuth scopes minimal.
- Make job progress observable.
- Preserve enough raw evidence to support regeneration and citation links.

## Open Architectural Decisions
- Session mechanism: secure cookie session vs token-based frontend session
- Background execution strategy: in-process async tasks vs external worker
- PDF generation approach: browser print pipeline vs dedicated renderer
