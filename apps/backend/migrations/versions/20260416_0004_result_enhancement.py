"""add result enhancement metadata

Revision ID: 20260416_0004
Revises: 20260415_0003
Create Date: 2026-04-16
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260416_0004"
down_revision: Optional[str] = "20260415_0003"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.add_column(
        "portfolio_results",
        sa.Column(
            "enhancement_status",
            sa.String(length=32),
            nullable=False,
            server_default="not_configured",
        ),
    )
    op.add_column(
        "portfolio_results",
        sa.Column("enhancement_model", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "portfolio_results",
        sa.Column(
            "enhancement_message",
            sa.String(length=256),
            nullable=False,
            server_default="기본 생성 사용",
        ),
    )


def downgrade() -> None:
    op.drop_column("portfolio_results", "enhancement_message")
    op.drop_column("portfolio_results", "enhancement_model")
    op.drop_column("portfolio_results", "enhancement_status")
