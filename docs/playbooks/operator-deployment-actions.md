# Operator Deployment / DB Action Checklist

이 문서는 Commitfolio 기능 개발 중 **사람이 직접 해야 하는 외부 콘솔 작업**을 정리한다. Codex/OMX는 코드, 문서, 검증, PR을 처리하지만, 결제/계정/secret/외부 서비스 생성은 사람 권한이 필요하다.

## 기본 원칙

- 기능 개발은 계속 `develop` 기준 PR로 진행한다.
- 새 OMX/Codex 개발 세션은 기본적으로 `omx --madmax`로 시작한다. 이미 full-access/equivalent 세션이면 재실행하지 않고 "madmax 규칙 충족"으로 보고한다.
- secret은 Git에 커밋하지 않는다. `.env`, Render, Vercel, Neon, GitHub OAuth 콘솔에만 둔다.
- 가능하면 secret 값을 채팅에 직접 붙이지 않는다. 사용자가 로컬 `.env` 또는 배포 콘솔에 직접 넣고, Codex에는 성공/실패 로그만 전달하는 방식을 우선한다.
- 단, 사용자가 임시 dev credential을 명시적으로 공유하면 Codex가 로컬 smoke를 대신 실행할 수 있다. 이 경우 작업 후 credential rotation을 권장한다.
- 배포/DB는 마지막에 처음 연결하지 않는다. 최소 한 번은 **Neon dev DB 로컬 smoke**를 먼저 통과시킨다.

## 역할 분담 요약

| 구간 | Codex/OMX가 하는 일 | 사용자가 하는 일 |
| --- | --- | --- |
| 기능 개발 | PRD/task 작성, 코드 구현, 테스트, PR 준비 | 제품 판단, secret/콘솔 권한 제공 여부 결정 |
| Neon DB 준비 | 필요한 env 이름/검증 명령 제공, migration smoke 실행 | Neon 프로젝트/DB 생성, connection string 확보 |
| Render backend | build/start/env 목록 제공, 배포 로그 분석 | Render 서비스 생성, env 입력, 필요 시 Shell/Manual Deploy 실행 |
| Vercel frontend | frontend env 이름 제공, 배포 오류 분석 | Vercel 프로젝트 생성, `VITE_API_BASE_URL` 입력 |
| GitHub OAuth | callback/env 값 검증, 코드 수정 | OAuth App callback URL/secret 관리 |
| Release | develop→main PR, 검증/위험 요약 | 최종 공개 여부/도메인/credential rotation 결정 |

## 단계별 사용자 액션

### Stage 7 이후: Neon dev DB 로컬 smoke

목표: production DB를 바로 배포에 붙이기 전에, 로컬 backend가 Neon/PostgreSQL로 migration과 핵심 API를 통과하는지 확인한다.

사용자가 할 일:

1. Neon 콘솔에서 Commitfolio용 프로젝트를 만든다.
2. `main` branch의 기본 database/role을 확인한다.
3. Connect 버튼에서 connection string을 복사한다.
4. Commitfolio backend가 SQLAlchemy psycopg URL을 사용하므로 URL scheme을 아래처럼 맞춘다.

```bash
# Neon이 제공하는 예시
postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require&channel_binding=require

# Commitfolio backend에 넣을 형태
postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require&channel_binding=require
```

5. 아래 둘 중 하나를 선택한다.

#### 옵션 A — 사용자가 직접 로컬 smoke 실행

```bash
cd /Users/donggun/Desktop/Commitfolio/apps/backend
cp .env.example .env
# .env의 DATABASE_URL을 Neon URL로 교체
.venv/bin/alembic upgrade head
DATABASE_URL='postgresql+psycopg://...' .venv/bin/uvicorn app.main:app --reload
curl http://localhost:8000/healthz
```

성공하면 Codex에게 다음을 알려준다.

```text
Neon 로컬 smoke 완료. alembic upgrade head 성공, /healthz 200 OK.
```

