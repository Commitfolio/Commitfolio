from __future__ import annotations

from typing import Optional, TypedDict

from pydantic import BaseModel


class SessionUser(TypedDict):
    id: str
    github_login: str
    connected: bool
    name: Optional[str]
    avatar_url: Optional[str]


class MeResponse(BaseModel):
    id: str
    github_login: str
    connected: bool
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class RepositoryPermissionsResponse(BaseModel):
    admin: bool
    push: bool
    pull: bool


class RepositoryResponse(BaseModel):
    id: int
    full_name: str
    private: bool
    owner_type: str
    default_branch: str
    permissions: RepositoryPermissionsResponse
    html_url: str
    description: Optional[str] = None
    updated_at: Optional[str] = None


class RepositoryListResponse(BaseModel):
    items: list[RepositoryResponse]
    next_cursor: Optional[str] = None


class AnalysisJobCreateRequest(BaseModel):
    repository_full_name: str
    branch: str = "main"
    github_repo_id: Optional[int] = None
    private: bool = False
    owner_type: str = "Unknown"
    default_branch: str = "main"
    html_url: str = ""
    description: Optional[str] = None


class AnalysisJobProgressResponse(BaseModel):
    stage: str
    percent: int


class AnalysisJobResponse(BaseModel):
    job_id: str
    status: str
    repository_full_name: str
    branch: str
    progress: AnalysisJobProgressResponse
    result_id: Optional[str] = None
    failure_reason: Optional[str] = None


class AnalysisJobEventResponse(BaseModel):
    sequence: int
    event_type: str
    stage: str
    percent: int
    message: str
    payload_json: dict
    created_at: str


class EvidenceSummaryResponse(BaseModel):
    job_id: str
    total_count: int
    counts: dict[str, int]
    latest_events: list[AnalysisJobEventResponse]


class AnalysisRunResponse(BaseModel):
    job: AnalysisJobResponse
    evidence: EvidenceSummaryResponse


class PortfolioEvidenceLinkResponse(BaseModel):
    section_key: str
    label: str
    url: str
    evidence_id: str


class PortfolioResultResponse(BaseModel):
    result_id: str
    analysis_job_id: str
    repository_full_name: str
    version: int
    headline: str
    project_overview: str
    role_summary: str
    key_contributions: list[str]
    tech_stack: list[str]
    evidence_summary: str
    interview_questions: list[str]
    evidence_links: list[PortfolioEvidenceLinkResponse]
    created_at: str
    updated_at: str


class PortfolioResultListItemResponse(BaseModel):
    result_id: str
    analysis_job_id: str
    repository_full_name: str
    headline: str
    version: int
    created_at: str
    updated_at: str


class PortfolioResultListResponse(BaseModel):
    items: list[PortfolioResultListItemResponse]


class PortfolioResultUpdateRequest(BaseModel):
    headline: Optional[str] = None
    project_overview: Optional[str] = None
    role_summary: Optional[str] = None
    key_contributions: Optional[list[str]] = None
    tech_stack: Optional[list[str]] = None
    evidence_summary: Optional[str] = None
    interview_questions: Optional[list[str]] = None
