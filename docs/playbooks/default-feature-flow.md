# Default Feature Flow

This is the strongest harness path for this repo. The human should be able to say what they want once, and the system should progress through the standard stages without requiring command choreography.

## Principle
- A plain feature request is enough to start work.
- When GitHub auth and repo access are ready, the system should follow an issue-first GitHub delivery path.
- The system should create planning artifacts first.
- The system should continue into implementation by default.
- The system should only pause for ambiguity, destructive action, or explicit approval gates.

## Automatic Pipeline
1. Interpret the request and derive a short feature slug.
2. If GitHub auth + repo access are available, create or link a GitHub issue for the feature.
3. Create or update `docs/prd/<slug>.md`.
4. Create or update `docs/tasks/<slug>.md`.
5. Create or update `.omx/plans/prd-<slug>.md`.
6. Create or update `.omx/plans/test-spec-<slug>.md`.
7. If an issue exists, branch from it using `feat/<issue>-<slug>`; otherwise keep the local branch name explicit and report the missing issue as a blocker.
8. Implement the narrowest viable slice.
9. Run verification using the repo baseline in `docs/playbooks/verification-baseline.md` unless the feature docs define a narrower or stricter command set.
10. Update docs and task execution log.
11. Push the branch and prepare a PR or draft PR when GitHub permissions allow it.

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
- Create or link a GitHub issue when auth is available.
- Write the PRD, task, and test-spec artifacts.
- Start implementation if the path is clear.
- Open a branch and finish with push + PR/draft PR if permissions allow.
- Stop only if scope, auth policy, or API constraints need a decision.

## Output Discipline
- Do not dump the full plan repeatedly.
- Keep progress updates short.
- End with evidence: changed files, verification run, remaining risks.

## Related Playbooks
- For the stricter GitHub issue → branch → PR operating lane, use `docs/playbooks/github-issue-first-flow.md`.