실패하면 secret을 제외한 에러 로그만 보낸다.

#### 옵션 B — Codex가 대신 smoke 실행

사용자가 임시 dev `DATABASE_URL`을 안전한 방식으로 제공하거나 로컬 `.env`에 직접 넣은 뒤 다음처럼 말한다.

```text
apps/backend/.env에 Neon DATABASE_URL 넣어놨음. migration smoke 돌려줘.
```

Codex가 실행할 검증:

```bash
cd apps/backend
set -a && source .env && set +a
.venv/bin/alembic upgrade head
.venv/bin/python - <<'PY'
from app.config import get_settings
from app.db import create_db_engine
engine = create_db_engine(get_settings().database_url)
with engine.connect() as conn:
    print(conn.exec_driver_sql('select 1').scalar())
PY
```

완료 기준:

- Alembic head migration 성공
- `select 1` 성공
- `/healthz` 200 OK
- 기존 SQLite 테스트도 계속 통과

### Stage 8 전후: Render backend preview 배포

목표: backend가 Render에서 뜨고 Neon DB/env/GitHub OAuth와 연결되는지 preview 수준으로 확인한다.

사용자가 할 일:

1. Render에서 New Web Service를 선택한다.
2. GitHub의 `Commitfolio/Commitfolio` repository를 연결한다.
3. Root Directory를 설정할 수 있으면 `apps/backend`로 설정한다.
4. Runtime/Language는 Python을 선택한다.
5. Build Command:

```bash
pip install -e .
```

6. Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

7. Environment에 아래 값을 입력한다.

```bash
GITHUB_CLIENT_ID=<GitHub OAuth App client id>
GITHUB_CLIENT_SECRET=<GitHub OAuth App client secret>
GITHUB_CALLBACK_URL=https://<render-backend>.onrender.com/api/v1/auth/github/callback
GITHUB_SCOPE=read:user repo read:org
FRONTEND_APP_URL=https://<vercel-frontend-url 또는 임시 로컬/preview URL>
BACKEND_CORS_ORIGIN=https://<vercel-frontend-url 또는 preview URL>
SESSION_SECRET=<32 bytes 이상 랜덤 문자열>
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require&channel_binding=require
```

Stage 7에서 OpenAI 후처리를 구현했다면 추가로 입력한다.

```bash
OPENAI_API_KEY=<optional>
OPENAI_MODEL=<구현에서 정한 기본값이 있으면 생략 가능>
OPENAI_TIMEOUT_SECONDS=<구현에서 정한 기본값이 있으면 생략 가능>
```

8. 첫 deploy 후 backend URL을 Codex에게 알려준다.

```text
Render backend URL: https://....onrender.com
```

Codex/OMX가 확인할 것:

```bash
curl https://<render-backend>.onrender.com/healthz
```

주의:

- 첫 공개 배포 전에는 migration 실행 전략을 확정해야 한다.
- MVP 임시 전략은 Render Shell/one-off command에서 `alembic upgrade head`를 실행하는 방식이다.
- 더 안전한 전략은 Stage 9에서 별도 migration command/job 또는 deploy 절차로 문서화한다.

### Stage 8 전후: Vercel frontend preview 배포

목표: frontend가 배포 backend를 바라보도록 연결한다.

사용자가 할 일:

1. Vercel에서 New Project를 선택한다.
2. GitHub의 `Commitfolio/Commitfolio` repository를 import한다.
3. Root Directory를 `apps/frontend`로 설정한다.
4. Build Command는 기본 또는 아래 값을 사용한다.

```bash
npm run build
```

5. Output Directory는 Vite 기본값인 `dist`를 사용한다.
6. Environment Variables에 아래 값을 넣는다.

```bash
VITE_API_BASE_URL=https://<render-backend>.onrender.com
```

7. 배포 URL을 Codex에게 알려준다.

```text
Vercel frontend URL: https://....vercel.app
```

Codex/OMX가 확인할 것:

