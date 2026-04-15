from __future__ import annotations

from typing import Optional, TypedDict, Union
from urllib.parse import urlencode
import secrets

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from app.config import Settings, get_settings
from app.github_oauth import GitHubOAuthError, GitHubOAuthService


class SessionUser(TypedDict):
    id: str
    github_login: str
    connected: bool
    name: Optional[str]
    avatar_url: Optional[str]


class MeResponse(BaseModel):
    id: str
    github_login: str
    connected: bool
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


def build_frontend_redirect(frontend_app_url: str, **query: str) -> str:
    encoded = urlencode(query)
    return f"{frontend_app_url}/?{encoded}" if encoded else frontend_app_url


def get_github_service(request: Request) -> GitHubOAuthService:
    settings: Settings = request.app.state.settings
    return GitHubOAuthService(settings)


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(title="Commitfolio API", version="0.1.0")
    app.state.settings = resolved_settings

    app.add_middleware(
        SessionMiddleware,
        secret_key=resolved_settings.session_secret,
        same_site="lax",
        https_only=False,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved_settings.cors_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/auth/github/start")
    async def start_github_oauth(
        request: Request,
        github: GitHubOAuthService = Depends(get_github_service),
    ) -> RedirectResponse:
        if not github.is_configured():
            return RedirectResponse(
                build_frontend_redirect(
                    resolved_settings.frontend_app_url,
                    auth_error="backend_not_configured",
                ),
                status_code=status.HTTP_302_FOUND,
            )

        state = secrets.token_urlsafe(32)
        request.session["oauth_state"] = state
        return RedirectResponse(github.build_authorize_url(state), status_code=status.HTTP_302_FOUND)

    @app.get("/api/v1/auth/github/callback")
    async def finish_github_oauth(
        request: Request,
        code: Optional[str] = None,
        state: Optional[str] = None,
        error: Optional[str] = None,
        github: GitHubOAuthService = Depends(get_github_service),
    ) -> RedirectResponse:
        if error:
            return RedirectResponse(
                build_frontend_redirect(resolved_settings.frontend_app_url, auth_error="access_denied"),
                status_code=status.HTTP_302_FOUND,
            )

        expected_state = request.session.get("oauth_state")

        if not state or not expected_state or state != expected_state:
            request.session.pop("oauth_state", None)
            return RedirectResponse(
                build_frontend_redirect(resolved_settings.frontend_app_url, auth_error="invalid_state"),
                status_code=status.HTTP_302_FOUND,
            )

        if not code:
            request.session.pop("oauth_state", None)
            return RedirectResponse(
                build_frontend_redirect(resolved_settings.frontend_app_url, auth_error="missing_code"),
                status_code=status.HTTP_302_FOUND,
            )

        try:
            access_token = await github.exchange_code(code)
            profile = await github.fetch_user(access_token)
        except GitHubOAuthError as error_response:
            request.session.pop("oauth_state", None)
            return RedirectResponse(
                build_frontend_redirect(
                    resolved_settings.frontend_app_url,
                    auth_error=error_response.code,
                ),
                status_code=status.HTTP_302_FOUND,
            )

        request.session.pop("oauth_state", None)
        request.session["user"] = {
            "id": f"github:{profile.id}",
            "github_login": profile.login,
            "connected": True,
            "name": profile.name,
            "avatar_url": profile.avatar_url,
        }

        return RedirectResponse(
            build_frontend_redirect(resolved_settings.frontend_app_url, auth="success"),
            status_code=status.HTTP_302_FOUND,
        )

    @app.get(
        "/api/v1/me",
        response_model=MeResponse,
        responses={401: {"model": ErrorEnvelope}},
    )
    async def get_me(request: Request) -> Union[MeResponse, JSONResponse]:
        user = request.session.get("user")

        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "code": "unauthenticated",
                        "message": "Authentication required.",
                    }
                },
            )

        return MeResponse(**user)

    @app.post("/api/v1/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(request: Request) -> Response:
        request.session.clear()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
