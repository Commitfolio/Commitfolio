from __future__ import annotations

import json
from typing import Optional

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.db import init_db
from app.github_oauth import (
    GitHubEvidenceItem,
    GitHubOAuthError,
    GitHubRepository,
    GitHubRepositoryPage,
)
from app.main import create_app, get_github_service


class FakeGitHubService:
    def is_configured(self) -> bool:
        return True

    def build_authorize_url(self, state: str) -> str:
        return f"https://github.example/login?state={state}"

    async def exchange_code(self, code: str) -> str:
        assert code == "test-code"
        return "access-token"

    async def fetch_user(self, access_token: str):
        assert access_token == "access-token"
        return type(
            "GitHubUser",
            (),
            {
                "id": 123,
                "login": "octocat",
                "name": "The Octocat",
                "avatar_url": "https://avatars.example/octocat.png",
            },
        )()

    async def fetch_repositories(
        self,
        access_token: str,
        *,
        visibility: str = "all",
        cursor: Optional[str] = None,
    ) -> GitHubRepositoryPage:
        assert access_token == "access-token"
        assert visibility == "all"
        assert cursor is None
        return GitHubRepositoryPage(
            items=[
                GitHubRepository(
                    id=456,
                    full_name="octocat/commitfolio",
                    private=True,
                    owner_type="Organization",
                    default_branch="main",
                    permissions={"admin": False, "push": True, "pull": True},
                    html_url="https://github.com/octocat/commitfolio",
                    description="Portfolio generator",
                    updated_at="2026-04-15T00:00:00Z",
                )
            ],
            next_cursor=None,
        )


    async def fetch_repository_by_full_name(
        self,
        access_token: str,
        *,
        full_name: str,
    ) -> GitHubRepository:
        assert access_token == "access-token"
        assert full_name == "SERVICE-MOHAENG/Mohaeng-BE"
        return GitHubRepository(
            id=789,
            full_name="SERVICE-MOHAENG/Mohaeng-BE",
            private=True,
            owner_type="Organization",
            default_branch="develop",
            permissions={"admin": False, "push": True, "pull": True},
            html_url="https://github.com/SERVICE-MOHAENG/Mohaeng-BE",
            description="Mohaeng backend",
            updated_at="2026-04-17T00:00:00Z",
        )

    async def collect_repository_evidence(
        self,
        access_token: str,
        *,
        full_name: str,
        branch: str,
    ) -> list[GitHubEvidenceItem]:
        assert access_token == "access-token"
        assert full_name == "octocat/commitfolio"
        assert branch == "main"
        return [
            GitHubEvidenceItem(
                source_type="commit",
                source_id="abc123",
                url="https://github.com/octocat/commitfolio/commit/abc123",
                payload={"sha": "abc123", "message": "Initial commit"},
            ),
            GitHubEvidenceItem(
                source_type="pull_request",
                source_id="7",
                url="https://github.com/octocat/commitfolio/pull/7",
                payload={"number": 7, "title": "Add API"},
            ),
            GitHubEvidenceItem(
                source_type="issue",
                source_id="8",
                url="https://github.com/octocat/commitfolio/issues/8",
                payload={"number": 8, "title": "Track work"},
            ),
            GitHubEvidenceItem(
                source_type="review",
                source_id="7:11",
                url="https://github.com/octocat/commitfolio/pull/7#pullrequestreview-11",
                payload={"pull_number": 7, "review_id": 11},
            ),
            GitHubEvidenceItem(
                source_type="changed_file",
                source_id="7:apps/backend/app/main.py",
                url="https://github.com/octocat/commitfolio/blob/main/apps/backend/app/main.py",
                payload={"pull_number": 7, "filename": "apps/backend/app/main.py"},
            ),
        ]


class FakeOpenAIResponse:
    def __init__(self, payload: dict, *, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "OpenAI error",
                request=httpx.Request("POST", "https://api.openai.com/v1/responses"),
                response=httpx.Response(self.status_code),
            )

    def json(self) -> dict:
        return self.payload


