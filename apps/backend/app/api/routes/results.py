from __future__ import annotations

from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_portfolio_result_service
from app.api.responses import build_error_response
from app.api.schemas import ErrorEnvelope, PortfolioResultListResponse, PortfolioResultResponse, PortfolioResultUpdateRequest
from app.services.results import PortfolioResultService


router = APIRouter(prefix="/api/v1", tags=["results"])


@router.post(
    "/analysis-jobs/{job_id}/result",
    response_model=PortfolioResultResponse,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
)
async def generate_portfolio_result(
    request: Request,
    job_id: str,
    service: PortfolioResultService = Depends(get_portfolio_result_service),
) -> Union[PortfolioResultResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(status.HTTP_401_UNAUTHORIZED, "unauthenticated", "Authentication required.")

    result = service.generate_for_job(str(user["id"]), job_id)
    if not result:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "analysis_job_result_not_available",
            "Completed analysis job was not found for result generation.",
        )

    return result


@router.get(
    "/results",
    response_model=PortfolioResultListResponse,
    responses={401: {"model": ErrorEnvelope}},
)
async def list_portfolio_results(
    request: Request,
    service: PortfolioResultService = Depends(get_portfolio_result_service),
) -> Union[PortfolioResultListResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(status.HTTP_401_UNAUTHORIZED, "unauthenticated", "Authentication required.")

    return service.list_results(str(user["id"]))


@router.get(
    "/results/{result_id}",
    response_model=PortfolioResultResponse,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
)
async def get_portfolio_result(
    request: Request,
    result_id: str,
    service: PortfolioResultService = Depends(get_portfolio_result_service),
) -> Union[PortfolioResultResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(status.HTTP_401_UNAUTHORIZED, "unauthenticated", "Authentication required.")

    result = service.get_result(str(user["id"]), result_id)
    if not result:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "portfolio_result_not_found",
            "Portfolio result was not found.",
        )

    return result


@router.patch(
    "/results/{result_id}",
    response_model=PortfolioResultResponse,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
)
async def update_portfolio_result(
    request: Request,
    result_id: str,
    payload: PortfolioResultUpdateRequest,
    service: PortfolioResultService = Depends(get_portfolio_result_service),
) -> Union[PortfolioResultResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(status.HTTP_401_UNAUTHORIZED, "unauthenticated", "Authentication required.")

    result = service.update_result(str(user["id"]), result_id, payload)
    if not result:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "portfolio_result_not_found",
            "Portfolio result was not found.",
        )

    return result


@router.post(
    "/results/{result_id}/regenerate",
    response_model=PortfolioResultResponse,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
)
async def regenerate_portfolio_result(
    request: Request,
    result_id: str,
    service: PortfolioResultService = Depends(get_portfolio_result_service),
) -> Union[PortfolioResultResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(status.HTTP_401_UNAUTHORIZED, "unauthenticated", "Authentication required.")

    result = service.regenerate_result(str(user["id"]), result_id)
    if not result:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "portfolio_result_not_found",
            "Portfolio result was not found.",
        )

    return result
