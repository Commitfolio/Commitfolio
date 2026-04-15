# Feature Delivery Playbook

This repo uses a document-first harness. The goal is to let the human approve intent and scope, then let Codex/OMX execute against a fixed contract.

If you want the strongest automatic path, use [default-feature-flow.md](/Users/donggun/Desktop/Commitfolio/docs/playbooks/default-feature-flow.md). This file documents the stricter approval-gated variant.

## Default Flow
1. Request arrives.
2. Create or link a GitHub issue.
3. Create or update a PRD in `docs/prd/`.
4. Create or update a task checklist in `docs/tasks/`.
5. Human reviews and approves scope.
6. Create branch from the issue.
7. Implement against the approved docs.
8. Run verification.
9. Open a draft PR with doc links and verification notes.

## What The Human Should Do
- Describe the feature or change.
- Review the PRD and task checklist.
- Approve or narrow scope.
- Review final PR/draft PR.

## What Codex / OMX Should Do
- Turn vague requests into a concrete brief.
- Keep implementation aligned with the approved PRD/task.
- Refuse silent scope creep by updating docs first.
- Verify with lint, typecheck, tests, and manual checks where applicable.

## Recommended OMX Session Pattern

### 1. Start an interactive OMX session
```bash
cd /Users/donggun/Desktop/Commitfolio
omx
```

### 2. Plan before coding
Inside Codex, use prompts like:

```text
$ralplan 이번 기능은 GitHub OAuth 로그인 플로우다. PRD와 task부터 정리해줘.
```

Use `$deep-interview` instead when the request is still ambiguous.

### 3. Only implement after approval
After you approve the PRD/task:

```text
승인함. docs/prd/github-oauth.md 와 docs/tasks/github-oauth.md 기준으로 구현 진행해.
```

If you want OMX runtime persistence for a single approved feature:

```bash
omx ralph
```

If you want parallel execution for a clearly split task:

```bash
omx team
```

## When To Use This Playbook
- Use this file when you want a deliberate review checkpoint before coding.
- Use it for auth, permissions, billing, data policy, or major scope questions.
- Use [default-feature-flow.md](/Users/donggun/Desktop/Commitfolio/docs/playbooks/default-feature-flow.md) when you want the system to continue automatically unless blocked.
- Use [github-issue-first-flow.md](/Users/donggun/Desktop/Commitfolio/docs/playbooks/github-issue-first-flow.md) when you want GitHub issue → branch → PR discipline spelled out.

## Branch and PR Discipline
- One approved task per branch.
- Branch name should include the issue number when one exists.
- PR body should link the PRD and task doc.
- A task is incomplete if verification evidence is missing.

## Suggested Branch Naming
- `feat/123-github-oauth`
- `feat/124-repo-selector`
- `feat/125-analysis-job-sse`
- `fix/126-pdf-layout`

## Minimal Prompting Contract
Use this pattern when you want "approve first, implement second":

```text
이 요청을 바로 구현하지 말고 먼저 PRD와 task 문서로 브리핑해. 내가 approve 하면 그때 구현해.
```

Use this pattern when the docs are already approved:

```text
docs/prd/<file>.md 와 docs/tasks/<file>.md 승인됨. 이 기준으로 구현하고 테스트와 문서 반영까지 끝내.
```

## Definition of Done
- Approved PRD exists.
- Matching task checklist exists.
- Code is implemented.
- Relevant docs are updated.
- Verification evidence exists.
- Branch is ready for PR or draft PR.