class FakeOpenAIClient:
    def __init__(self, response: FakeOpenAIResponse) -> None:
        self.response = response
        self.seen_json: Optional[dict] = None
        self.seen_headers: Optional[dict] = None

    def __enter__(self) -> "FakeOpenAIClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def post(self, url: str, **kwargs) -> FakeOpenAIResponse:
        assert url == "https://api.openai.com/v1/responses"
        self.seen_json = kwargs["json"]
        self.seen_headers = kwargs["headers"]
        return self.response


def create_test_client(*, openai_api_key: str = "", openai_model: str = "gpt-4.1-mini") -> TestClient:
    app = create_app(
        Settings(
            github_client_id="test-client-id",
            github_client_secret="test-client-secret",
            github_callback_url="http://testserver/api/v1/auth/github/callback",
            frontend_app_url="http://frontend.test",
            session_secret="test-session-secret",
            cors_origin="http://frontend.test",
            database_url="sqlite+pysqlite:///:memory:",
            openai_api_key=openai_api_key,
            openai_model=openai_model,
        )
    )
    init_db(app.state.db_engine)
    app.dependency_overrides[get_github_service] = lambda: FakeGitHubService()
    return TestClient(app)


def test_github_start_redirects_and_persists_state() -> None:
    client = create_test_client()

    response = client.get("/api/v1/auth/github/start", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"].startswith("https://github.example/login?state=")


def test_github_start_redirects_to_frontend_when_backend_is_not_configured() -> None:
    class UnconfiguredGitHubService(FakeGitHubService):
        def is_configured(self) -> bool:
            return False

    app = create_app(
        Settings(
            github_callback_url="http://testserver/api/v1/auth/github/callback",
            frontend_app_url="http://frontend.test",
            session_secret="test-session-secret",
            cors_origin="http://frontend.test",
            database_url="sqlite+pysqlite:///:memory:",
        )
    )
    init_db(app.state.db_engine)
    app.dependency_overrides[get_github_service] = lambda: UnconfiguredGitHubService()
    client = TestClient(app)

    response = client.get("/api/v1/auth/github/start", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "http://frontend.test/?auth_error=backend_not_configured"


def test_callback_creates_session_and_me_returns_user() -> None:
    client = create_test_client()

    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    location = start_response.headers["location"]
    state = location.split("state=")[1]

    callback_response = client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    assert callback_response.status_code == 302
    assert callback_response.headers["location"] == "http://frontend.test/?auth=success"

    me_response = client.get("/api/v1/me")

    assert me_response.status_code == 200
    assert me_response.json() == {
        "id": "github:123",
        "github_login": "octocat",
        "connected": True,
        "name": "The Octocat",
        "avatar_url": "https://avatars.example/octocat.png",
    }


def test_callback_rejects_invalid_state() -> None:
    client = create_test_client()

    client.get("/api/v1/auth/github/start", follow_redirects=False)
    response = client.get(
        "/api/v1/auth/github/callback?code=test-code&state=wrong-state",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "http://frontend.test/?auth_error=invalid_state"


def test_logout_clears_session() -> None:
    client = create_test_client()

    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    logout_response = client.post("/api/v1/auth/logout")
    me_response = client.get("/api/v1/me")

    assert logout_response.status_code == 204
    assert me_response.status_code == 401
    assert me_response.json() == {
        "error": {
            "code": "unauthenticated",
            "message": "Authentication required.",
        }
    }


def test_repositories_requires_authenticated_session() -> None:
    client = create_test_client()

    response = client.get("/api/v1/repositories")

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthenticated",
            "message": "Authentication required.",
        }
    }


def test_repositories_returns_accessible_repository_metadata() -> None:
    client = create_test_client()

    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    response = client.get("/api/v1/repositories")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 456,
                "full_name": "octocat/commitfolio",
                "private": True,
                "owner_type": "Organization",
                "default_branch": "main",
                "permissions": {"admin": False, "push": True, "pull": True},
                "html_url": "https://github.com/octocat/commitfolio",
                "description": "Portfolio generator",
                "updated_at": "2026-04-15T00:00:00Z",
            }
        ],
        "next_cursor": None,
    }



