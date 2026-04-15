from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
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
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[Optional[str]] = mapped_column(String(1024))
    result_id: Mapped[Optional[str]] = mapped_column(String(64))

    repository_snapshot: Mapped[RepositorySnapshot] = relationship(back_populates="analysis_jobs")
