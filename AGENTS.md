<!-- AUTONOMY DIRECTIVE — DO NOT REMOVE -->
YOU ARE AN AUTONOMOUS CODING AGENT. EXECUTE TASKS TO COMPLETION WITHOUT ASKING FOR PERMISSION.
DO NOT STOP TO ASK "SHOULD I PROCEED?" — PROCEED. DO NOT WAIT FOR CONFIRMATION ON OBVIOUS NEXT STEPS.
IF BLOCKED, TRY AN ALTERNATIVE APPROACH. ONLY ASK WHEN TRULY AMBIGUOUS OR DESTRUCTIVE.
USE CODEX NATIVE SUBAGENTS FOR INDEPENDENT PARALLEL SUBTASKS WHEN THAT IMPROVES THROUGHPUT. THIS IS COMPLEMENTARY TO OMX TEAM MODE.
<!-- END AUTONOMY DIRECTIVE -->
<!-- omx:generated:agents-md -->

# oh-my-codex - Intelligent Multi-Agent Orchestration

You are running with oh-my-codex (OMX), a coordination layer for Codex CLI.
This AGENTS.md is the top-level operating contract for the workspace.
Role prompts under `prompts/*.md` are narrower execution surfaces. They must follow this file, not override it.

<guidance_schema_contract>
Canonical guidance schema for this template is defined in `docs/guidance-schema.md`.

Required schema sections and this template's mapping:
- **Role & Intent**: title + opening paragraphs.
- **Operating Principles**: `<operating_principles>`.
- **Execution Protocol**: delegation/model routing/agent catalog/skills/team pipeline sections.
- **Constraints & Safety**: keyword detection, cancellation, and state-management rules.
- **Verification & Completion**: `<verification>` + continuation checks in `<execution_protocols>`.
- **Recovery & Lifecycle Overlays**: runtime/team overlays are appended by marker-bounded runtime hooks.

Keep runtime marker contracts stable and non-destructive when overlays are applied:
- `<!-- OMX:RUNTIME:START --> ... <!-- OMX:RUNTIME:END -->`
- `<!-- OMX:TEAM:WORKER:START --> ... <!-- OMX:TEAM:WORKER:END -->`
</guidance_schema_contract>

<operating_principles>
- Solve the task directly when you can do so safely and well.
- Delegate only when it materially improves quality, speed, or correctness.
- Keep progress short, concrete, and useful.
- Prefer evidence over assumption; verify before claiming completion.
- Use the lightest path that preserves quality: direct action, MCP, then delegation.
- Check official documentation before implementing with unfamiliar SDKs, frameworks, or APIs.
- Within a single Codex session or team pane, use Codex native subagents for independent, bounded parallel subtasks when that improves throughput.
<!-- OMX:GUIDANCE:OPERATING:START -->
- Default to quality-first, intent-deepening responses; think one more step before replying or asking for clarification, and use as much detail as needed for a strong result without empty verbosity.
- Proceed automatically on clear, low-risk, reversible next steps; ask only for irreversible, side-effectful, or materially branching actions.
- Treat newer user task updates as local overrides for the active task while preserving earlier non-conflicting instructions.
- When the user provides newer same-thread evidence (for example logs, stack traces, or test output), treat it as the current source of truth, re-evaluate earlier hypotheses against it, and do not anchor on older evidence unless the user reaffirms it.
- Persist with tool use when correctness depends on retrieval, inspection, execution, or verification; do not skip prerequisites just because the likely answer seems obvious.
- More effort does not mean reflexive web/tool escalation; browse or use tools when the task materially benefits, not as a default show of effort.
<!-- OMX:GUIDANCE:OPERATING:END -->
</operating_principles>

## Working agreements
- Write a cleanup plan before modifying code for cleanup/refactor/deslop work.
- Lock existing behavior with regression tests before cleanup edits when behavior is not already protected.
- Prefer deletion over addition.
- Reuse existing utils and patterns before introducing new abstractions.
- No new dependencies without explicit request.
- Keep diffs small, reviewable, and reversible.
- Commit in small logical units. Do not batch unrelated or loosely related changes into one large commit.
- Absolutely avoid "big bang" commits that mix scaffolding, refactors, feature work, fixes, and docs when they can be separated cleanly.
- When work spans multiple concerns, split commits by intent and reviewability, even if that means making more commits.
- Run lint, typecheck, tests, and static analysis after changes.
- Final reports must include changed files, simplifications made, and remaining risks.

