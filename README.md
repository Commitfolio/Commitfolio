# Commitfolio

Commitfolio는 GitHub 활동을 **근거 링크가 살아있는 포트폴리오 문서**로 바꿔주는 서비스입니다.
사용자는 GitHub OAuth로 접근 가능한 **public / private / organization repository** 중 하나를 선택하고,
해당 프로젝트의 commit / PR / issue / review / changed files 데이터를 바탕으로
편집 가능한 포트폴리오 초안을 생성할 수 있습니다.

현재 목표는 **공개 가능한 MVP**를 완성하는 것입니다. 규칙 기반 결과 생성이 기본값이며,
선택적으로 OpenAI 후처리를 붙여 문장 품질을 높일 수 있습니다.

## 현재 MVP 흐름

1. GitHub OAuth로 로그인
2. 접근 가능한 저장소 목록 조회
3. 저장소 하나를 선택해 분석 작업 생성/실행
4. 실시간 진행 상태와 근거 요약 확인
5. 포트폴리오 결과 생성, 수정, PDF 저장

## 저장소 구조

```text
apps/
  frontend/   React + Vite + TypeScript
  backend/    FastAPI
docs/
  prd/        기능 PRD
  tasks/      실행 체크리스트 및 검증 기록
scripts/
  deployment/ preview / release helper
```

## Quick start

### 1) Backend 실행

```bash
cd apps/backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

기본 backend 주소는 `http://localhost:8000`입니다.

### 2) Frontend 실행

```bash
cd apps/frontend
npm install
cp .env.example .env
npm run dev
```

기본 frontend 주소는 `http://localhost:5173`입니다.

## 핵심 환경 변수

### Backend (`apps/backend/.env`)

- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_CALLBACK_URL`
- `GITHUB_SCOPE`
- `FRONTEND_APP_URL`
- `BACKEND_CORS_ORIGIN`
- `SESSION_SECRET`
- `SESSION_COOKIE_SAME_SITE`
- `SESSION_COOKIE_SECURE`
- `DATABASE_URL`
- `OPENAI_API_KEY` *(optional)*
- `OPENAI_MODEL` *(optional)*
- `OPENAI_TIMEOUT_SECONDS` *(optional)*
- `LOG_LEVEL`

### Frontend (`apps/frontend/.env`)

- `VITE_API_BASE_URL`

## 권한 / 개인정보 / 지원 범위

- 로그인 직후에는 접근 가능한 저장소의 **메타데이터만 먼저** 조회합니다.
- 실제 분석은 사용자가 **직접 선택한 저장소 하나**에 대해서만 실행합니다.
- private repository 조회를 위해 현재 OAuth App은 GitHub의 넓은 `repo` scope를 사용합니다.
- organization repository가 보이지 않으면 해당 조직의 **OAuth App access 승인**이 필요할 수 있습니다.
- 세션은 backend 쿠키로 유지되며, 서버 재시작이나 세션 만료 시 다시 로그인해야 할 수 있습니다.

> 이 저장소는 MVP 기준 안내를 제공합니다. 법률 문서 수준의 privacy policy를 대체하지는 않습니다.

## Preview / public release readiness

Stage 9 기준으로 공개 배포 전에는 아래를 확인해야 합니다.

### Preview smoke

```bash
scripts/deployment/preview_smoke.py \
  --mode preview \
  --backend-url http://localhost:8000 \
  --frontend-url http://localhost:5173 \
  --report-json .omx/reports/local-preview-smoke.json
```

실제 Render / Vercel preview URL이 준비되면 외부 URL로 다시 실행합니다.
배포 증적을 남기려면 `--report-json`으로 구조화된 결과를 저장합니다.

### Release smoke artifact

```bash
scripts/deployment/preview_smoke.py \
  --mode release \
  --backend-url https://<render-backend>.onrender.com \
  --frontend-url https://<vercel-frontend>.vercel.app \
  --expected-frontend-api-base https://<render-backend>.onrender.com \
  --report-json .omx/reports/release-smoke.json
```

release smoke report에는 다음이 포함됩니다.

- backend health
- unauthenticated `/api/v1/me` contract와 `X-Request-ID`
- GitHub OAuth start redirect
- frontend app shell
- CORS preflight
- frontend runtime API base
- 다음 운영 액션 힌트

### 운영자 참고 문서

- Stage 9 roadmap: `docs/prd/mvp-feature-roadmap.md`
- Stage 9 baseline PRD: `docs/prd/mvp-hardening.md`
- Preview smoke PRD: `docs/prd/preview-deployment-smoke.md`
- Operator playbook: `docs/playbooks/operator-deployment-actions.md`
- Backend env / cookie / OAuth 참고: `apps/backend/README.md`

### 외부 콘솔 사용자 액션

아래 작업은 저장소 안에서 자동으로 완료되지 않습니다.

- Render backend env 반영
- Vercel frontend env 반영
- GitHub OAuth callback URL 설정
- Neon production/preview DB 연결
- 필요 시 custom domain / release PR 운영

## 샘플 검증 시나리오

공개 MVP 전 최소 한 번은 아래 케이스를 확인합니다.

### Public repository

- 로그인 후 저장소 목록에서 조회 가능
- 분석 작업 생성 / 실행 / 결과 생성이 정상 동작
- empty state 없이 결과를 확인 가능

### Private repository

- `repo` scope가 포함된 로그인으로 목록 조회 가능
- 결과 생성까지 세션이 유지됨
- 세션 유실 시 재로그인 안내가 정상 노출됨

### Organization repository

- 조직 승인된 계정에서는 목록/직접 조회가 가능
- 미승인 상태에서는 권한 안내 또는 접근 불가 메시지가 명확함
- permission failure copy가 사용자 행동(재로그인, 승인 요청)을 안내함
- release 전에는 위 세 케이스의 결과를 smoke report와 함께 기록함

## 데모 흐름

1. GitHub로 로그인
2. public 또는 private 저장소를 하나 선택
3. 분석 작업 생성
4. 분석 실행 후 evidence summary 확인
5. 포트폴리오 결과 생성
6. 결과 문장 수정
7. PDF 저장 또는 인쇄

## 품질 검증 명령

```bash
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run typecheck
npm --prefix apps/frontend run test -- --run
npm --prefix apps/frontend run build

cd apps/backend && .venv/bin/python -m pytest tests
git diff --check
```

## 관련 문서

- `docs/prd/mvp-feature-roadmap.md`
- `docs/tasks/mvp-feature-roadmap.md`
- `docs/prd/mvp-hardening.md`
- `docs/tasks/mvp-hardening.md`
- `docs/playbooks/operator-deployment-actions.md`
