from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlencode

import httpx

from app.config import Settings


AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_URL = "https://api.github.com/user"


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

        if response.status_code != 200 or "login" not in payload or "id" not in payload:
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

    @staticmethod
    def _decode_json(response: httpx.Response, code: str) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as error:  # pragma: no cover - defensive fallback
            raise GitHubOAuthError(code, "GitHub returned invalid JSON.") from error

        if not isinstance(payload, dict):
            raise GitHubOAuthError(code, "GitHub returned an unexpected payload.")

        return payload
