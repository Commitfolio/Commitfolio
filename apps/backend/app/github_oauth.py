from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from app.config import Settings


AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_URL = "https://api.github.com/user"
REPOSITORIES_URL = "https://api.github.com/user/repos"


class GitHubOAuthError(RuntimeError):
    """Raised when the GitHub OAuth flow cannot complete."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class GitHubUser:
    id: int
    login: str
    name: Optional[str]
    avatar_url: Optional[str]


@dataclass
class GitHubRepository:
    id: int
    full_name: str
    private: bool
    owner_type: str
    default_branch: str
    permissions: dict[str, bool]
    html_url: str
    description: Optional[str]
    updated_at: Optional[str]


@dataclass
class GitHubRepositoryPage:
    items: list[GitHubRepository]
    next_cursor: Optional[str]


class GitHubOAuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        return bool(self.settings.github_client_id and self.settings.github_client_secret)

    def build_authorize_url(self, state: str) -> str:
        query = urlencode(
            {
                "client_id": self.settings.github_client_id,
                "redirect_uri": self.settings.github_callback_url,
                "scope": self.settings.github_scope,
                "state": state,
                "allow_signup": "false",
            }
        )
        return f"{AUTHORIZE_URL}?{query}"

    async def exchange_code(self, code: str) -> str:
        if not self.is_configured():
            raise GitHubOAuthError(
                "backend_not_configured",
                "GitHub OAuth credentials are missing.",
            )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.settings.github_client_id,
                    "client_secret": self.settings.github_client_secret,
                    "code": code,
                    "redirect_uri": self.settings.github_callback_url,
                },
            )

        payload = self._decode_json(response, "oauth_exchange_failed")

        if not isinstance(payload, dict):
            raise GitHubOAuthError(
                "oauth_exchange_failed",
                "GitHub returned an unexpected token payload.",
            )

        access_token = payload.get("access_token")

        if response.status_code != 200 or not access_token:
            raise GitHubOAuthError(
                "oauth_exchange_failed",
                "GitHub token exchange failed.",
            )

        return str(access_token)

    async def fetch_user(self, access_token: str) -> GitHubUser:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                USER_URL,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {access_token}",
                },
            )

        payload = self._decode_json(response, "oauth_profile_failed")

        if (
            response.status_code != 200
            or not isinstance(payload, dict)
            or "login" not in payload
            or "id" not in payload
        ):
            raise GitHubOAuthError(
                "oauth_profile_failed",
                "GitHub user lookup failed.",
            )

        return GitHubUser(
            id=int(payload["id"]),
            login=str(payload["login"]),
            name=str(payload["name"]) if payload.get("name") else None,
            avatar_url=str(payload["avatar_url"]) if payload.get("avatar_url") else None,
        )

    async def fetch_repositories(
        self,
        access_token: str,
        *,
        visibility: str = "all",
        cursor: Optional[str] = None,
    ) -> GitHubRepositoryPage:
        page = self._parse_cursor(cursor)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                REPOSITORIES_URL,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {access_token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                params={
                    "visibility": visibility,
                    "affiliation": "owner,collaborator,organization_member",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 30,
                    "page": page,
                },
            )

        payload = self._decode_json(response, "repository_lookup_failed")

        if response.status_code != 200 or not isinstance(payload, list):
            raise GitHubOAuthError(
                "repository_lookup_failed",
                "GitHub repository lookup failed.",
            )

        return GitHubRepositoryPage(
            items=[self._decode_repository(item) for item in payload if isinstance(item, dict)],
            next_cursor=self._extract_next_cursor(response),
        )

    @staticmethod
    def _parse_cursor(cursor: Optional[str]) -> int:
        if cursor is None:
            return 1

        try:
            page = int(cursor)
        except ValueError as error:
            raise GitHubOAuthError("invalid_repository_cursor", "Repository cursor is invalid.") from error

        if page < 1:
            raise GitHubOAuthError("invalid_repository_cursor", "Repository cursor is invalid.")

        return page

    @staticmethod
    def _decode_repository(payload: dict[str, Any]) -> GitHubRepository:
        permissions_payload = payload.get("permissions")
        permissions = permissions_payload if isinstance(permissions_payload, dict) else {}
        owner_payload = payload.get("owner")
        owner = owner_payload if isinstance(owner_payload, dict) else {}

        return GitHubRepository(
            id=int(payload["id"]),
            full_name=str(payload["full_name"]),
            private=bool(payload.get("private", False)),
            owner_type=str(owner.get("type") or "Unknown"),
            default_branch=str(payload.get("default_branch") or ""),
            permissions={
                "admin": bool(permissions.get("admin", False)),
                "push": bool(permissions.get("push", False)),
                "pull": bool(permissions.get("pull", False)),
            },
            html_url=str(payload.get("html_url") or ""),
            description=str(payload["description"]) if payload.get("description") else None,
            updated_at=str(payload["updated_at"]) if payload.get("updated_at") else None,
        )

    @staticmethod
    def _extract_next_cursor(response: httpx.Response) -> Optional[str]:
        next_link = response.links.get("next")
        if not next_link:
            return None

        next_url = next_link.get("url")
        if not next_url:
            return None

        next_page = parse_qs(urlparse(next_url).query).get("page")
        return next_page[0] if next_page else None

    @staticmethod
    def _decode_json(response: httpx.Response, code: str) -> Any:
        try:
            return response.json()
        except ValueError as error:  # pragma: no cover - defensive fallback
            raise GitHubOAuthError(code, "GitHub returned invalid JSON.") from error
