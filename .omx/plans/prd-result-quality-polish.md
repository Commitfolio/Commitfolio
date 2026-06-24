# OMX PRD: result-quality-polish

## Objective
Add optional OpenAI post-processing and a richer deterministic fallback so Commitfolio can generate portfolio-ready summaries from GitHub evidence even when no LLM key is configured.

## Issue / Branch
- Issue: https://github.com/Commitfolio/Commitfolio/issues/18
- Branch: `기능/이슈-18-결과-품질-개선-openai`

## Scope
- Backend optional OpenAI configuration and enhancement service
- Fallback-safe integration into result generation/regeneration
- Richer deterministic evidence inputs from GitHub repository metadata, README, language distribution, and top-level structure
- Higher-quality default wording for technology choice, implemented features, and collaboration signals
- Minimal persisted/API-visible enhancement status
- Frontend status display
- Tests proving no-key, success, and failure fallback paths

## Non-goals
- Streaming generation
- PDF export
- Required OpenAI dependency
- Prompt management framework
- Rewriting evidence link relationships

## Acceptance
- OpenAI missing key path behaves exactly as a successful deterministic generation path.
- OpenAI success path improves allowed text fields only.
- OpenAI failure path stores fallback output and exposes neutral fallback status.
- Existing frontend editor/regenerate behavior still works.