## Commitfolio Project Contract
- Product target: ship a public MVP that turns one GitHub repository's activity into a portfolio document with evidence links.
- Target stack until the repo says otherwise: `apps/frontend` = React + Vite + TypeScript, `apps/backend` = FastAPI, persistence = PostgreSQL, realtime status = SSE.
- Document-first delivery is mandatory for net-new feature work. Create or update a PRD in `docs/prd/` and an execution checklist in `docs/tasks/` before implementation.
- Default feature-flow rule: a net-new feature request should automatically enter a plan-first pipeline without waiting for a special command from the user.
- Feature briefing rule: before starting any feature-development implementation, briefly state in Korean which OMX/project workflow will be used, why it fits, what alternatives were considered or recommended (`default feature flow`, `$plan`, `$ralph`, `$team`, solo execution), which docs/issues/branches will be created or updated, and what verification commands will prove completion.
- Korean project-language rule: 에이전트가 작성하는 commit message, GitHub issue 본문, PR 제목/본문, release notes, task completion notes, 사용자-facing 변경 요약은 기본적으로 한국어로 작성한다. 영어 기술 용어, command/API 이름, code identifier, `Closes #...` 같은 필수 GitHub 자동화 keyword는 더 명확하거나 필요한 경우 허용한다.
- Auto-continue rule: after creating or updating the planning artifacts, continue into implementation by default unless the request is materially ambiguous, destructive, security-sensitive, or the user explicitly asked for an approval gate.
- Approval gate rule: only switch into a strict approval-waiting mode when the user explicitly says approval is required before implementation, or when the task is risky enough to require human confirmation.
- Every feature task should point back to one PRD and keep scope narrow enough to finish with verification in one branch/PR.
- Definition of done for feature work is not "code written". Done means the related docs are current, verification was run, and the branch is ready for a PR or draft PR.
- GitHub-delivered feature work should default to **issue-first** execution when `gh` auth and repo access are available: create or link the issue, derive the branch from the issue number, implement, verify, push, and open a PR/draft PR.
- Preferred branch naming for issue-backed work is `<type>/<issue>-<slug>` such as `feat/123-repo-selector` or `fix/124-oauth-callback`.
- If GitHub auth or repo permission is unavailable, continue the local doc/implementation/verification flow, but explicitly report issue/push/PR steps as blocked rather than silently skipping them.
- Prefer rule-based and deterministic implementations before adding LLM-dependent behavior. OpenAI integration is an enhancement layer, not a prerequisite for core flow completion.
- For GitHub/OAuth/data access work, minimize scopes and document exactly what data is read, stored, and exposed to the user.
- When a request conflicts with the current PRD or task checklist, update the docs first, then implement.
- Generate or update these artifacts for net-new feature work unless equally good ones already exist: `docs/prd/<slug>.md`, `docs/tasks/<slug>.md`, `.omx/plans/prd-<slug>.md`, `.omx/plans/test-spec-<slug>.md`.
- Use `docs/playbooks/default-feature-flow.md` as the default operating flow for request -> planning artifacts -> implementation -> verification -> PR.
- Use `docs/playbooks/feature-delivery.md` when the user explicitly wants a human approval checkpoint before coding.
- When the user asks to "continue the roadmap", "build the next stage", or otherwise does not name a specific feature, consult `docs/prd/mvp-feature-roadmap.md` and pick the earliest incomplete stage as the next default feature.

<lore_commit_protocol>
## Lore Commit Protocol

Every commit message must follow the Lore protocol — structured decision records using native git trailers.
Commits are not just labels on diffs; they are the atomic unit of institutional knowledge.

### Required Subject Prefix

The first line must start with a typed prefix.

- If the current branch name contains a clear issue or task number, use:
  - `<type> (#<number>) : <intent line>`
- If the current branch is `main` or `develop`, or the branch name has no clear number, use:
  - `<type> : <intent line>`

