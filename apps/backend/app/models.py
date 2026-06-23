from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class Base(DeclarativeBase):
    pass


class RepositorySnapshot(Base):
    __tablename__ = "repository_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "full_name", name="uq_repository_snapshot_user_full_name"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    github_repo_id: Mapped[Optional[int]]
    full_name: Mapped[str] = mapped_column(String(256), index=True)
    owner_type: Mapped[str] = mapped_column(String(64), default="Unknown")
    private: Mapped[bool] = mapped_column(Boolean, default=False)
    default_branch: Mapped[str] = mapped_column(String(128), default="")
    html_url: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[Optional[str]] = mapped_column(String(1024))
    last_synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(back_populates="repository_snapshot")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    repository_snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("repository_snapshots.id"),
        index=True,
    )
    repository_full_name: Mapped[str] = mapped_column(String(256), index=True)
    branch: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    current_stage: Mapped[str] = mapped_column(String(64), default="queued")
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[Optional[str]] = mapped_column(String(1024))
    result_id: Mapped[Optional[str]] = mapped_column(String(64))

    repository_snapshot: Mapped[RepositorySnapshot] = relationship(back_populates="analysis_jobs")
    evidence: Mapped[list["AnalysisEvidence"]] = relationship(
        back_populates="analysis_job",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["AnalysisJobEvent"]] = relationship(
        back_populates="analysis_job",
        cascade="all, delete-orphan",
    )
    results: Mapped[list["PortfolioResult"]] = relationship(
        back_populates="analysis_job",
        cascade="all, delete-orphan",
    )


class AnalysisEvidence(Base):
    __tablename__ = "analysis_evidence"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    analysis_job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    source_id: Mapped[str] = mapped_column(String(256))
    url: Mapped[str] = mapped_column(String(512), default="")
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    analysis_job: Mapped[AnalysisJob] = relationship(back_populates="evidence")


class AnalysisJobEvent(Base):
    __tablename__ = "analysis_job_events"
    __table_args__ = (
        UniqueConstraint("analysis_job_id", "sequence", name="uq_analysis_job_events_job_sequence"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    analysis_job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), index=True)
    sequence: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    stage: Mapped[str] = mapped_column(String(64), default="")
    percent: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(512), default="")
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    analysis_job: Mapped[AnalysisJob] = relationship(back_populates="events")


class PortfolioResult(Base):
    __tablename__ = "portfolio_results"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    analysis_job_id: Mapped[str] = mapped_column(ForeignKey("analysis_jobs.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    repository_full_name: Mapped[str] = mapped_column(String(256), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    headline: Mapped[str] = mapped_column(String(256), default="")
    project_overview: Mapped[str] = mapped_column(Text, default="")
    role_summary: Mapped[str] = mapped_column(Text, default="")
    key_contributions: Mapped[list] = mapped_column(JSON, default=list)
    tech_stack: Mapped[list] = mapped_column(JSON, default=list)
    evidence_summary: Mapped[str] = mapped_column(Text, default="")
    interview_questions: Mapped[list] = mapped_column(JSON, default=list)
    enhancement_status: Mapped[str] = mapped_column(String(32), default="not_configured")
    enhancement_model: Mapped[Optional[str]] = mapped_column(String(128))
    enhancement_message: Mapped[str] = mapped_column(String(256), default="기본 생성 사용")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    analysis_job: Mapped[AnalysisJob] = relationship(back_populates="results")
    evidence_links: Mapped[list["PortfolioSectionEvidenceLink"]] = relationship(
        back_populates="portfolio_result",
        cascade="all, delete-orphan",
    )


class PortfolioSectionEvidenceLink(Base):
    __tablename__ = "portfolio_section_evidence_links"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    portfolio_result_id: Mapped[str] = mapped_column(ForeignKey("portfolio_results.id"), index=True)
    evidence_id: Mapped[str] = mapped_column(ForeignKey("analysis_evidence.id"), index=True)
    section_key: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(256), default="")
    url: Mapped[str] = mapped_column(String(512), default="")

    portfolio_result: Mapped[PortfolioResult] = relationship(back_populates="evidence_links")
    evidence: Mapped[AnalysisEvidence] = relationship()
