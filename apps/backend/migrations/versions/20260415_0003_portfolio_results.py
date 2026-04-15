"""add portfolio results

Revision ID: 20260415_0003
Revises: 20260415_0002
Create Date: 2026-04-15
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260415_0003"
down_revision: Optional[str] = "20260415_0002"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.create_table(
        "portfolio_results",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("analysis_job_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("repository_full_name", sa.String(length=256), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("headline", sa.String(length=256), nullable=False),
        sa.Column("project_overview", sa.Text(), nullable=False),
        sa.Column("role_summary", sa.Text(), nullable=False),
        sa.Column("key_contributions", sa.JSON(), nullable=False),
        sa.Column("tech_stack", sa.JSON(), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=False),
        sa.Column("interview_questions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_job_id"], ["analysis_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portfolio_results_analysis_job_id"), "portfolio_results", ["analysis_job_id"], unique=False)
    op.create_index(op.f("ix_portfolio_results_repository_full_name"), "portfolio_results", ["repository_full_name"], unique=False)
    op.create_index(op.f("ix_portfolio_results_user_id"), "portfolio_results", ["user_id"], unique=False)

    op.create_table(
        "portfolio_section_evidence_links",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("portfolio_result_id", sa.String(length=64), nullable=False),
        sa.Column("evidence_id", sa.String(length=64), nullable=False),
        sa.Column("section_key", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=256), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.ForeignKeyConstraint(["evidence_id"], ["analysis_evidence.id"]),
        sa.ForeignKeyConstraint(["portfolio_result_id"], ["portfolio_results.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_portfolio_section_evidence_links_evidence_id"),
        "portfolio_section_evidence_links",
        ["evidence_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_section_evidence_links_portfolio_result_id"),
        "portfolio_section_evidence_links",
        ["portfolio_result_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_section_evidence_links_section_key"),
        "portfolio_section_evidence_links",
        ["section_key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_portfolio_section_evidence_links_section_key"), table_name="portfolio_section_evidence_links")
    op.drop_index(
        op.f("ix_portfolio_section_evidence_links_portfolio_result_id"),
        table_name="portfolio_section_evidence_links",
    )
    op.drop_index(op.f("ix_portfolio_section_evidence_links_evidence_id"), table_name="portfolio_section_evidence_links")
    op.drop_table("portfolio_section_evidence_links")
    op.drop_index(op.f("ix_portfolio_results_user_id"), table_name="portfolio_results")
    op.drop_index(op.f("ix_portfolio_results_repository_full_name"), table_name="portfolio_results")
    op.drop_index(op.f("ix_portfolio_results_analysis_job_id"), table_name="portfolio_results")
    op.drop_table("portfolio_results")
