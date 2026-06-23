from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultDraft:
    headline: str
    project_overview: str
    role_summary: str
    key_contributions: list[str]
    tech_stack: list[str]
    evidence_summary: str
    interview_questions: list[str]
