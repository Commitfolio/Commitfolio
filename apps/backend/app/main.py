from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal, Optional, TypedDict, Union
from urllib.parse import urlencode
import secrets

from fastapi import Depends, FastAPI, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.config import Settings, get_settings
from app.db import create_db_engine, create_session_factory, get_db_session, init_db
from app.github_oauth import GitHubOAuthError, GitHubOAuthService
from app.models import AnalysisJob, RepositorySnapshot, prefixed_id, utc_now


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


class RepositoryPermissionsResponse(BaseModel):
    admin: bool
    push: bool
    pull: bool


class RepositoryResponse(BaseModel):
    id: int
    full_name: str
    private: bool
    owner_type: str
    default_branch: str
    permissions: RepositoryPermissionsResponse
    html_url: str
    description: Optional[str] = None
    updated_at: Optional[str] = None


class RepositoryListResponse(BaseModel):
    items: list[RepositoryResponse]
    next_cursor: Optional[str] = None


class AnalysisJobCreateRequest(BaseModel):
    repository_full_name: str
    branch: str = "main"
    github_repo_id: Optional[int] = None
    private: bool = False
    owner_type: str = "Unknown"
    default_branch: str = "main"
    html_url: str = ""
    description: Optional[str] = None


class AnalysisJobProgressResponse(BaseModel):
    stage: str
    percent: int


class AnalysisJobResponse(BaseModel):
    job_id: str
    status: str
    repository_full_name: str
    branch: str
    progress: AnalysisJobProgressResponse
    result_id: Optional[str] = None
    failure_reason: Optional[str] = None


def build_frontend_redirect(frontend_app_url: str, **query: str) -> str:
    encoded = urlencode(query)
    return f"{frontend_app_url}/?{encoded}" if encoded else frontend_app_url


def get_github_service(request: Request) -> GitHubOAuthService:
    settings: Settings = request.app.state.settings
    return GitHubOAuthService(settings)


def build_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db(app.state.db_engine)
    yield


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(title="Commitfolio API", version="0.1.0", lifespan=lifespan)
    app.state.settings = resolved_settings
    app.state.github_access_tokens = {}
    app.state.db_engine = create_db_engine(resolved_settings.database_url)
    app.state.db_session_factory = create_session_factory(app.state.db_engine)

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
            return build_error_response(
                status.HTTP_401_UNAUTHORIZED,
                "unauthenticated",
                "Authentication required.",
            )

        return MeResponse(**user)

    @app.get(
        "/api/v1/repositories",
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

    @app.post(
        "/api/v1/analysis-jobs",
        response_model=AnalysisJobResponse,
        status_code=status.HTTP_201_CREATED,
        responses={401: {"model": ErrorEnvelope}},
    )
    async def create_analysis_job(
        request: Request,
        payload: AnalysisJobCreateRequest,
        db: Session = Depends(get_db_session),
    ) -> Union[AnalysisJobResponse, JSONResponse]:
        user = request.session.get("user")

        if not user:
            return build_error_response(
                status.HTTP_401_UNAUTHORIZED,
                "unauthenticated",
                "Authentication required.",
            )

        user_id = str(user["id"])
        repository = upsert_repository_snapshot(db, user_id, payload)
        job = AnalysisJob(
            id=prefixed_id("job"),
            user_id=user_id,
            repository_snapshot_id=repository.id,
            repository_full_name=repository.full_name,
            branch=payload.branch or repository.default_branch,
            status="queued",
            requested_at=utc_now(),
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        return build_analysis_job_response(job)

    @app.get(
        "/api/v1/analysis-jobs/{job_id}",
        response_model=AnalysisJobResponse,
        responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
    )
    async def get_analysis_job(
        request: Request,
        job_id: str,
        db: Session = Depends(get_db_session),
    ) -> Union[AnalysisJobResponse, JSONResponse]:
        user = request.session.get("user")

        if not user:
            return build_error_response(
                status.HTTP_401_UNAUTHORIZED,
                "unauthenticated",
                "Authentication required.",
            )

        job = db.scalar(
            select(AnalysisJob).where(
                AnalysisJob.id == job_id,
                AnalysisJob.user_id == str(user["id"]),
            )
        )

        if not job:
            return build_error_response(
                status.HTTP_404_NOT_FOUND,
                "analysis_job_not_found",
                "Analysis job was not found.",
            )

        return build_analysis_job_response(job)

    @app.post("/api/v1/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(request: Request) -> Response:
        github_token_id = request.session.get("github_token_id")
        if github_token_id:
            request.app.state.github_access_tokens.pop(github_token_id, None)
        request.session.clear()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


def upsert_repository_snapshot(
    db: Session,
    user_id: str,
    payload: AnalysisJobCreateRequest,
) -> RepositorySnapshot:
    repository = db.scalar(
        select(RepositorySnapshot).where(
            RepositorySnapshot.user_id == user_id,
            RepositorySnapshot.full_name == payload.repository_full_name,
        )
    )

    if not repository:
        repository = RepositorySnapshot(
            id=prefixed_id("repo"),
            user_id=user_id,
            full_name=payload.repository_full_name,
        )
        db.add(repository)

    repository.github_repo_id = payload.github_repo_id
    repository.private = payload.private
    repository.owner_type = payload.owner_type or "Unknown"
    repository.default_branch = payload.default_branch or payload.branch or "main"
    repository.html_url = payload.html_url
    repository.description = payload.description
    repository.last_synced_at = utc_now()

    db.flush()
    return repository


def build_analysis_job_response(job: AnalysisJob) -> AnalysisJobResponse:
    progress_by_status = {
        "queued": AnalysisJobProgressResponse(stage="queued", percent=0),
        "running": AnalysisJobProgressResponse(stage="running", percent=10),
        "completed": AnalysisJobProgressResponse(stage="completed", percent=100),
        "failed": AnalysisJobProgressResponse(stage="failed", percent=100),
    }

    return AnalysisJobResponse(
        job_id=job.id,
        status=job.status,
        repository_full_name=job.repository_full_name,
        branch=job.branch,
        progress=progress_by_status.get(
            job.status,
            AnalysisJobProgressResponse(stage=job.status, percent=0),
        ),
        result_id=job.result_id,
        failure_reason=job.failure_reason,
    )


app = create_app()