def test_repository_lookup_returns_direct_org_repository() -> None:
    client = create_test_client()

    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    response = client.get("/api/v1/repositories/lookup?full_name=SERVICE-MOHAENG/Mohaeng-BE")

    assert response.status_code == 200
    assert response.json() == {
        "id": 789,
        "full_name": "SERVICE-MOHAENG/Mohaeng-BE",
        "private": True,
        "owner_type": "Organization",
        "default_branch": "develop",
        "permissions": {"admin": False, "push": True, "pull": True},
        "html_url": "https://github.com/SERVICE-MOHAENG/Mohaeng-BE",
        "description": "Mohaeng backend",
        "updated_at": "2026-04-17T00:00:00Z",
    }

def test_repositories_normalizes_github_failures() -> None:
    class FailingRepositoryGitHubService(FakeGitHubService):
        async def fetch_repositories(
            self,
            access_token: str,
            *,
            visibility: str = "all",
            cursor: Optional[str] = None,
        ) -> GitHubRepositoryPage:
            raise GitHubOAuthError("repository_lookup_failed", "GitHub repository lookup failed.")

    app = create_app(
        Settings(
            github_client_id="test-client-id",
            github_client_secret="test-client-secret",
            github_callback_url="http://testserver/api/v1/auth/github/callback",
            frontend_app_url="http://frontend.test",
            session_secret="test-session-secret",
            cors_origin="http://frontend.test",
            database_url="sqlite+pysqlite:///:memory:",
        )
    )
    init_db(app.state.db_engine)
    app.dependency_overrides[get_github_service] = lambda: FailingRepositoryGitHubService()
    client = TestClient(app)

    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    response = client.get("/api/v1/repositories")

    assert response.status_code == 502
    assert response.json() == {
        "error": {
            "code": "repository_lookup_failed",
            "message": "GitHub repository lookup failed.",
        }
    }


def test_analysis_jobs_require_authenticated_session() -> None:
    client = create_test_client()

    response = client.post(
        "/api/v1/analysis-jobs",
        json={"repository_full_name": "octocat/commitfolio", "branch": "main"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthenticated",
            "message": "Authentication required.",
        }
    }


def test_analysis_job_create_and_lookup() -> None:
    client = create_test_client()

    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    create_response = client.post(
        "/api/v1/analysis-jobs",
        json={
            "repository_full_name": "octocat/commitfolio",
            "branch": "main",
            "github_repo_id": 456,
            "private": True,
            "owner_type": "Organization",
            "default_branch": "main",
            "html_url": "https://github.com/octocat/commitfolio",
            "description": "Portfolio generator",
        },
    )

    assert create_response.status_code == 201
    payload = create_response.json()
    assert payload["job_id"].startswith("job_")
    assert payload == {
        "job_id": payload["job_id"],
        "status": "queued",
        "repository_full_name": "octocat/commitfolio",
        "branch": "main",
        "progress": {"stage": "queued", "percent": 0},
        "result_id": None,
        "failure_reason": None,
    }

    lookup_response = client.get(f"/api/v1/analysis-jobs/{payload['job_id']}")

    assert lookup_response.status_code == 200
    assert lookup_response.json() == payload


def test_analysis_job_lookup_returns_not_found_for_unknown_job() -> None:
    client = create_test_client()

    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    response = client.get("/api/v1/analysis-jobs/job_missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "analysis_job_not_found",
            "message": "Analysis job was not found.",
        }
    }


def create_authenticated_job(client: TestClient) -> str:
    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )
    create_response = client.post(
        "/api/v1/analysis-jobs",
        json={
            "repository_full_name": "octocat/commitfolio",
            "branch": "main",
            "github_repo_id": 456,
            "private": True,
            "owner_type": "Organization",
            "default_branch": "main",
            "html_url": "https://github.com/octocat/commitfolio",
            "description": "Portfolio generator",
        },
    )
    return str(create_response.json()["job_id"])


