from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import AnalysisJobCreateRequest
from app.models import AnalysisEvidence, AnalysisJob, AnalysisJobEvent, RepositorySnapshot, prefixed_id, utc_now


class AnalysisJobRepository:
    """Persistence layer for analysis jobs, evidence, and replay events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def flush(self) -> None:
        self.db.flush()

    def refresh_job(self, job: AnalysisJob) -> None:
        self.db.refresh(job)

    def upsert_repository_snapshot(
        self,
        user_id: str,
        payload: AnalysisJobCreateRequest,
    ) -> RepositorySnapshot:
        repository = self.db.scalar(
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
            self.db.add(repository)

        repository.github_repo_id = payload.github_repo_id
        repository.private = payload.private
        repository.owner_type = payload.owner_type or "Unknown"
        repository.default_branch = payload.default_branch or payload.branch or "main"
        repository.html_url = payload.html_url
        repository.description = payload.description
        repository.last_synced_at = utc_now()

        self.db.flush()
        return repository

    def add_analysis_job(
        self,
        user_id: str,
        repository: RepositorySnapshot,
        payload: AnalysisJobCreateRequest,
    ) -> AnalysisJob:
        job = AnalysisJob(
            id=prefixed_id("job"),
            user_id=user_id,
            repository_snapshot_id=repository.id,
            repository_full_name=repository.full_name,
            branch=payload.branch or repository.default_branch,
            status="queued",
            current_stage="queued",
            progress_percent=0,
            requested_at=utc_now(),
        )
        self.db.add(job)
        return job

    def get_owned_job(self, user_id: str, job_id: str) -> Optional[AnalysisJob]:
        return self.db.scalar(
            select(AnalysisJob).where(
                AnalysisJob.id == job_id,
                AnalysisJob.user_id == user_id,
            )
        )

    def clear_run_artifacts(self, job: AnalysisJob) -> None:
        self.db.query(AnalysisEvidence).filter(AnalysisEvidence.analysis_job_id == job.id).delete()
        self.db.query(AnalysisJobEvent).filter(AnalysisJobEvent.analysis_job_id == job.id).delete()
        self.db.flush()

    def add_evidence(
        self,
        job: AnalysisJob,
        *,
        source_type: str,
        source_id: str,
        url: str,
        payload: dict,
    ) -> AnalysisEvidence:
        evidence = AnalysisEvidence(
            id=prefixed_id("ev"),
            analysis_job_id=job.id,
            source_type=source_type,
            source_id=source_id,
            url=url,
            payload_json=payload,
            created_at=utc_now(),
        )
        self.db.add(evidence)
        return evidence

    def append_event(
        self,
        job: AnalysisJob,
        *,
        event_type: str,
        stage: str,
        percent: int,
        message: str,
        payload: Optional[dict] = None,
    ) -> AnalysisJobEvent:
        sequence = (
            self.db.scalar(
                select(func.max(AnalysisJobEvent.sequence)).where(
                    AnalysisJobEvent.analysis_job_id == job.id,
                )
            )
            or 0
        ) + 1
        event = AnalysisJobEvent(
            id=prefixed_id("evt"),
            analysis_job_id=job.id,
            sequence=sequence,
            event_type=event_type,
            stage=stage,
            percent=percent,
            message=message,
            payload_json=payload or {},
            created_at=utc_now(),
        )
        self.db.add(event)
        self.db.flush()
        return event

    def count_evidence_by_type(self, job: AnalysisJob) -> dict[str, int]:
        rows = self.db.execute(
            select(AnalysisEvidence.source_type, func.count(AnalysisEvidence.id))
            .where(AnalysisEvidence.analysis_job_id == job.id)
            .group_by(AnalysisEvidence.source_type)
        ).all()
        return {str(source_type): int(count) for source_type, count in rows}

    def list_latest_events(self, job: AnalysisJob, *, limit: int = 8) -> list[AnalysisJobEvent]:
        return list(
            reversed(
                self.db.scalars(
                    select(AnalysisJobEvent)
                    .where(AnalysisJobEvent.analysis_job_id == job.id)
                    .order_by(AnalysisJobEvent.sequence.desc())
                    .limit(limit)
                ).all()
            )
        )

    def list_events_after(
        self,
        *,
        job_id: str,
        last_sequence: int,
        limit: int = 50,
    ) -> list[AnalysisJobEvent]:
        return self.db.scalars(
            select(AnalysisJobEvent)
            .where(
                AnalysisJobEvent.analysis_job_id == job_id,
                AnalysisJobEvent.sequence > last_sequence,
            )
            .order_by(AnalysisJobEvent.sequence)
            .limit(limit)
        ).all()
