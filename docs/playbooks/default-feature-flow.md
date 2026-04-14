# Default Feature Flow

This is the strongest harness path for this repo. The human should be able to say what they want once, and the system should progress through the standard stages without requiring command choreography.

## Principle
- A plain feature request is enough to start work.
- The system should create planning artifacts first.
- The system should continue into implementation by default.
- The system should only pause for ambiguity, destructive action, or explicit approval gates.

## Automatic Pipeline
1. Interpret the request and derive a short feature slug.
2. Create or update `docs/prd/<slug>.md`.
3. Create or update `docs/tasks/<slug>.md`.
4. Create or update `.omx/plans/prd-<slug>.md`.
5. Create or update `.omx/plans/test-spec-<slug>.md`.
6. Implement the narrowest viable slice.
7. Run verification.
8. Update docs and task execution log.
9. Prepare the branch for PR or draft PR.

## When To Pause
- The request is genuinely ambiguous.
- The change is destructive or irreversible.
- The change touches auth, permissions, secrets, or data policy in a way that needs a human choice.
- The user explicitly says "do not implement until I approve".

## Expected Human Input
- A product request, bug report, or change request.
- Optional corrections if the generated plan is wrong.
- Optional approval only when the task explicitly requires a gate.

## Example
Human input:

```text
GitHub OAuth 로그인 기능 만들고 싶어.
```

Expected system behavior:
- Define a slug such as `github-oauth`.
- Write the PRD, task, and test-spec artifacts.
- Start implementation if the path is clear.
- Stop only if scope, auth policy, or API constraints need a decision.

## Output Discipline
- Do not dump the full plan repeatedly.
- Keep progress updates short.
- End with evidence: changed files, verification run, remaining risks.
