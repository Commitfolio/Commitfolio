from __future__ import annotations

from typing import Optional

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


def create_test_client() -> TestClient:
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
