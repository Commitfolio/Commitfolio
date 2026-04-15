from __future__ import annotations

from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_analysis_job_service, get_github_service
from app.api.responses import build_error_response
from app.api.schemas import (
    AnalysisJobCreateRequest,
    AnalysisJobResponse,
    AnalysisRunResponse,
    ErrorEnvelope,
    EvidenceSummaryResponse,
)
from app.github_oauth import GitHubOAuthError, GitHubOAuthService
from app.services.analysis_jobs import AnalysisJobService


router = APIRouter(prefix="/api/v1", tags=["analysis-jobs"])


@router.post(
    "/analysis-jobs",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorEnvelope}},
)
async def create_analysis_job(
    request: Request,
    payload: AnalysisJobCreateRequest,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> Union[AnalysisJobResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthenticated",
            "Authentication required.",
        )

    return service.create_job_for_repository(str(user["id"]), payload)


@router.get(
    "/analysis-jobs/{job_id}",
    response_model=AnalysisJobResponse,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
)
async def get_analysis_job(
    request: Request,
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> Union[AnalysisJobResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthenticated",
            "Authentication required.",
        )

    response = service.get_owned_job_response(str(user["id"]), job_id)

    if not response:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "analysis_job_not_found",
            "Analysis job was not found.",
        )

    return response


@router.post(
    "/analysis-jobs/{job_id}/run",
    response_model=AnalysisRunResponse,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}, 502: {"model": ErrorEnvelope}},
)
async def run_analysis_job(
    request: Request,
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
    github: GitHubOAuthService = Depends(get_github_service),
) -> Union[AnalysisRunResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthenticated",
            "Authentication required.",
        )

    job = service.get_owned_job(str(user["id"]), job_id)

    if not job:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "analysis_job_not_found",
            "Analysis job was not found.",
        )

    github_token_id = request.session.get("github_token_id")
    access_token = (
        request.app.state.github_access_tokens.get(github_token_id)
        if github_token_id
        else None
    )

    if not access_token:
        service.mark_job_failed(job, "GitHub session token is missing. Sign in again.")
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "github_token_missing",
            "GitHub session token is missing. Sign in again.",
        )

    try:
        return await service.run_job_with_github(job, github, access_token)
    except GitHubOAuthError as error_response:
        return build_error_response(status.HTTP_502_BAD_GATEWAY, error_response.code, error_response.message)


@router.get(
    "/analysis-jobs/{job_id}/evidence",
    response_model=EvidenceSummaryResponse,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
)
async def get_analysis_job_evidence(
    request: Request,
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> Union[EvidenceSummaryResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthenticated",
            "Authentication required.",
        )

    job = service.get_owned_job(str(user["id"]), job_id)

    if not job:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "analysis_job_not_found",
            "Analysis job was not found.",
        )

    return service.build_evidence_summary(job)
