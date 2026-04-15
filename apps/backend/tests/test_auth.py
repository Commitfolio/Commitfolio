from __future__ import annotations

from typing import Optional

from fastapi.testclient import TestClient

from app.config import Settings
from app.github_oauth import GitHubOAuthError, GitHubRepository, GitHubRepositoryPage
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


def create_test_client() -> TestClient:
    app = create_app(
        Settings(
            github_client_id="test-client-id",
            github_client_secret="test-client-secret",
            github_callback_url="http://testserver/api/v1/auth/github/callback",
            frontend_app_url="http://frontend.test",
            session_secret="test-session-secret",
            cors_origin="http://frontend.test",
        )
    )
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
        )
    )
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
        )
    )
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