def test_analysis_job_run_collects_evidence_and_events() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)

    run_response = client.post(f"/api/v1/analysis-jobs/{job_id}/run")

    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["job"]["status"] == "completed"
    assert payload["job"]["progress"] == {"stage": "completed", "percent": 100}
    assert payload["evidence"]["total_count"] == 5
    assert payload["evidence"]["counts"] == {
        "changed_file": 1,
        "commit": 1,
        "issue": 1,
        "pull_request": 1,
        "review": 1,
    }
    assert [event["sequence"] for event in payload["evidence"]["latest_events"]] == list(range(1, 8))
    assert payload["evidence"]["latest_events"][-1]["event_type"] == "job_completed"

    lookup_response = client.get(f"/api/v1/analysis-jobs/{job_id}")

    assert lookup_response.status_code == 200
    assert lookup_response.json()["status"] == "completed"


def test_analysis_job_events_stream_replays_after_cursor() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")

    response = client.get(f"/api/v1/analysis-jobs/{job_id}/events?after=6")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert "event: snapshot" in body
    assert "id: 7" in body
    assert "event: job_completed" in body
    assert "id: 6" not in body


def test_analysis_job_events_stream_accepts_last_event_id_header() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")

    response = client.get(
        f"/api/v1/analysis-jobs/{job_id}/events",
        headers={"Last-Event-ID": "6"},
    )

    assert response.status_code == 200
    assert "id: 7" in response.text


def test_analysis_job_events_stream_rejects_invalid_last_event_id() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)

    response = client.get(
        f"/api/v1/analysis-jobs/{job_id}/events",
        headers={"Last-Event-ID": "not-a-number"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_event_cursor",
            "message": "Event replay cursor is invalid.",
        }
    }


def test_analysis_job_evidence_summary_requires_owner_job() -> None:
    client = create_test_client()

    response = client.get("/api/v1/analysis-jobs/job_missing/evidence")

    assert response.status_code == 401


def test_analysis_job_run_persists_failed_status_on_github_error() -> None:
    class FailingEvidenceGitHubService(FakeGitHubService):
        async def collect_repository_evidence(
            self,
            access_token: str,
            *,
            full_name: str,
            branch: str,
        ) -> list[GitHubEvidenceItem]:
            raise GitHubOAuthError("commits_lookup_failed", "GitHub evidence lookup failed.")

    app = create_app(
        Settings(
            github_client_id="test-client-id",
            github_client_secret="test-client-secret",
            github_callback_url="http://testserver/api/v1/auth/github/callback",
            frontend_app_url="http://frontend.test",
            session_secret="test-session-secret",
            cors_origin="http://frontend.test",
            database_url="sqlite+pysqlite:///:memory:",
        )
    )
    init_db(app.state.db_engine)
    app.dependency_overrides[get_github_service] = lambda: FailingEvidenceGitHubService()
    client = TestClient(app)
    job_id = create_authenticated_job(client)

    run_response = client.post(f"/api/v1/analysis-jobs/{job_id}/run")
    lookup_response = client.get(f"/api/v1/analysis-jobs/{job_id}")

    assert run_response.status_code == 502
    assert run_response.json() == {
        "error": {
            "code": "commits_lookup_failed",
            "message": "GitHub evidence lookup failed.",
        }
    }
    assert lookup_response.json()["status"] == "failed"
    assert lookup_response.json()["failure_reason"] == "GitHub evidence lookup failed."


def test_portfolio_result_generation_requires_authenticated_session() -> None:
    client = create_test_client()

    response = client.post("/api/v1/analysis-jobs/job_missing/result")

    assert response.status_code == 401


