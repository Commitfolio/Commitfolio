from __future__ import annotations

from typing import Literal, Optional, Union

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_github_service
from app.api.responses import build_error_response
from app.api.schemas import (
    ErrorEnvelope,
    RepositoryListResponse,
    RepositoryPermissionsResponse,
    RepositoryResponse,
)
from app.github_oauth import GitHubOAuthError, GitHubOAuthService


router = APIRouter(prefix="/api/v1", tags=["repositories"])


@router.get(
    "/repositories",
    response_model=RepositoryListResponse,
    responses={401: {"model": ErrorEnvelope}, 502: {"model": ErrorEnvelope}},
)
async def list_repositories(
    request: Request,
    visibility: Literal["all", "public", "private"] = "all",
    cursor: Optional[str] = Query(default=None),
    github: GitHubOAuthService = Depends(get_github_service),
) -> Union[RepositoryListResponse, JSONResponse]:
    if not request.session.get("user"):
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthenticated",
            "Authentication required.",
        )

    github_token_id = request.session.get("github_token_id")
    access_token = (
        request.app.state.github_access_tokens.get(github_token_id)
        if github_token_id
        else None
    )

    if not access_token:
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "github_token_missing",
            "GitHub session token is missing. Sign in again.",
        )

    try:
        repository_page = await github.fetch_repositories(
            access_token,
            visibility=visibility,
            cursor=cursor,
        )
    except GitHubOAuthError as error_response:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if error_response.code == "invalid_repository_cursor"
            else status.HTTP_502_BAD_GATEWAY
        )
        return build_error_response(status_code, error_response.code, error_response.message)

    return RepositoryListResponse(
        items=[
            RepositoryResponse(
                id=repository.id,
                full_name=repository.full_name,
                private=repository.private,
                owner_type=repository.owner_type,
                default_branch=repository.default_branch,
                permissions=RepositoryPermissionsResponse(**repository.permissions),
                html_url=repository.html_url,
                description=repository.description,
                updated_at=repository.updated_at,
            )
            for repository in repository_page.items
        ],
        next_cursor=repository_page.next_cursor,
    )
