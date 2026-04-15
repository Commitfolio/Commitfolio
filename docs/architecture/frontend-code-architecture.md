# 프론트엔드 코드 아키텍처와 React 양식 가이드

Commitfolio 프론트엔드는 React + Vite + TypeScript 기반이며, MVP 속도를 유지하면서도 `App.tsx`가
모든 책임을 끌어안지 않도록 **가벼운 Feature-Sliced Architecture**를 따른다.

React에는 FastAPI처럼 하나의 공식 레이어드 아키텍처가 정해져 있지 않다. Commitfolio에서는
기능 단위로 UI와 상태 흐름을 찾기 쉽게 만드는 feature-sliced 구조를 기본으로 하고, 서버 상태
라이브러리나 라우터는 실제 필요가 생기는 Stage에서 도입한다.

## 적용 원칙

- `app/`: 앱 조립, provider, router, root layout만 담당한다.
- `features/`: 사용자가 수행하는 행동 단위 UI와 해당 feature 전용 helper를 둔다.
- `entities/`: API/domain entity type과 entity-level helper를 둔다.
- `shared/`: 공용 API client, UI primitive, config, formatting helper를 둔다.
- `App.tsx`는 호환 re-export만 유지하고 실제 구현은 `app/App.tsx`에 둔다.
- 새 dependency는 기능 PR에서 명시적으로 필요할 때만 추가한다.
- Stage 5 결과 기능은 처음부터 `features/result-viewer`, `entities/portfolio-result`,
  `shared/api` 경계를 따른다.

## 현재 구조

```text
apps/frontend/src/
  App.tsx                         # compatibility re-export
  app/
    App.tsx                       # root composition and page-level orchestration
  entities/
    analysis-job/
      analysis-job.types.ts
    repository/
      repository.types.ts
    session/
      session.types.ts
  features/
    github-auth/
      auth-status.ts
      SessionPanel.tsx
    repository-selector/
      RepositorySelector.tsx
      useRepositorySelector.ts
    analysis-job/
      AnalysisJobPanel.tsx
      useAnalysisJobFlow.ts
    analysis-progress/
      progress-stream.ts
  shared/
    api/
      commitfolio-api.ts
  lib/
    api.ts                        # compatibility re-export to shared/api
  main.tsx
  styles.css
```

## 레이어 규칙

### `app/`

- 앱 조립과 page-level orchestration을 담당한다.
- provider, router, layout이 생기면 이 레이어에 둔다.
- feature 내부 markup과 entity-specific helper가 길어지면 `features/` 또는 `entities/`로 이동한다.

### `features/`

- 사용자 행동 단위의 UI와 feature 전용 helper를 둔다.
- 예: GitHub 로그인 상태, repository 선택, analysis job 실행, SSE 진행 상태, result viewer.
- feature가 공용 API client를 직접 호출할 수는 있지만, 여러 feature에서 공유되는 호출은
  `shared/api`로 이동한다.
- feature 상태와 side effect가 길어지면 `use<FeatureName>` hook으로 분리하고, component는 markup과
  event props 중심으로 유지한다.
- feature 간 직접 import는 피하고, 공통 type/helper는 `entities/` 또는 `shared/`로 올린다.

### `entities/`

- Repository, AnalysisJob, Evidence, PortfolioResult처럼 제품 도메인 명사 단위 type을 둔다.
- API response type을 재사용하되, UI 표시 규칙이 복잡해지면 entity helper로 분리한다.

### `shared/`

- 제품 전반에서 공유되는 API client, config, UI primitive, formatting helper를 둔다.
- feature-specific 상태나 markup은 shared로 올리지 않는다.

### `lib/`

- 기존 import 호환을 위한 얇은 re-export만 허용한다.
- 신규 코드는 `shared/`를 직접 import한다.

## API와 서버 상태

현재는 새 dependency 없이 `fetch` 기반 API client를 유지한다.

- 공용 API client: `shared/api/commitfolio-api.ts`
- 기존 호환 경로: `lib/api.ts`

로드맵에는 TanStack Query와 React Router가 예정되어 있지만, 현재 `package.json`에는 아직 설치하지
않았다. Stage 5 이후 results 목록/상세/편집/재생성 흐름이 복잡해지면 별도 PR에서 도입한다.

도입 시 기준:

- React Router: 실제 페이지 URL이 2개 이상 필요할 때 도입한다.
- TanStack Query: 결과 목록/상세/재생성처럼 캐싱과 invalidation이 명확해질 때 도입한다.

## 테스트 규칙

- 기존 사용자-visible text와 button label은 회귀 테스트에 의존하므로 이유 없이 바꾸지 않는다.
- feature를 분리해도 `App.test.tsx`의 critical path 테스트는 계속 통과해야 한다.
- feature별 테스트가 늘어나면 `features/<name>/*.test.tsx`로 분리한다.

## 다음 기능 추가 기준

Stage 5 — Portfolio result generation + view는 아래 구조로 시작한다.

```text
src/features/result-viewer/
  ResultDocument.tsx
  ResultEvidenceLinks.tsx
  useResultViewer.ts
src/entities/portfolio-result/
  portfolio-result.types.ts
src/shared/api/commitfolio-api.ts   # results API 함수 추가
```

편집 기능이 시작되면 다음 구조를 추가한다.

```text
src/features/result-editor/
  ResultEditor.tsx
```

최근 결과 목록 또는 상세 URL이 필요해지면 React Router 도입 PR에서 `pages/` 레이어를 추가한다.