def test_completed_analysis_job_generates_portfolio_result_and_detail() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")

    result_response = client.post(f"/api/v1/analysis-jobs/{job_id}/result")

    assert result_response.status_code == 200
    result_payload = result_response.json()
    assert result_payload["result_id"].startswith("res_")
    assert result_payload["analysis_job_id"] == job_id
    assert result_payload["repository_full_name"] == "octocat/commitfolio"
    assert result_payload["headline"]
    assert result_payload["project_overview"]
    assert result_payload["role_summary"]
    assert result_payload["key_contributions"]
    assert result_payload["tech_stack"]
    assert result_payload["evidence_summary"]
    assert result_payload["interview_questions"]
    assert result_payload["enhancement_status"] == "not_configured"
    assert result_payload["enhancement_model"] is None
    assert result_payload["enhancement_message"] == "기본 생성 사용"
    assert result_payload["evidence_links"]
    assert {link["section_key"] for link in result_payload["evidence_links"]} >= {
        "key_contributions",
        "evidence_summary",
    }

    lookup_response = client.get(f"/api/v1/results/{result_payload['result_id']}")
    job_response = client.get(f"/api/v1/analysis-jobs/{job_id}")

    assert lookup_response.status_code == 200
    assert lookup_response.json()["result_id"] == result_payload["result_id"]
    assert job_response.json()["result_id"] == result_payload["result_id"]


def test_portfolio_result_generation_applies_openai_enhancement(monkeypatch: pytest.MonkeyPatch) -> None:
    enhanced_payload = {
        "headline": "OpenAI가 다듬은 포트폴리오 헤드라인",
        "project_overview": "OpenAI가 근거를 유지하며 다듬은 프로젝트 개요입니다.",
        "role_summary": "OpenAI가 다듬은 역할 요약입니다.",
        "key_contributions": ["OpenAI가 다듬은 핵심 기여"],
        "tech_stack": ["Python", "React"],
        "evidence_summary": "OpenAI가 다듬은 근거 요약입니다.",
        "interview_questions": ["OpenAI가 다듬은 면접 질문은 무엇인가요?"],
    }

    fake_client = FakeOpenAIClient(FakeOpenAIResponse({"output_text": json.dumps(enhanced_payload, ensure_ascii=False)}))

    monkeypatch.setattr("app.services.result_enhancement.httpx.Client", lambda timeout: fake_client)
    client = create_test_client(openai_api_key="test-openai-key", openai_model="test-model")
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")

    response = client.post(f"/api/v1/analysis-jobs/{job_id}/result")

    assert response.status_code == 200
    assert fake_client.seen_headers is not None
    assert fake_client.seen_headers["Authorization"] == "Bearer test-openai-key"
    assert fake_client.seen_json is not None
    assert fake_client.seen_json["model"] == "test-model"
    payload = response.json()
    assert payload["headline"] == "OpenAI가 다듬은 포트폴리오 헤드라인"
    assert payload["key_contributions"] == ["OpenAI가 다듬은 핵심 기여"]
    assert payload["enhancement_status"] == "enhanced"
    assert payload["enhancement_model"] == "test-model"
    assert payload["enhancement_message"] == "OpenAI 후처리 적용"
    assert payload["evidence_links"]


def test_portfolio_result_generation_falls_back_when_openai_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeOpenAIClient(FakeOpenAIResponse({"error": {"message": "boom"}}, status_code=500))

    monkeypatch.setattr("app.services.result_enhancement.httpx.Client", lambda timeout: fake_client)
    client = create_test_client(openai_api_key="test-openai-key", openai_model="test-model")
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")

    response = client.post(f"/api/v1/analysis-jobs/{job_id}/result")

    assert response.status_code == 200
    payload = response.json()
    assert payload["headline"] == "octocat/commitfolio에서 근거 기반 개발 흐름을 완성한 프로젝트 경험"
    assert payload["enhancement_status"] == "fallback"
    assert payload["enhancement_model"] == "test-model"
    assert payload["enhancement_message"] == "OpenAI 후처리 실패, 기본 생성 사용"


def test_portfolio_result_list_returns_recent_results() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")
    result_response = client.post(f"/api/v1/analysis-jobs/{job_id}/result")

    list_response = client.get("/api/v1/results")

    assert list_response.status_code == 200
    assert list_response.json()["items"] == [
        {
            "result_id": result_response.json()["result_id"],
            "analysis_job_id": job_id,
            "repository_full_name": "octocat/commitfolio",
            "headline": result_response.json()["headline"],
            "version": 1,
            "created_at": result_response.json()["created_at"],
            "updated_at": result_response.json()["updated_at"],
        }
    ]


