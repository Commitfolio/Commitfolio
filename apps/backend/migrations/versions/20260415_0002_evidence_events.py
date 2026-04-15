"""add analysis evidence and job events

Revision ID: 20260415_0002
Revises: 20260415_0001
Create Date: 2026-04-15
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260415_0002"
down_revision: Optional[str] = "20260415_0001"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.add_column(
        "analysis_jobs",
        sa.Column("current_stage", sa.String(length=64), nullable=False, server_default="queued"),
    )
    op.add_column(
        "analysis_jobs",
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "analysis_evidence",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("analysis_job_id", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=256), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_job_id"], ["analysis_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analysis_evidence_analysis_job_id"),
        "analysis_evidence",
        ["analysis_job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analysis_evidence_source_type"),
        "analysis_evidence",
        ["source_type"],
        unique=False,
    )

    op.create_table(
        "analysis_job_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("analysis_job_id", sa.String(length=64), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("percent", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(length=512), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_job_id"], ["analysis_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("analysis_job_id", "sequence", name="uq_analysis_job_events_job_sequence"),
    )
    op.create_index(
        op.f("ix_analysis_job_events_analysis_job_id"),
        "analysis_job_events",
        ["analysis_job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analysis_job_events_event_type"),
        "analysis_job_events",
        ["event_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_analysis_job_events_event_type"), table_name="analysis_job_events")
    op.drop_index(
        op.f("ix_analysis_job_events_analysis_job_id"),
        table_name="analysis_job_events",
    )
    op.drop_table("analysis_job_events")
    op.drop_index(op.f("ix_analysis_evidence_source_type"), table_name="analysis_evidence")
    op.drop_index(
        op.f("ix_analysis_evidence_analysis_job_id"),
        table_name="analysis_evidence",
    )
    op.drop_table("analysis_evidence")
    op.drop_column("analysis_jobs", "progress_percent")
    op.drop_column("analysis_jobs", "current_stage")
