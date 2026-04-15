from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.config import Settings
from app.db import get_db_session
from app.github_oauth import GitHubOAuthService
from app.repositories.analysis_jobs import AnalysisJobRepository
from app.services.analysis_events import AnalysisEventService
from app.services.analysis_jobs import AnalysisJobService


def get_github_service(request: Request) -> GitHubOAuthService:
    settings: Settings = request.app.state.settings
    return GitHubOAuthService(settings)


def get_analysis_job_repository(
    db: Session = Depends(get_db_session),
) -> AnalysisJobRepository:
    return AnalysisJobRepository(db)


def get_analysis_job_service(
    repository: AnalysisJobRepository = Depends(get_analysis_job_repository),
) -> AnalysisJobService:
    return AnalysisJobService(repository)


def get_analysis_event_service() -> AnalysisEventService:
    return AnalysisEventService()
