from __future__ import annotations

from typing import Optional, Union

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.dependencies import get_analysis_event_service, get_analysis_job_service
from app.api.responses import build_error_response
from app.api.schemas import ErrorEnvelope
from app.services.analysis_events import AnalysisEventService
from app.services.analysis_jobs import AnalysisJobService


router = APIRouter(prefix="/api/v1", tags=["analysis-events"])


@router.get(
    "/analysis-jobs/{job_id}/events",
    response_model=None,
    responses={401: {"model": ErrorEnvelope}, 404: {"model": ErrorEnvelope}},
)
async def stream_analysis_job_events(
    request: Request,
    job_id: str,
    after: Optional[int] = Query(default=None, ge=0),
    analysis_jobs: AnalysisJobService = Depends(get_analysis_job_service),
    analysis_events: AnalysisEventService = Depends(get_analysis_event_service),
) -> Union[StreamingResponse, JSONResponse]:
    user = request.session.get("user")

    if not user:
        return build_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthenticated",
            "Authentication required.",
        )

    after_sequence = analysis_events.resolve_event_cursor(after, request.headers.get("last-event-id"))
    if after_sequence is None:
        return build_error_response(
            status.HTTP_400_BAD_REQUEST,
            "invalid_event_cursor",
            "Event replay cursor is invalid.",
        )

    user_id = str(user["id"])
    job = analysis_jobs.get_owned_job(user_id, job_id)

    if not job:
        return build_error_response(
            status.HTTP_404_NOT_FOUND,
            "analysis_job_not_found",
            "Analysis job was not found.",
        )

    return StreamingResponse(
        analysis_events.stream_job_events(
            request,
            request.app.state.db_session_factory,
            job.id,
            user_id,
            after_sequence,
            analysis_jobs.build_analysis_job_response(job),
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
