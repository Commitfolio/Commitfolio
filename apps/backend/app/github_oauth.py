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


@dataclass
class GitHubEvidenceItem:
    source_type: str
    source_id: str
    url: str
    payload: dict[str, Any]


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


    async def fetch_repository_by_full_name(
        self,
        access_token: str,
        *,
        full_name: str,
    ) -> GitHubRepository:
        owner, repo = self._split_full_name(full_name)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {access_token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

        payload = self._decode_json(response, "repository_lookup_failed")

        if response.status_code in {403, 404}:
            raise GitHubOAuthError(
                "repository_not_accessible",
                "Repository was not found or the OAuth app does not have access.",
            )

        if response.status_code != 200 or not isinstance(payload, dict):
            raise GitHubOAuthError(
                "repository_lookup_failed",
                "GitHub repository lookup failed.",
            )

        return self._decode_repository(payload)

    async def collect_repository_evidence(
        self,
        access_token: str,
        *,
        full_name: str,
        branch: str,
    ) -> list[GitHubEvidenceItem]:
        owner, repo = self._split_full_name(full_name)

        async with httpx.AsyncClient(timeout=15.0) as client:
            commits = await self._get_github_list(
                client,
                access_token,
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                "commits_lookup_failed",
                params={"sha": branch, "per_page": 10},
            )
            pulls = await self._get_github_list(
                client,
                access_token,
                f"https://api.github.com/repos/{owner}/{repo}/pulls",
                "pull_requests_lookup_failed",
                params={"state": "all", "sort": "updated", "direction": "desc", "per_page": 10},
            )
            issues = await self._get_github_list(
                client,
                access_token,
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                "issues_lookup_failed",
                params={"state": "all", "sort": "updated", "direction": "desc", "per_page": 10},
            )

            evidence: list[GitHubEvidenceItem] = []
            evidence.extend(self._decode_commits(commits))
            evidence.extend(self._decode_pull_requests(pulls))
            evidence.extend(self._decode_issues(issues))

            for pull in pulls[:5]:
                if not isinstance(pull, dict) or "number" not in pull:
                    continue

                pull_number = int(pull["number"])
                reviews = await self._get_github_list(
                    client,
                    access_token,
                    f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
                    "reviews_lookup_failed",
                    params={"per_page": 10},
                )
                files = await self._get_github_list(
                    client,
                    access_token,
                    f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files",
                    "changed_files_lookup_failed",
                    params={"per_page": 20},
                )
                evidence.extend(self._decode_reviews(pull_number, reviews))
                evidence.extend(self._decode_changed_files(pull_number, files))

        return evidence

    async def _get_github_list(
        self,
        client: httpx.AsyncClient,
        access_token: str,
        url: str,
        error_code: str,
        *,
        params: dict[str, object],
    ) -> list[Any]:
        response = await client.get(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            params=params,
        )
        payload = self._decode_json(response, error_code)

        if response.status_code == 403:
            raise GitHubOAuthError(error_code, "GitHub permission or rate limit prevented evidence lookup.")

        if response.status_code != 200 or not isinstance(payload, list):
            raise GitHubOAuthError(error_code, "GitHub evidence lookup failed.")

        return payload

    @staticmethod
    def _split_full_name(full_name: str) -> tuple[str, str]:
        parts = full_name.split("/", 1)
        if len(parts) != 2 or not all(parts):
            raise GitHubOAuthError("invalid_repository_full_name", "Repository full name is invalid.")

        return parts[0], parts[1]

    @staticmethod
    def _decode_commits(items: list[Any]) -> list[GitHubEvidenceItem]:
        evidence: list[GitHubEvidenceItem] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            commit = item.get("commit") if isinstance(item.get("commit"), dict) else {}
            author = commit.get("author") if isinstance(commit.get("author"), dict) else {}
            evidence.append(
                GitHubEvidenceItem(
                    source_type="commit",
                    source_id=str(item.get("sha") or ""),
                    url=str(item.get("html_url") or ""),
                    payload={
                        "sha": item.get("sha"),
                        "message": commit.get("message"),
                        "author_name": author.get("name"),
                        "authored_at": author.get("date"),
                    },
                )
            )

        return evidence

    @staticmethod
    def _decode_pull_requests(items: list[Any]) -> list[GitHubEvidenceItem]:
        evidence: list[GitHubEvidenceItem] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            evidence.append(
                GitHubEvidenceItem(
                    source_type="pull_request",
                    source_id=str(item.get("number") or ""),
                    url=str(item.get("html_url") or ""),
                    payload={
                        "number": item.get("number"),
                        "title": item.get("title"),
                        "state": item.get("state"),
                        "merged_at": item.get("merged_at"),
                        "updated_at": item.get("updated_at"),
                    },
                )
            )

        return evidence

    @staticmethod
    def _decode_issues(items: list[Any]) -> list[GitHubEvidenceItem]:
        evidence: list[GitHubEvidenceItem] = []

        for item in items:
            if not isinstance(item, dict) or item.get("pull_request"):
                continue

            evidence.append(
                GitHubEvidenceItem(
                    source_type="issue",
                    source_id=str(item.get("number") or ""),
                    url=str(item.get("html_url") or ""),
                    payload={
                        "number": item.get("number"),
                        "title": item.get("title"),
                        "state": item.get("state"),
                        "updated_at": item.get("updated_at"),
                    },
                )
            )

        return evidence

    @staticmethod
    def _decode_reviews(pull_number: int, items: list[Any]) -> list[GitHubEvidenceItem]:
        evidence: list[GitHubEvidenceItem] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            evidence.append(
                GitHubEvidenceItem(
                    source_type="review",
                    source_id=f"{pull_number}:{item.get('id')}",
                    url=str(item.get("html_url") or ""),
                    payload={
                        "pull_number": pull_number,
                        "review_id": item.get("id"),
                        "state": item.get("state"),
                        "submitted_at": item.get("submitted_at"),
                    },
                )
            )

        return evidence

    @staticmethod
    def _decode_changed_files(pull_number: int, items: list[Any]) -> list[GitHubEvidenceItem]:
        evidence: list[GitHubEvidenceItem] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            filename = str(item.get("filename") or "")
            evidence.append(
                GitHubEvidenceItem(
                    source_type="changed_file",
                    source_id=f"{pull_number}:{filename}",
                    url=str(item.get("blob_url") or ""),
                    payload={
                        "pull_number": pull_number,
                        "filename": filename,
                        "status": item.get("status"),
                        "additions": item.get("additions"),
                        "deletions": item.get("deletions"),
                        "changes": item.get("changes"),
                    },
                )
            )

        return evidence

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
