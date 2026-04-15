from __future__ import annotations

from typing import Optional

from app.api.schemas import (
    AnalysisJobCreateRequest,
    AnalysisJobEventResponse,
    AnalysisJobProgressResponse,
    AnalysisJobResponse,
    AnalysisRunResponse,
    EvidenceSummaryResponse,
)
from app.github_oauth import GitHubOAuthError, GitHubOAuthService
from app.models import AnalysisJob, utc_now
from app.repositories.analysis_jobs import AnalysisJobRepository


class AnalysisJobService:
    """Business use cases for analysis jobs and evidence ingestion."""

    def __init__(self, repository: AnalysisJobRepository) -> None:
        self.repository = repository

    def create_job_for_repository(
        self,
        user_id: str,
        payload: AnalysisJobCreateRequest,
    ) -> AnalysisJobResponse:
        repository = self.repository.upsert_repository_snapshot(user_id, payload)
        job = self.repository.add_analysis_job(user_id, repository, payload)
        self.repository.commit()
        self.repository.refresh_job(job)
        return self.build_analysis_job_response(job)

    def get_owned_job(self, user_id: str, job_id: str) -> Optional[AnalysisJob]:
        return self.repository.get_owned_job(user_id, job_id)

    def get_owned_job_response(self, user_id: str, job_id: str) -> Optional[AnalysisJobResponse]:
        job = self.get_owned_job(user_id, job_id)
        return self.build_analysis_job_response(job) if job else None

    async def run_job_with_github(
        self,
        job: AnalysisJob,
        github: GitHubOAuthService,
        access_token: str,
    ) -> AnalysisRunResponse:
        self.repository.clear_run_artifacts(job)
        job.status = "running"
        job.current_stage = "starting"
        job.progress_percent = 0
        job.started_at = utc_now()
        job.completed_at = None
        job.failure_reason = None
        self.repository.append_event(
            job,
            event_type="job_started",
            stage="starting",
            percent=0,
            message="Analysis job started.",
        )
        self.repository.commit()
        self.repository.refresh_job(job)

        try:
            evidence_items = await github.collect_repository_evidence(
                access_token,
                full_name=job.repository_full_name,
                branch=job.branch,
            )
        except GitHubOAuthError as error_response:
            self.mark_job_failed(job, error_response.message, payload={"code": error_response.code})
            raise

        counts: dict[str, int] = {}
        for item in evidence_items:
            counts[item.source_type] = counts.get(item.source_type, 0) + 1
            self.repository.add_evidence(
                job,
                source_type=item.source_type,
                source_id=item.source_id,
                url=item.url,
                payload=item.payload,
            )

        for stage_name, percent, source_type in [
            ("collecting_commits", 20, "commit"),
            ("collecting_pull_requests", 40, "pull_request"),
            ("collecting_issues", 60, "issue"),
            ("collecting_reviews", 80, "review"),
            ("collecting_changed_files", 90, "changed_file"),
        ]:
            self.repository.append_event(
                job,
                event_type="progress",
                stage=stage_name,
                percent=percent,
                message=f"Collected {counts.get(source_type, 0)} {source_type} evidence item(s).",
                payload={"source_type": source_type, "count": counts.get(source_type, 0)},
            )

        job.status = "completed"
        job.current_stage = "completed"
        job.progress_percent = 100
        job.completed_at = utc_now()
        self.repository.append_event(
            job,
            event_type="job_completed",
            stage="completed",
            percent=100,
            message="Analysis evidence ingestion completed.",
            payload={"counts": counts, "total_count": len(evidence_items)},
        )
        self.repository.commit()
        self.repository.refresh_job(job)

        return AnalysisRunResponse(
            job=self.build_analysis_job_response(job),
            evidence=self.build_evidence_summary(job),
        )

    def mark_job_failed(
        self,
        job: AnalysisJob,
        failure_reason: str,
        *,
        payload: Optional[dict] = None,
    ) -> None:
        job.status = "failed"
        job.current_stage = "failed"
        job.progress_percent = 100
        job.failure_reason = failure_reason
        job.completed_at = utc_now()
        self.repository.append_event(
            job,
            event_type="job_failed",
            stage="failed",
            percent=100,
            message=failure_reason,
            payload=payload,
        )
        self.repository.commit()

    def build_evidence_summary(self, job: AnalysisJob) -> EvidenceSummaryResponse:
        counts = self.repository.count_evidence_by_type(job)
        latest_events = self.repository.list_latest_events(job)

        return EvidenceSummaryResponse(
            job_id=job.id,
            total_count=sum(counts.values()),
            counts=counts,
            latest_events=[
                AnalysisJobEventResponse(
                    sequence=event.sequence,
                    event_type=event.event_type,
                    stage=event.stage,
                    percent=event.percent,
                    message=event.message,
                    payload_json=event.payload_json,
                    created_at=event.created_at.isoformat(),
                )
                for event in latest_events
            ],
        )

    @staticmethod
    def build_analysis_job_response(job: AnalysisJob) -> AnalysisJobResponse:
        progress_by_status = {
            "queued": AnalysisJobProgressResponse(stage="queued", percent=0),
            "running": AnalysisJobProgressResponse(
                stage=job.current_stage or "running",
                percent=job.progress_percent or 10,
            ),
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