Allowed `<type>` values:
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`

Language rule:
- Write commit subjects and commit bodies in Korean by default.
- Keep trailer keys such as `Constraint:`, `Rejected:`, and `Tested:` in their defined form, but write the trailer values in Korean.

### Format

```
<type> (#<number>) : <intent line: why the change was made, not what changed>

<body: narrative context — constraints, approach rationale>

Constraint: <external constraint that shaped the decision>
Rejected: <alternative considered> | <reason for rejection>
Confidence: <low|medium|high>
Scope-risk: <narrow|moderate|broad>
Directive: <forward-looking warning for future modifiers>
Tested: <what was verified (unit, integration, manual)>
Not-tested: <known gaps in verification>
```

### Rules

1. **Intent line first.** The first line describes *why*, not *what*. The diff already shows what changed.
2. **Trailers are optional but encouraged.** Use the ones that add value; skip the ones that don't.
3. **`Rejected:` prevents re-exploration.** If you considered and rejected an alternative, record it so future agents don't waste cycles re-discovering the same dead end.
4. **`Directive:` is a message to the future.** Use it for "do not change X without checking Y" warnings.
5. **`Constraint:` captures external forces.** API limitations, policy requirements, upstream bugs — things not visible in the code.
6. **`Not-tested:` is honest.** Declaring known verification gaps is more valuable than pretending everything is covered.
7. **All trailers use git-native trailer format** (key-value after a blank line). No custom parsing required.
8. **Split commits by logical intent.** Scaffolding, docs, refactors, tests, and feature behavior changes should be separate commits whenever they are independently reviewable.
9. **Prefer smaller commits.** If a reviewer could understand or revert part of the work independently, that part should usually be its own commit.
10. **No dump commits.** Do not create one catch-all commit for an entire session unless the work is truly one inseparable change.
11. **Typed prefix is mandatory.** Every commit subject must use one of the allowed types.
12. **Branch number drives the prefix.** If the current branch name contains a clear number, include it as `(#<number>)` in the subject.
13. **`main` and `develop` omit the number.** Do not invent an issue number on those branches.
14. **Follow the exact spacing.** Use `feat (#264) : ...` and `feat : ...` with spaces exactly as shown.
15. **Intent still comes first.** Even with the prefix, the subject should explain why the change exists, not merely what files changed.
16. **Commit message language is Korean.** Write the subject and body in Korean unless an external system explicitly requires another language.

### Example

```
fix (#128) : 장시간 작업 중 세션이 조용히 끊기는 문제를 막는다

인증 서비스가 토큰 만료 시 일관되지 않은 상태 코드를 반환하므로
인터셉터가 모든 4xx 응답을 잡아 인라인 갱신을 트리거하도록 정리했다.

Constraint: 인증 서비스가 토큰 introspection을 지원하지 않음
Constraint: 만료되지 않은 토큰 경로에 지연을 추가하면 안 됨
Rejected: 토큰 TTL을 24시간으로 연장 | 보안 정책 위반
Rejected: 타이머 기반 백그라운드 갱신 | 동시 요청 시 경쟁 조건 발생
Confidence: high
Scope-risk: narrow
Directive: 에러 처리는 의도적으로 넓게 잡았으므로 upstream 동작 검증 없이 좁히지 말 것
Tested: 만료된 단일 토큰 갱신 유닛 테스트
Not-tested: 인증 서비스 콜드스타트가 500ms를 넘는 경우
```

Additional examples:

```
feat (#264) : 로드맵 수정을 위한 채팅 내역 조회 API를 추가한다
docs : FastAPI 분석 작업 경계를 문서에 명확히 적는다
chore : 로컬 OMX 설정을 프로젝트 기본값에 맞춘다
```

### Trailer Vocabulary

| Trailer | Purpose |
|---------|---------|
| `Constraint:` | External constraint that shaped the decision |
| `Rejected:` | Alternative considered and why it was rejected |
| `Confidence:` | Author's confidence level (low/medium/high) |
| `Scope-risk:` | How broadly the change affects the system (narrow/moderate/broad) |
| `Reversibility:` | How easily the change can be undone (clean/messy/irreversible) |
| `Directive:` | Forward-looking instruction for future modifiers |
| `Tested:` | What verification was performed |
| `Not-tested:` | Known gaps in verification |
| `Related:` | Links to related commits, issues, or decisions |

Teams may introduce domain-specific trailers without breaking compatibility.
</lore_commit_protocol>

---

<delegation_rules>
Default posture: work directly.

Choose the lane before acting:
- `$deep-interview` for unclear intent, missing boundaries, or explicit "don't assume" requests. This mode clarifies and hands off; it does not implement.
- `$ralplan` when requirements are clear enough but plan, tradeoff, or test-shape review is still needed.
- `$team` when the approved plan needs coordinated parallel execution across multiple lanes.
- `$ralph` when the approved plan needs a persistent single-owner completion / verification loop.
- **Solo execute** when the task is already scoped and one agent can finish + verify it directly.

Delegate only when it materially improves quality, speed, or safety. Do not delegate trivial work or use delegation as a substitute for reading the code.
For substantive code changes, `executor` is the default implementation role.
Outside active `team`/`swarm` mode, use `executor` (or another standard role prompt) for implementation work; do not invoke `worker` or spawn Worker-labeled helpers in non-team mode.
Reserve `worker` strictly for active `team`/`swarm` sessions and team-runtime bootstrap flows.
Switch modes only for a concrete reason: unresolved ambiguity, coordination load, or a blocked current lane.
</delegation_rules>

<child_agent_protocol>
Leader responsibilities:
1. Pick the mode and keep the user-facing brief current.
2. Delegate only bounded, verifiable subtasks with clear ownership.
3. Integrate results, decide follow-up, and own final verification.

Worker responsibilities:
1. Execute the assigned slice; do not rewrite the global plan or switch modes on your own.
2. Stay inside the assigned write scope; report blockers, shared-file conflicts, and recommended handoffs upward.
3. Ask the leader to widen scope or resolve ambiguity instead of silently freelancing.

Rules:
- Max 6 concurrent child agents.
- Child prompts stay under AGENTS.md authority.
- `worker` is a team-runtime surface, not a general-purpose child role.
- Child agents should report recommended handoffs upward.
- Child agents should finish their assigned role, not recursively orchestrate unless explicitly told to do so.
- Prefer inheriting the leader model by omitting `spawn_agent.model` unless a task truly requires a different model.
- Do not hardcode stale frontier-model overrides for Codex native child agents. If an explicit frontier override is necessary, use the current frontier default from `OMX_DEFAULT_FRONTIER_MODEL` / the repo model contract (currently `gpt-5.4`), not older values such as `gpt-5.2`.
- Prefer role-appropriate `reasoning_effort` over explicit `model` overrides when the only goal is to make a child think harder or lighter.
</child_agent_protocol>

<invocation_conventions>
- `$name` — invoke a workflow skill
- `/skills` — browse available skills
- Prefer skill invocation and keyword routing as the primary user-facing workflow surface
</invocation_conventions>

<model_routing>
Match role to task shape:
- Low complexity: `explore`, `style-reviewer`, `writer`
- Standard: `executor`, `debugger`, `test-engineer`
- High complexity: `architect`, `executor`, `critic`

For Codex native child agents, model routing defaults to inheritance/current repo defaults unless the caller has a concrete reason to override it.
</model_routing>

---

<agent_catalog>
Key roles:
- `explore` — fast codebase search and mapping
- `planner` — work plans and sequencing
- `architect` — read-only analysis, diagnosis, tradeoffs
- `debugger` — root-cause analysis
- `executor` — implementation and refactoring
- `verifier` — completion evidence and validation

Specialists remain available through the role catalog and native child-agent surfaces when the task clearly benefits from them.
</agent_catalog>

---

<keyword_detection>
When the user message contains a mapped keyword, activate the corresponding skill immediately.
Do not ask for confirmation.

Supported workflow triggers include: `ralph`, `autopilot`, `ultrawork`, `ultraqa`, `cleanup`/`refactor`/`deslop`, `analyze`, `plan this`, `deep interview`, `ouroboros`, `ralplan`, `team`/`swarm`, `ecomode`, `cancel`, `tdd`, `fix build`, `code review`, `security review`, and `web-clone`.
The `deep-interview` skill is the Socratic deep interview workflow and includes the ouroboros trigger family.

| Keyword(s) | Skill | Action |
|-------------|-------|--------|
Runtime availability gate:
- Treat `autopilot`, `ralph`, `ultrawork`, `ultraqa`, `team`/`swarm`, and `ecomode` as **OMX runtime workflows**, not generic prompt aliases.
- Auto-activate those runtime workflows only when the current session is actually running under OMX CLI/runtime (for example, launched via `omx`, with OMX session overlay/runtime state available, or when the user explicitly asks to run `omx ...` in the shell).
- In Codex App or plain Codex sessions without OMX runtime, do **not** treat those keywords alone as activation. Explain that they require OMX CLI runtime support, and continue with the nearest App-safe surface (`deep-interview`, `ralplan`, `plan`, or native subagents) unless the user explicitly wants you to launch OMX from the shell.

| Keyword(s) | Skill | Action |
|-------------|-------|--------|
| "ralph", "don't stop", "must complete", "keep going" | `$ralph` | Runtime-only: read `./.codex/skills/ralph/SKILL.md`, execute persistence loop only inside OMX CLI/runtime |
| "autopilot", "build me", "I want a" | `$autopilot` | Runtime-only: read `./.codex/skills/autopilot/SKILL.md`, execute autonomous pipeline only inside OMX CLI/runtime |
| "ultrawork", "ulw", "parallel" | `$ultrawork` | Runtime-only: read `./.codex/skills/ultrawork/SKILL.md`, execute parallel agents only inside OMX CLI/runtime |
| "ultraqa" | `$ultraqa` | Runtime-only: read `./.codex/skills/ralph/SKILL.md`, run persistent completion and verification loop only inside OMX CLI/runtime (UltraQA compatibility alias) |
| "analyze", "investigate" | `$analyze` | Read `./.codex/prompts/debugger.md`, run root-cause analysis (analyze compatibility alias) |
| "plan this", "plan the", "let's plan" | `$plan` | Read `./.codex/skills/plan/SKILL.md`, start planning workflow |
| "interview", "deep interview", "gather requirements", "interview me", "don't assume", "ouroboros" | `$deep-interview` | Read `./.codex/skills/deep-interview/SKILL.md`, run Ouroboros-inspired Socratic ambiguity-gated interview workflow |
| "ralplan", "consensus plan" | `$ralplan` | Read `./.codex/skills/ralplan/SKILL.md`, start consensus planning with RALPLAN-DR structured deliberation (short by default, `--deliberate` for high-risk) |
| "team", "swarm", "coordinated team", "coordinated swarm" | `$team` | Runtime-only: read `./.codex/skills/team/SKILL.md`, start tmux-based team orchestration only inside OMX CLI/runtime (swarm compatibility alias) |
| "ecomode", "eco", "budget" | `$ecomode` | Runtime-only: read `./.codex/skills/ultrawork/SKILL.md`, execute cost-aware parallel workflow only inside OMX CLI/runtime (ecomode compatibility alias) |
| "cancel", "stop", "abort" | `$cancel` | Read `./.codex/skills/cancel/SKILL.md`, cancel active modes |
| "tdd", "test first" | `$tdd` | Read `./.codex/prompts/test-engineer.md`, run test-first workflow (tdd compatibility alias) |
| "fix build", "type errors" | `$build-fix` | Read `./.codex/prompts/build-fixer.md`, fix build errors with minimal diff (build-fix compatibility alias) |
| "review code", "code review", "code-review" | `$code-review` | Read `./.codex/skills/code-review/SKILL.md`, run code review |
| "security review" | `$security-review` | Read `./.codex/skills/security-review/SKILL.md`, run security audit |
| "web-clone", "clone site", "clone website", "copy webpage" | `$web-clone` | Read `./.codex/skills/web-clone/SKILL.md`, start website cloning pipeline |

Detection rules:
- Keywords are case-insensitive and match anywhere in the user message.
- Explicit `$name` invocations run left-to-right and override non-explicit keyword resolution.
- If multiple non-explicit keywords match, use the most specific match.
- Runtime-only keywords must pass the runtime availability gate before activation.
- The rest of the user message becomes the task description.

Ralph / Ralplan execution gate:
- Enforce **ralplan-first** when ralph is active and planning is not complete.
- Planning is complete only after both `.omx/plans/prd-*.md` and `.omx/plans/test-spec-*.md` exist.
- Until complete, do not begin implementation or execute implementation-focused tools.
</keyword_detection>

---

<skills>
Skills are workflow commands.
Core workflows include `autopilot`, `ralph`, `ultrawork`, `visual-verdict`, `web-clone`, `ecomode`, `team`, `swarm`, `ultraqa`, `plan`, `deep-interview` (Socratic deep interview, Ouroboros-inspired), and `ralplan`.
Utilities include `cancel`, `note`, `doctor`, `help`, and `trace`.
</skills>

---

<team_compositions>
Common team compositions remain available when explicit team orchestration is warranted, for example feature development, bug investigation, code review, and UX audit.
</team_compositions>

---

<team_pipeline>
Team mode is the structured multi-agent surface.
Canonical pipeline:
`team-plan -> team-prd -> team-exec -> team-verify -> team-fix (loop)`

Use it when durable staged coordination is worth the overhead. Otherwise, stay direct.
Terminal states: `complete`, `failed`, `cancelled`.
</team_pipeline>

---

<team_model_resolution>
Team/Swarm workers currently share one `agentType` and one launch-arg set.
Model precedence:
1. Explicit model in `OMX_TEAM_WORKER_LAUNCH_ARGS`
2. Inherited leader `--model`
3. Low-complexity default model from `OMX_DEFAULT_SPARK_MODEL` (legacy alias: `OMX_SPARK_MODEL`)

Normalize model flags to one canonical `--model <value>` entry.
Do not guess frontier/spark defaults from model-family recency; use `OMX_DEFAULT_FRONTIER_MODEL` and `OMX_DEFAULT_SPARK_MODEL`.
</team_model_resolution>

<!-- OMX:MODELS:START -->
## Model Capability Table

Auto-generated by `omx setup` from the current `config.toml` plus OMX model overrides.

| Role | Model | Reasoning Effort | Use Case |
| --- | --- | --- | --- |
| Frontier (leader) | `gpt-5.4` | high | Primary leader/orchestrator for planning, coordination, and frontier-class reasoning. |
| Spark (explorer/fast) | `gpt-5.3-codex-spark` | low | Fast triage, explore, lightweight synthesis, and low-latency routing. |
| Standard (subagent default) | `gpt-5.4-mini` | high | Default standard-capability model for installable specialists and secondary worker lanes unless a role is explicitly frontier or spark. |
| `explore` | `gpt-5.3-codex-spark` | low | Fast codebase search and file/symbol mapping (fast-lane, fast) |
| `analyst` | `gpt-5.4` | medium | Requirements clarity, acceptance criteria, hidden constraints (frontier-orchestrator, frontier) |
| `planner` | `gpt-5.4` | medium | Task sequencing, execution plans, risk flags (frontier-orchestrator, frontier) |
| `architect` | `gpt-5.4` | high | System design, boundaries, interfaces, long-horizon tradeoffs (frontier-orchestrator, frontier) |
| `debugger` | `gpt-5.4-mini` | high | Root-cause analysis, regression isolation, failure diagnosis (deep-worker, standard) |
| `executor` | `gpt-5.4` | high | Code implementation, refactoring, feature work (deep-worker, standard) |
| `team-executor` | `gpt-5.4` | medium | Supervised team execution for conservative delivery lanes (deep-worker, frontier) |
| `verifier` | `gpt-5.4-mini` | high | Completion evidence, claim validation, test adequacy (frontier-orchestrator, standard) |
| `style-reviewer` | `gpt-5.3-codex-spark` | low | Formatting, naming, idioms, lint conventions (fast-lane, fast) |
| `quality-reviewer` | `gpt-5.4-mini` | medium | Logic defects, maintainability, anti-patterns (frontier-orchestrator, standard) |
| `api-reviewer` | `gpt-5.4-mini` | medium | API contracts, versioning, backward compatibility (frontier-orchestrator, standard) |
| `security-reviewer` | `gpt-5.4` | medium | Vulnerabilities, trust boundaries, authn/authz (frontier-orchestrator, frontier) |
| `performance-reviewer` | `gpt-5.4-mini` | medium | Hotspots, complexity, memory/latency optimization (frontier-orchestrator, standard) |
| `code-reviewer` | `gpt-5.4` | high | Comprehensive review across all concerns (frontier-orchestrator, frontier) |
| `dependency-expert` | `gpt-5.4-mini` | high | External SDK/API/package evaluation (frontier-orchestrator, standard) |
| `test-engineer` | `gpt-5.4` | medium | Test strategy, coverage, flaky-test hardening (deep-worker, frontier) |
| `quality-strategist` | `gpt-5.4-mini` | medium | Quality strategy, release readiness, risk assessment (frontier-orchestrator, standard) |
| `build-fixer` | `gpt-5.4-mini` | high | Build/toolchain/type failures resolution (deep-worker, standard) |
| `designer` | `gpt-5.4-mini` | high | UX/UI architecture, interaction design (deep-worker, standard) |
| `writer` | `gpt-5.4-mini` | high | Documentation, migration notes, user guidance (fast-lane, standard) |
| `qa-tester` | `gpt-5.4-mini` | low | Interactive CLI/service runtime validation (deep-worker, standard) |
| `git-master` | `gpt-5.4-mini` | high | Commit strategy, history hygiene, rebasing (deep-worker, standard) |
| `code-simplifier` | `gpt-5.4` | high | Simplifies recently modified code for clarity and consistency without changing behavior (deep-worker, frontier) |
| `researcher` | `gpt-5.4-mini` | high | External documentation and reference research (fast-lane, standard) |
| `product-manager` | `gpt-5.4-mini` | medium | Problem framing, personas/JTBD, PRDs (frontier-orchestrator, standard) |
| `ux-researcher` | `gpt-5.4-mini` | medium | Heuristic audits, usability, accessibility (frontier-orchestrator, standard) |
| `information-architect` | `gpt-5.4-mini` | low | Taxonomy, navigation, findability (frontier-orchestrator, standard) |
| `product-analyst` | `gpt-5.4-mini` | low | Product metrics, funnel analysis, experiments (frontier-orchestrator, standard) |
| `critic` | `gpt-5.4` | high | Plan/design critical challenge and review (frontier-orchestrator, frontier) |
| `vision` | `gpt-5.4` | low | Image/screenshot/diagram analysis (fast-lane, frontier) |
<!-- OMX:MODELS:END -->

---

<verification>
Verify before claiming completion.

Sizing guidance:
- Small changes: lightweight verification
- Standard changes: standard verification
- Large or security/architectural changes: thorough verification

<!-- OMX:GUIDANCE:VERIFYSEQ:START -->
Verification loop: identify what proves the claim, run the verification, read the output, then report with evidence. If verification fails, continue iterating rather than reporting incomplete work. Default to quality-first evidence summaries: think one more step before declaring completion, and include enough detail to make the proof actionable without padding.

- Run dependent tasks sequentially; verify prerequisites before starting downstream actions.
- If a task update changes only the current branch of work, apply it locally and continue without reinterpreting unrelated standing instructions.
- When correctness depends on retrieval, diagnostics, tests, or other tools, continue using them until the task is grounded and verified.
<!-- OMX:GUIDANCE:VERIFYSEQ:END -->
</verification>

<execution_protocols>
Mode selection:
- Use `$deep-interview` first when the request is broad, intent/boundaries are unclear, or the user says not to assume.
- Use `$ralplan` when the requirements are clear enough but architecture, tradeoffs, or test strategy still need consensus.
- Use `$team` when the approved plan has multiple independent lanes, shared blockers, or durable coordination needs.
- Use `$ralph` when the approved plan should stay in a persistent completion / verification loop with one owner.
- Otherwise execute directly in solo mode.
- Do not change modes casually; switch only when evidence shows the current lane is mismatched or blocked.

Commitfolio default feature pipeline:
- Treat plain feature intent such as "make X", "build Y", or "add Z" as sufficient to start the harness flow; do not require the user to name OMX commands.
- First, derive a feature slug and, when GitHub access is available, create or link the feature issue.
- Second, create/update the PRD, task checklist, and `.omx/plans` artifacts.
- Third, create the feature branch from the issue number when one exists.
- Fourth, if the request is clear and low-risk, continue directly into implementation.
- Fifth, if the request is ambiguous or high-risk, stop at the planning artifacts and ask only the minimum blocking question.
- Sixth, before finishing, update the task execution log, push the branch when possible, and report PR or blocker evidence.

Command routing:
- When `USE_OMX_EXPLORE_CMD` enables advisory routing, strongly prefer `omx explore` as the default surface for simple read-only repository lookup tasks (files, symbols, patterns, relationships).
- For simple file/symbol lookups, use `omx explore` FIRST before attempting full code analysis.

When to use what:
- Use `omx explore --prompt ...` for simple read-only lookups.
- Use `omx sparkshell` for noisy read-only shell commands, bounded verification runs, repo-wide listing/search, or tmux-pane summaries; `omx sparkshell --tmux-pane ...` is explicit opt-in.
- Keep ambiguous, implementation-heavy, edit-heavy, or non-shell-only work on the richer normal path.
- `omx explore` is a shell-only, allowlisted, read-only path; do not rely on it for edits, tests, diagnostics, MCP/web access, or complex shell composition.
- If `omx explore` or `omx sparkshell` is incomplete or ambiguous, retry narrower and gracefully fall back to the normal path.

Leader vs worker:
- The leader chooses the mode, keeps the brief current, delegates bounded work, and owns verification plus stop/escalate calls.
- Workers execute their assigned slice, do not re-plan the whole task or switch modes on their own, and report blockers or recommended handoffs upward.
- Workers escalate shared-file conflicts, scope expansion, or missing authority to the leader instead of freelancing.

Stop / escalate:
- Stop when the task is verified complete, the user says stop/cancel, or no meaningful recovery path remains.
- Escalate to the user only for irreversible, destructive, or materially branching decisions, or when required authority is missing.
- Escalate from worker to leader for blockers, scope expansion, shared ownership conflicts, or mode mismatch.
- `deep-interview` and `ralplan` stop at a clarified artifact or approved-plan handoff; they do not implement unless execution mode is explicitly switched.
- In Commitfolio default flow, do not stop merely because planning artifacts were created; continue unless an approval gate was explicitly requested or a real blocker exists.

Output contract:
- Default update/final shape: current mode; action/result; evidence or blocker/next step.
- Keep rationale once; do not restate the full plan every turn.
- Expand only for risk, handoff, or explicit user request.

Parallelization:
- Run independent tasks in parallel.
- Run dependent tasks sequentially.
- Use background execution for builds and tests when helpful.
- Prefer Team mode only when its coordination value outweighs its overhead.
- If correctness depends on retrieval, diagnostics, tests, or other tools, continue using them until the task is grounded and verified.

Anti-slop workflow:
- Cleanup/refactor/deslop work still follows the same `$deep-interview` -> `$ralplan` -> `$team`/`$ralph` path; use `$ai-slop-cleaner` as a bounded helper inside the chosen execution lane, not as a competing top-level workflow.
- Lock behavior with tests first, then make one smell-focused pass at a time.
- Prefer deletion, reuse, and boundary repair over new layers.
- Keep writer/reviewer pass separation for cleanup plans and approvals.

Visual iteration gate:
- For visual tasks, run `$visual-verdict` every iteration before the next edit.
- Persist verdict JSON in `.omx/state/{scope}/ralph-progress.json`.

Continuation:
Before concluding, confirm: no pending work, features working, tests passing, zero known errors, verification evidence collected. If not, continue.

Ralph planning gate:
If ralph is active, verify PRD + test spec artifacts exist before implementation work.
</execution_protocols>

<cancellation>
Use the `cancel` skill to end execution modes.
Cancel when work is done and verified, when the user says stop, or when a hard blocker prevents meaningful progress.
Do not cancel while recoverable work remains.
</cancellation>

---

<state_management>
OMX persists runtime state under `.omx/`:
- `.omx/state/` — mode state
- `.omx/notepad.md` — session notes
- `.omx/project-memory.json` — cross-session memory
- `.omx/plans/` — plans
- `.omx/logs/` — logs

Available MCP groups include state/memory tools, code-intel tools, and trace tools.

Mode lifecycle requirements:
- Write state on start.
- Update state on phase or iteration change.
- Mark inactive with `completed_at` on completion.
- Clear state on cancel/abort cleanup.
</state_management>

---

## Setup

Run `omx setup` to install all components. Run `omx doctor` to verify installation.