- frontend 접속 가능 여부
- `VITE_API_BASE_URL`이 localhost가 아닌 Render URL인지
- GitHub OAuth start 링크가 Render backend를 향하는지

### GitHub OAuth App production callback 설정

목표: 배포된 frontend/backend에서 GitHub 로그인 callback이 맞게 돌아오도록 한다.

사용자가 할 일:

1. GitHub Developer settings의 OAuth App으로 이동한다.
2. Homepage URL을 Vercel frontend URL로 맞춘다.

```text
https://<vercel-frontend>.vercel.app
```

3. Authorization callback URL을 Render backend callback으로 맞춘다.

```text
https://<render-backend>.onrender.com/api/v1/auth/github/callback
```

4. client id/secret을 Render env에 넣는다.

Codex/OMX가 확인할 것:

- `GITHUB_CALLBACK_URL` env와 GitHub OAuth App callback URL이 같은지
- login → callback → frontend redirect → `/api/v1/me` 흐름이 성공하는지

주의:

- 현재 cross-site 배포에서는 session cookie 설정이 막힐 수 있다. 이 경우 Stage 9에서 `SameSite=None; Secure` 같은 production cookie config를 추가해야 한다.
- public launch 전에는 OAuth App 권한 안내와 broad `repo` scope 문구를 다시 검토한다.

### Stage 9: public MVP release

목표: preview smoke가 아니라 실제 공개 가능한 main 배포로 승격한다.

사용자가 할 일:

1. 공개에 사용할 최종 Vercel/Render/Neon 리소스를 확정한다.
2. 필요하면 custom domain을 정한다.
3. production env 값을 최종 점검한다.
4. 임시 dev secret을 썼다면 rotation한다.
5. Codex에게 배포를 요청한다.

```text
배포해줘. develop 기준으로 main release PR 열고, Render/Vercel/Neon 상태까지 확인해줘.
```

Codex/OMX가 할 일:

- `develop` 최신/clean 확인
- verification baseline 실행
- develop → main release PR 생성
- merge 가능한 checks 확인
- main merge 후 deployment pipeline 확인
- `/healthz`, frontend URL, OAuth smoke, DB migration 상태 보고

## 사용자가 Codex에게 전달하면 좋은 정보 템플릿

secret 값은 가능하면 빼고, URL/상태만 전달한다.

```text
Neon:
- project created: yes
- DATABASE_URL inserted locally/in Render: yes
- local alembic smoke: pass/fail

Render:
- backend URL: https://...
- env inserted: yes
- latest deploy status: pass/fail
- error log without secrets: ...

Vercel:
- frontend URL: https://...
- VITE_API_BASE_URL: https://...
- latest deploy status: pass/fail

GitHub OAuth:
- callback URL set to: https://.../api/v1/auth/github/callback
- login smoke: pass/fail
```

## 앞으로 기능 개발 브리핑에 반드시 포함할 사용자 액션 섹션

기능이 외부 서비스, secret, 배포, DB, OAuth, 결제/요금제, 도메인 설정을 건드리면 Codex는 구현 전에 짧게 아래를 포함한다.

```text
사용자가 해야 할 일:
1. <콘솔/계정 작업>
2. <필요한 env/secret 이름>
3. <Codex에게 알려줄 값 또는 로그>
4. <사용자가 직접 실행할 수 있는 검증 명령>
```

작업 완료 보고에도 아래를 포함한다.

```text
사용자 후속 액션:
- 지금 해야 하는 것:
- 나중에 Stage N에서 해야 하는 것:
- secret rotation/배포 콘솔 확인 필요 여부:
```

## 공식 참고 문서

- Render FastAPI 배포: https://render.com/docs/deploy-fastapi
- Render 환경변수/secret: https://render.com/docs/configure-environment-variables
- Neon connection string: https://neon.com/docs/connect/connect-from-any-app
- Vercel environment variables: https://vercel.com/docs/environment-variables
- GitHub OAuth redirect URL: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#redirect-urls
