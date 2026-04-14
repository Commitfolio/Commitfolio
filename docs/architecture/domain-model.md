# Domain Model

This document captures the first-pass core entities for the MVP. The goal is stable conceptual boundaries, not final table names.

## Core Entities

### User
- Represents an authenticated product user
- Key fields:
  - `id`
  - `email` or nullable app identifier
  - `created_at`
  - `last_login_at`

### ConnectedGitHubAccount
- Represents the GitHub account linked through OAuth
- Key fields:
  - `id`
  - `user_id`
  - `github_user_id`
  - `github_login`
  - `access_token_encrypted`
  - `scope`
  - `connected_at`

### RepositorySnapshot
- Cached metadata for a repository the user can access
- Key fields:
  - `id`
  - `github_repo_id`
  - `full_name`
  - `owner_type`
  - `private`
  - `default_branch`
  - `last_synced_at`

### AnalysisJob
- Represents one analysis run for one repository
- Key fields:
  - `id`
  - `user_id`
  - `repository_full_name`
  - `status`
  - `requested_at`
  - `started_at`
  - `completed_at`
  - `failure_reason`

### AnalysisEvidence
- Normalized evidence collected from GitHub during one job
- Key fields:
  - `id`
  - `analysis_job_id`
  - `source_type` (`commit`, `pull_request`, `issue`, `review`, `changed_file`)
  - `source_id`
  - `url`
  - `payload_json`

### PortfolioResult
- Stored generated result for one completed job
- Key fields:
  - `id`
  - `analysis_job_id`
  - `user_id`
  - `version`
  - `headline`
  - `project_overview`
  - `role_summary`
  - `key_contributions`
  - `tech_stack`
  - `evidence_summary`
  - `interview_questions`
  - `updated_at`

### PortfolioSectionEvidenceLink
- Maps result sections or sentences back to GitHub evidence
- Key fields:
  - `id`
  - `portfolio_result_id`
  - `section_key`
  - `evidence_id`
  - `label`
  - `url`

## Relationships
- One `User` has one or more `ConnectedGitHubAccount` rows over time.
- One `User` starts many `AnalysisJob` rows.
- One `AnalysisJob` targets one repository.
- One `AnalysisJob` produces many `AnalysisEvidence` rows.
- One `AnalysisJob` produces one or more `PortfolioResult` versions.
- One `PortfolioResult` has many `PortfolioSectionEvidenceLink` rows.

## Status Enums

### AnalysisJob.status
- `queued`
- `running`
- `completed`
- `failed`

## Design Rules
- Keep raw GitHub evidence separate from generated portfolio text.
- Store enough evidence to support regeneration without asking the user to re-select everything.
- Treat the editable result as an artifact derived from evidence, not as the evidence itself.
- Allow future support for reanalysis and multiple result versions.

## Likely MVP Tables
- `users`
- `connected_github_accounts`
- `repository_snapshots`
- `analysis_jobs`
- `analysis_evidence`
- `portfolio_results`
- `portfolio_section_evidence_links`
