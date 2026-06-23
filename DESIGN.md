# Design

## Source of truth
- Status: Active
- Last refreshed: 2026-06-23
- Primary product surfaces: landing shell, GitHub auth entry, repository selection, analysis progress, portfolio result viewer/editor
- Evidence reviewed:
  - `apps/frontend/src/app/App.tsx`
  - `apps/frontend/src/features/github-auth/SessionPanel.tsx`
  - `apps/frontend/src/features/repository-selector/RepositorySelector.tsx`
  - `apps/frontend/src/features/analysis-job/AnalysisJobPanel.tsx`
  - `apps/frontend/src/features/result-viewer/ResultDocument.tsx`
  - `apps/frontend/src/features/result-editor/ResultEditor.tsx`
  - `apps/frontend/src/styles.css`
  - `docs/prd/stitch-frontend-ui.md`
  - deployed UI at `https://commitfolio.vercel.app/` reviewed on 2026-06-23
  - preview UI at `https://commitfolio-k264n7ust-dongguli08s-projects.vercel.app/` reviewed on 2026-06-23

## Brand
- Personality: calm, credible, editorial, productized
- Trust signals: restrained color use, clear section titles, explicit next actions, evidence-oriented copy
- Avoid: oversized hero typography, visually identical action buttons, operator/debug copy in the main user flow, hard-sell SaaS styling

## Product goals
- Goals:
  - First-time visitors should understand the product in one scan.
  - Signed-in users should know the next recommended action without reading long paragraphs.
  - Core steps should feel like one guided flow instead of disconnected cards.
  - Generated portfolio results should read like concrete project outcomes, not commit log summaries.
- Non-goals:
  - Full rebrand or new product positioning
  - Backend/API/auth behavior changes
  - New routes or state-management architecture
- Success signals:
  - Primary CTA is visually unambiguous in signed-out and signed-in states.
  - Panel hierarchy remains readable on desktop and mobile.
  - Existing critical-path tests still pass with minimal text churn.

## Personas and jobs
- Primary personas: developers turning one GitHub repository into a portfolio-ready narrative
- User jobs:
  - connect GitHub safely
  - choose the right repository quickly
  - run analysis and understand progress
  - refine and export the generated result
- Key contexts of use: laptop-first, short evaluation sessions, portfolio prep before interviews or applications

## Information architecture
- Primary navigation: lightweight anchors to repository selection and portfolio result
- Core routes/screens: single-screen app shell with stepwise panels
- Content hierarchy:
  - product promise
  - immediate next action
  - guided workflow steps
  - operational details only when context requires them

## Design principles
- Principle 1: Reduce noise before adding emphasis.
- Principle 2: One panel, one decision. Each panel should surface a primary action and demote everything else.
- Principle 3: Product trust comes from consistency, not decoration.
- Principle 4: Result content must privilege interpreted contribution over raw evidence listing.
- Tradeoffs:
  - Keep expressive hero language, but cap scale to preserve readability.
  - Preserve existing Korean user-visible strings where tests depend on them.

## Visual language
- Color: warm neutral surfaces with restrained blue reserved for recommended actions and status accents
- Typography: strong but controlled display headlines, stable body copy, improved line-height
- Spacing/layout rhythm: wider panel padding, tighter vertical stacks, consistent action clusters
- Shape/radius/elevation: soft cards, low-contrast borders, moderate shadows only on key surfaces
- Motion: subtle hover lift only for interactive cards/buttons
- Imagery/iconography: no new illustration assets; rely on badges, section labels, and timeline motifs

## Components
- Existing components to reuse: existing `panel`, `button`, `badge`, repository cards, result document sections
- New/changed components:
  - hero supporting CTA row
  - action clusters with clear primary/secondary/quiet variants
  - contextual support cards for signed-out and signed-in states
  - optional environment note hidden from production flow
  - result summary header that surfaces project type, contribution density, and evidence confidence
  - richer result sections that separate "무엇을 만들었는가", "어떻게 만들었는가", "왜 중요한가"
- Variants and states:
  - `button primary`: recommended next step
  - `button secondary`: meaningful but non-primary action
  - `button tertiary`: maintenance/utility actions
  - `button danger`: sign-out/destructive-adjacent action
- Token/component ownership: keep repo-local CSS tokens in `apps/frontend/src/styles.css`

## Accessibility
- Target standard: practical WCAG AA-level readability and focus visibility
- Keyboard/focus behavior: preserve existing button/link semantics and visible focus rings
- Contrast/readability: avoid low-contrast gray-on-white; reduce giant text blocks
- Screen-reader semantics: keep current headings, labels, aria-live status, and action names
- Reduced motion and sensory considerations: hover motion should remain subtle and non-essential

## Responsive behavior
- Supported breakpoints/devices: desktop first, mobile fallback at current single-column breakpoint
- Layout adaptations: hero stacks vertically; action rows wrap; panel controls become full-width where needed
- Touch/hover differences: card hover should not be required to understand selection state

## Interaction states
- Loading: concise inline status without dominating the screen
- Empty: contextual empty cards that explain the next decision
- Error: visible but contained notice blocks near the affected area
- Success: badges/notices should confirm state without competing with the primary CTA
- Disabled: disabled buttons must look intentionally unavailable, not broken
- Offline/slow network, if applicable: refresh and recovery actions stay visible in analysis/result panels

## Content voice
- Tone: calm, direct, evidence-based
- Terminology: keep Korean product copy, allow GitHub/API terms where clearer
- Microcopy rules: explain why a user would take an action, not just what the action is called
- Result-writing rules:
  - Never describe a contribution as merely "근거를 남겼습니다."
  - Prefer "어떤 기능/플로우를 구현했고, 어떤 기술/모듈을 다뤘는지"가 먼저 보이게 쓴다.
  - Raw evidence titles are support, not the final narrative.
  - Tech stack should infer framework/domain concepts before fallbacking to file extensions.

## Implementation constraints
- Framework/styling system: React + Vite + TypeScript, single global CSS file
- Design-token constraints: no new dependency or design-system package
- Performance constraints: visual changes should remain CSS-first
- Compatibility constraints: existing frontend tests rely on several current labels
- Test/screenshot expectations: lint, typecheck, vitest, build, and before/after screenshot review on local + deployed flows

## Open questions
- [ ] Preview deployment URL의 세션/상태 이상이 stale build인지 cross-site/session 문제인지 최종 배포 후 다시 확인해야 한다.
