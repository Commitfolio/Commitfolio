# 백엔드 코드 아키텍처와 Python 양식 가이드

이 문서는 `apps/backend`의 현재 FastAPI 구조와 앞으로 기능을 추가할 때 지켜야 할 레이어 경계를
고정한다. Commitfolio 백엔드는 FastAPI에서 흔히 쓰는 **Presentation(router/controller) / Service /
Repository(Persistence) / Entity** 구조를 따른다. 기준 참고 문서는 Velog의
[FastAPI 레이어드 아키텍처(Layered Architecture)](https://velog.io/@byu0hyun/FastAPI-%EB%A0%88%EC%9D%B4%EC%96%B4%EB%93%9C-%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98Layered-Architecture)이며,
해당 글의 핵심 원칙인 router-service-repository 분리와 `Depends()` 기반 dependency wiring을
Commitfolio의 동기 SQLAlchemy 환경에 맞춰 적용한다.

## 2026-04-15 Stage 4 이후 적용 결과

### 결론

- 추적 중인 `apps/backend/**/*.py` 파일은 모두 실제 Python 소스이며 문법 컴파일에 성공했다.
- 추적 중인 Python 파일의 Git mode는 모두 `100644`라서 실행 파일로 잘못 추적된 상태도 아니다.
- 현재 `apps/backend/.venv`에는 `pyproject.toml`의 런타임/개발 의존성이 설치되어 있다.
- `pip check` 기준 깨진 의존성은 없다.
- 백엔드 테스트는 현재 17개 모두 통과한다.
- `app/main.py`는 앱 조립 파일로 축소했고, 기존 route/schema/use case/SSE helper는 아래 레이어로
  분리했다.
- route가 DB `Session`을 직접 주입받아 쓰던 경계를 제거하고, `api/dependencies.py`가 repository와
  service 생성을 관리하도록 바꿨다.
- analysis job DB 접근은 `app/repositories/analysis_jobs.py`로 이동했다.
- 남은 구조 부채는 `app/github_oauth.py`에 OAuth, repository listing, evidence 수집/디코딩이 아직
  같이 있다는 점이다. 다음 기능 또는 cleanup에서 `integrations/github/`로 추가 분리한다.

### 확인한 명령

```bash
cd apps/backend
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q -p no:cacheprovider
```

```bash
PYTHONDONTWRITEBYTECODE=1 apps/backend/.venv/bin/python - <<'PY'
from pathlib import Path
import subprocess

result = subprocess.run(
    ["git", "ls-files", "apps/backend/*.py", "apps/backend/**/*.py"],
    check=True,
    text=True,
    capture_output=True,
)

for line in result.stdout.splitlines():
    path = Path(line)
    compile(path.read_text(), str(path), "exec")
    print(f"{path}: OK")
PY
```

### 로컬 생성물 주의

아래 경로들은 개발 중 생성되지만 제품 코드로 읽으면 안 된다.

- `apps/backend/.venv/`
- `apps/backend/.pytest_cache/`
- `apps/backend/build/`
- `apps/backend/*.egg-info/`
- `__pycache__/`
- `*.pyc`

루트 `.gitignore`에는 위 경로들이 제외되어 있다. IDE에서 이 파일들이 보이면 Python 코드가
이상해진 것처럼 보일 수 있지만, 현재 추적 중인 제품 Python 파일에는 해당 문제가 없다.

## 현재 백엔드 모듈 지도

| 경로 | 레이어 | 현재 역할 |
| --- | --- | --- |
| `app/main.py` | app composition | FastAPI app factory, middleware, lifespan, router registration, `/healthz`만 담당한다. |
| `app/api/routes/auth.py` | controller/router | GitHub OAuth start/callback, `/me`, logout HTTP 입출력. |
| `app/api/routes/repositories.py` | controller/router | repository listing HTTP 입출력. |
| `app/api/routes/analysis_jobs.py` | controller/router | analysis job create/status/run/evidence HTTP 입출력. |
| `app/api/routes/analysis_events.py` | controller/router | SSE event stream HTTP 입출력. |
| `app/api/schemas.py` | schema | Pydantic request/response/error model. |
| `app/api/dependencies.py` | dependency wiring | FastAPI `Depends()` provider. Repository와 service 객체 생성을 관리한다. |
| `app/api/responses.py` | HTTP helper | error envelope, frontend redirect URL helper. |
| `app/services/analysis_jobs.py` | service/use case | analysis job/evidence business flow와 response mapping. |
| `app/services/analysis_events.py` | service/use case | SSE cursor parsing, event formatting, event replay stream. |
| `app/repositories/analysis_jobs.py` | repository/persistence | analysis job, evidence, event DB read/write. |
| `app/github_oauth.py` | integration, pending split | GitHub OAuth, profile/repository lookup, evidence API calls and decode. |
| `app/models.py` | entity/persistence | SQLAlchemy entity models, ID/time helper. |
| `app/db.py` | persistence wiring | engine/session factory, DB init, FastAPI DB dependency. |
| `app/config.py` | configuration | 환경 변수 기반 settings. |
| `migrations/` | persistence migration | Alembic migration. |
| `tests/test_auth.py` | regression tests | auth, repository, analysis job, evidence, SSE route contract 테스트. |

## 현재 디렉터리 구조

```text
apps/backend/app/
  main.py                     # create_app, middleware, router registration only
  config.py                   # Settings
  db.py                       # engine/session dependency
  models.py                   # SQLAlchemy models
  github_oauth.py             # GitHub integration; 다음 cleanup에서 추가 분리 후보
  api/
    dependencies.py           # FastAPI Depends providers; service/repository wiring
    responses.py              # common HTTP response helpers
    schemas.py                # Pydantic schemas
    routes/
      auth.py                 # /auth, /me
      repositories.py         # /repositories
      analysis_jobs.py        # job create/status/run/evidence
      analysis_events.py      # SSE/event replay
  services/
    analysis_jobs.py          # analysis job + evidence use cases
    analysis_events.py        # SSE replay use cases
  repositories/
    analysis_jobs.py          # DB read/write persistence layer
```

## 레이어 규칙

### `main.py`

- 앱 조립만 담당한다.
- 유지할 책임:
  - `create_app()`
  - middleware 등록
  - router 등록
  - lifespan 등록
  - `/healthz`
- 신규 route, schema, business flow를 직접 추가하지 않는다.

### `api/routes/*`

FastAPI의 Presentation/controller layer다. Django/Java식 `Controller` 이름 대신 보통 `router` 또는
`route`라고 부른다.

- 허용 책임:
  - request/session 확인
  - query/body validation 연결
  - service 호출
  - response/status code 반환
- 금지 책임:
  - DB `Session` 직접 주입/조작
  - Repository 직접 호출
  - GitHub API payload decode
  - DB row 생성 규칙 직접 구현
  - 긴 orchestration

### `api/schemas.py`

- Pydantic request/response model만 둔다.
- SQLAlchemy model과 API schema를 섞지 않는다.
- 파일이 커지면 `api/schemas/` 패키지로 나누되, 외부 API shape 변경은
  `docs/architecture/api-contract.md`를 먼저 업데이트한다.

### `services/*`

- 제품 use case와 business flow를 담당한다.
- FastAPI `Request` 객체에 직접 의존하지 않는다.
- DB `Session` 대신 repository 객체를 입력으로 받는다.
- GitHub 같은 외부 integration client는 service method의 명시적 입력으로 받는다.
- transaction 경계가 필요한 경우 repository의 `commit()`/`refresh()`를 호출하되, route에는 노출하지 않는다.

### `repositories/*`

- DB read/write persistence layer다.
- SQLAlchemy query와 `Session` 조작은 이 레이어에 둔다.
- API schema를 반환하지 않고 SQLAlchemy entity 또는 primitive data를 반환한다.
- 비즈니스 판단은 service에 둔다.

### `integrations/github/*` 또는 `github_oauth.py`

- GitHub OAuth와 GitHub REST API 호출만 담당한다.
- 제품 DB model을 import하지 않는다.
- 외부 API 실패는 route/service에서 제품 error envelope으로 바꿀 수 있는 typed error로 올린다.
- 현재는 `github_oauth.py` 한 파일이지만, 다음 cleanup에서 `integrations/github/` 패키지로 분리한다.

### `models.py`

- persistence 구조만 담당한다.
- business rule이 길어지면 service/domain helper로 옮긴다.

## Python 코드 양식

### 파일 기본

- 신규 Python 파일은 `from __future__ import annotations`로 시작한다.
- import는 표준 라이브러리, third-party, local 순서로 묶는다.
- Python 3.9 지원을 유지하는 동안 nullable type은 `Optional[T]`를 기본으로 쓴다.

### FastAPI route

- route handler는 30~80줄 안쪽을 목표로 한다.
- 길어지는 orchestration은 service로 이동한다.
- 공통 error envelope 형식은 유지한다.

```json
{
  "error": {
    "code": "machine_readable_code",
    "message": "Human readable message."
  }
}
```

### SQLAlchemy

- SQLAlchemy 2.x `Mapped[...]`, `mapped_column(...)` 패턴을 유지한다.
- model 변경은 Alembic migration과 같이 간다.
- `analysis_jobs`는 최신 상태 snapshot이고, `analysis_job_events`는 SSE replay source of truth다.

### GitHub integration

- GitHub REST endpoint별 decode 함수는 integration layer에 둔다.
- OAuth scope 변경은 PRD 또는 architecture 문서에 반드시 남긴다.
- GitHub private repository 접근은 현재 OAuth App의 `repo` scope tradeoff를 유지하되,
  public MVP 전에는 GitHub App/fine-grained permission 대안을 다시 검토한다.

### 테스트

- route contract 테스트와 service 단위 테스트를 점진 분리한다.
- 외부 GitHub 호출은 mock/fake client로 고정한다.
- 신규 DB table은 migration smoke와 pytest를 같이 검증한다.

## 의존성 관리

공식 의존성 소스는 `apps/backend/pyproject.toml`이다.

새 패키지가 필요할 때는 다음 순서로 처리한다.

1. 표준 라이브러리나 기존 패키지로 해결 가능한지 먼저 확인한다.
2. 정말 필요하면 `apps/backend/pyproject.toml`에 좁은 버전 범위로 추가한다.
3. 개발 환경을 다시 설치하고 의존성 검증을 실행한다.

```bash
cd apps/backend
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pip check
```

현재 점검 기준으로는 누락 설치된 런타임 패키지가 보이지 않는다. 단, pip가 사용자 cache에 쓰지
못한다는 경고가 나올 수 있는데 이는 패키지 누락이 아니라 로컬 cache 권한 문제다.

## 다음 리팩터링 후보

이번 pass는 `main.py` 비대화 해소와 controller/service/schema/SSE helper 분리에 집중했다. 다음
cleanup은 아래 순서로 작게 진행한다.

1. `app/github_oauth.py`를 `integrations/github/oauth.py`, `client.py`, `repositories.py`,
   `evidence.py`로 분리한다.
2. `tests/test_auth.py`를 route/use case별 테스트 파일로 나눈다.
3. `app/api/schemas.py`가 더 커지면 `api/schemas/` 패키지로 분리한다.
4. Stage 5 결과 생성 기능은 처음부터 `api/routes/results.py`, `services/results.py`,
   `repositories/results.py` 경계로 추가한다.

각 단계는 독립 커밋으로 만들고 최소 검증은 아래를 통과해야 한다.

```bash
cd apps/backend
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
```
