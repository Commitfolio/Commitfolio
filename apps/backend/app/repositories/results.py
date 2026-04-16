from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    AnalysisEvidence,
    PortfolioResult,
    PortfolioSectionEvidenceLink,
    prefixed_id,
    utc_now,
)


class PortfolioResultRepository:
    """Persistence layer for generated portfolio results."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def refresh_result(self, result: PortfolioResult) -> None:
        self.db.refresh(result)

    def list_evidence_for_job(self, job_id: str) -> list[AnalysisEvidence]:
        return self.db.scalars(
            select(AnalysisEvidence)
            .where(AnalysisEvidence.analysis_job_id == job_id)
            .order_by(AnalysisEvidence.created_at, AnalysisEvidence.id)
        ).all()

    def add_result(
        self,
        *,
        analysis_job_id: str,
        user_id: str,
        repository_full_name: str,
        headline: str,
        project_overview: str,
        role_summary: str,
        key_contributions: list[str],
        tech_stack: list[str],
        evidence_summary: str,
        interview_questions: list[str],
        enhancement_status: str = "not_configured",
        enhancement_model: Optional[str] = None,
        enhancement_message: str = "기본 생성 사용",
        version: int = 1,
    ) -> PortfolioResult:
        now = utc_now()
        result = PortfolioResult(
            id=prefixed_id("res"),
            analysis_job_id=analysis_job_id,
            user_id=user_id,
            repository_full_name=repository_full_name,
            version=version,
            headline=headline,
            project_overview=project_overview,
            role_summary=role_summary,
            key_contributions=key_contributions,
            tech_stack=tech_stack,
            evidence_summary=evidence_summary,
            interview_questions=interview_questions,
            enhancement_status=enhancement_status,
            enhancement_model=enhancement_model,
            enhancement_message=enhancement_message,
            created_at=now,
            updated_at=now,
        )
        self.db.add(result)
        return result

    def add_evidence_link(
        self,
        *,
        result: PortfolioResult,
        evidence: AnalysisEvidence,
        section_key: str,
        label: str,
        url: str,
    ) -> PortfolioSectionEvidenceLink:
        link = PortfolioSectionEvidenceLink(
            id=prefixed_id("link"),
            portfolio_result_id=result.id,
            evidence_id=evidence.id,
            section_key=section_key,
            label=label,
            url=url,
        )
        self.db.add(link)
        return link



    def get_max_version_for_job(self, analysis_job_id: str) -> int:
        return int(
            self.db.scalar(
                select(func.max(PortfolioResult.version)).where(
                    PortfolioResult.analysis_job_id == analysis_job_id,
                )
            )
            or 0
        )

    def get_owned_result(self, user_id: str, result_id: str) -> Optional[PortfolioResult]:
        return self.db.scalar(
            select(PortfolioResult)
            .options(selectinload(PortfolioResult.evidence_links))
            .where(PortfolioResult.id == result_id, PortfolioResult.user_id == user_id)
        )

    def list_owned_results(self, user_id: str, *, limit: int = 20) -> list[PortfolioResult]:
        return self.db.scalars(
            select(PortfolioResult)
            .where(PortfolioResult.user_id == user_id)
            .order_by(PortfolioResult.created_at.desc())
            .limit(limit)
        ).all()
