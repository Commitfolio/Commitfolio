from __future__ import annotations

from typing import Optional, Union
import secrets

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response

from app.api.dependencies import get_github_service
from app.api.responses import build_error_response, build_frontend_redirect
from app.api.schemas import ErrorEnvelope, MeResponse
from app.github_oauth import GitHubOAuthError, GitHubOAuthService


router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.get("/auth/github/start")
async def start_github_oauth(
    request: Request,
    github: GitHubOAuthService = Depends(get_github_service),
) -> RedirectResponse:
    settings = request.app.state.settings

    if not github.is_configured():
        return RedirectResponse(
            build_frontend_redirect(
                settings.frontend_app_url,
                auth_error="backend_not_configured",
            ),
            status_code=status.HTTP_302_FOUND,
        )

    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    return RedirectResponse(github.build_authorize_url(state), status_code=status.HTTP_302_FOUND)


@router.get("/auth/github/callback")
async def finish_github_oauth(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    github: GitHubOAuthService = Depends(get_github_service),
) -> RedirectResponse:
    settings = request.app.state.settings

    if error:
        return RedirectResponse(
            build_frontend_redirect(settings.frontend_app_url, auth_error="access_denied"),
            status_code=status.HTTP_302_FOUND,
        )

    expected_state = request.session.get("oauth_state")

    if not state or not expected_state or state != expected_state:
        request.session.pop("oauth_state", None)
        return RedirectResponse(
            build_frontend_redirect(settings.frontend_app_url, auth_error="invalid_state"),
            status_code=status.HTTP_302_FOUND,
        )

    if not code:
        request.session.pop("oauth_state", None)
        return RedirectResponse(
            build_frontend_redirect(settings.frontend_app_url, auth_error="missing_code"),
            status_code=status.HTTP_302_FOUND,
        )

    try:
        access_token = await github.exchange_code(code)
        profile = await github.fetch_user(access_token)
    except GitHubOAuthError as error_response:
        request.session.pop("oauth_state", None)
        return RedirectResponse(
            build_frontend_redirect(
                settings.frontend_app_url,
                auth_error=error_response.code,
            ),
            status_code=status.HTTP_302_FOUND,
        )

    request.session.pop("oauth_state", None)
    previous_token_id = request.session.pop("github_token_id", None)
    if previous_token_id:
        request.app.state.github_access_tokens.pop(previous_token_id, None)

    github_token_id = secrets.token_urlsafe(32)
    request.app.state.github_access_tokens[github_token_id] = access_token
    request.session["github_token_id"] = github_token_id
    request.session["user"] = {
        "id": f"github:{profile.id}",
        "github_login": profile.login,
        "connected": True,
        "name": profile.name,
        "avatar_url": profile.avatar_url,
    }

    return RedirectResponse(
        build_frontend_redirect(settings.frontend_app_url, auth="success"),
        status_code=status.HTTP_302_FOUND,
    )


@router.get(
    "/me",
    response_model=MeResponse,
    responses={401: {"model": ErrorEnvelope}},
)
async def get_me(request: Request) -> Union[MeResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthenticated",
            "Authentication required.",
        )

    return MeResponse(**user)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request) -> Response:
    github_token_id = request.session.get("github_token_id")
    if github_token_id:
        request.app.state.github_access_tokens.pop(github_token_id, None)
    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