def test_portfolio_result_generation_requires_completed_job() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)

    response = client.post(f"/api/v1/analysis-jobs/{job_id}/result")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "analysis_job_result_not_available",
            "message": "Completed analysis job was not found for result generation.",
        }
    }


def test_portfolio_result_patch_updates_editable_fields() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")
    result_id = client.post(f"/api/v1/analysis-jobs/{job_id}/result").json()["result_id"]

    response = client.patch(
        f"/api/v1/results/{result_id}",
        json={
            "headline": "Updated headline",
            "project_overview": "Updated overview",
            "key_contributions": ["Updated contribution"],
            "tech_stack": ["Python", "React", "SQLAlchemy"],
            "interview_questions": ["Updated question?"],
        },
    )
    lookup = client.get(f"/api/v1/results/{result_id}")

    assert response.status_code == 200
    assert response.json()["headline"] == "Updated headline"
    assert response.json()["project_overview"] == "Updated overview"
    assert response.json()["key_contributions"] == ["Updated contribution"]
    assert response.json()["tech_stack"] == ["Python", "React", "SQLAlchemy"]
    assert response.json()["interview_questions"] == ["Updated question?"]
    assert lookup.json()["headline"] == "Updated headline"


def test_portfolio_result_patch_requires_authentication() -> None:
    client = create_test_client()

    response = client.patch("/api/v1/results/res_missing", json={"headline": "Updated"})

    assert response.status_code == 401


def test_portfolio_result_regenerate_creates_new_version_and_updates_job() -> None:
    client = create_test_client()
    job_id = create_authenticated_job(client)
    client.post(f"/api/v1/analysis-jobs/{job_id}/run")
    first_result = client.post(f"/api/v1/analysis-jobs/{job_id}/result").json()

    response = client.post(f"/api/v1/results/{first_result['result_id']}/regenerate")
    job_response = client.get(f"/api/v1/analysis-jobs/{job_id}")
    list_response = client.get("/api/v1/results")

    assert response.status_code == 200
    assert response.json()["result_id"] != first_result["result_id"]
    assert response.json()["version"] == 2
    assert job_response.json()["result_id"] == response.json()["result_id"]
    assert [item["result_id"] for item in list_response.json()["items"]] == [
        response.json()["result_id"],
        first_result["result_id"],
    ]


def test_portfolio_result_regenerate_requires_owned_result() -> None:
    client = create_test_client()
    start_response = client.get("/api/v1/auth/github/start", follow_redirects=False)
    state = start_response.headers["location"].split("state=")[1]
    client.get(
        f"/api/v1/auth/github/callback?code=test-code&state={state}",
        follow_redirects=False,
    )

    response = client.post("/api/v1/results/res_missing/regenerate")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "portfolio_result_not_found",
            "message": "Portfolio result was not found.",
        }
    }


def test_healthcheck_includes_request_id_header() -> None:
    client = create_test_client()

    response = client.get("/healthz", headers={"X-Request-ID": "req_test"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req_test"


def test_unexpected_exception_uses_common_error_envelope() -> None:
    app = create_app(
        Settings(
            github_client_id="test-client-id",
            github_client_secret="test-client-secret",
            github_callback_url="http://testserver/api/v1/auth/github/callback",
            frontend_app_url="http://frontend.test",
            session_secret="test-session-secret",
            cors_origin="http://frontend.test",
            database_url="sqlite+pysqlite:///:memory:",
        )
    )

    @app.get("/explode")
    async def explode() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/explode", headers={"X-Request-ID": "req_boom"})

    assert response.status_code == 500
    assert response.headers["x-request-id"] == "req_boom"
    assert response.json() == {
        "error": {
            "code": "internal_server_error",
            "message": "서버에서 예상하지 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        }
    }
