"""create repository snapshots and analysis jobs

Revision ID: 20260415_0001
Revises:
Create Date: 2026-04-15
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260415_0001"
down_revision: Optional[str] = None
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.create_table(
        "repository_snapshots",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("github_repo_id", sa.Integer(), nullable=True),
        sa.Column("full_name", sa.String(length=256), nullable=False),
        sa.Column("owner_type", sa.String(length=64), nullable=False),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.Column("default_branch", sa.String(length=128), nullable=False),
        sa.Column("html_url", sa.String(length=512), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "full_name", name="uq_repository_snapshot_user_full_name"),
    )
    op.create_index(
        op.f("ix_repository_snapshots_full_name"),
        "repository_snapshots",
        ["full_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_repository_snapshots_user_id"),
        "repository_snapshots",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("repository_snapshot_id", sa.String(length=64), nullable=False),
        sa.Column("repository_full_name", sa.String(length=256), nullable=False),
        sa.Column("branch", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(length=1024), nullable=True),
        sa.Column("result_id", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["repository_snapshot_id"], ["repository_snapshots.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analysis_jobs_repository_full_name"),
        "analysis_jobs",
        ["repository_full_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analysis_jobs_repository_snapshot_id"),
        "analysis_jobs",
        ["repository_snapshot_id"],
        unique=False,
    )
    op.create_index(op.f("ix_analysis_jobs_status"), "analysis_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_analysis_jobs_user_id"), "analysis_jobs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analysis_jobs_user_id"), table_name="analysis_jobs")
    op.drop_index(op.f("ix_analysis_jobs_status"), table_name="analysis_jobs")
    op.drop_index(op.f("ix_analysis_jobs_repository_snapshot_id"), table_name="analysis_jobs")
    op.drop_index(op.f("ix_analysis_jobs_repository_full_name"), table_name="analysis_jobs")
    op.drop_table("analysis_jobs")
    op.drop_index(op.f("ix_repository_snapshots_user_id"), table_name="repository_snapshots")
    op.drop_index(op.f("ix_repository_snapshots_full_name"), table_name="repository_snapshots")
    op.drop_table("repository_snapshots")
