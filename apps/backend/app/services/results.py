from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Optional

from app.api.schemas import (
    PortfolioEvidenceLinkResponse,
    PortfolioResultListItemResponse,
    PortfolioResultListResponse,
    PortfolioResultResponse,
    PortfolioResultUpdateRequest,
)
from app.models import AnalysisEvidence, AnalysisJob, PortfolioResult, utc_now
from app.repositories.analysis_jobs import AnalysisJobRepository
from app.repositories.results import PortfolioResultRepository


@dataclass(frozen=True)
class ResultDraft:
    headline: str
    project_overview: str
    role_summary: str
    key_contributions: list[str]
    tech_stack: list[str]
    evidence_summary: str
    interview_questions: list[str]


class PortfolioResultService:
    """Rule-based portfolio result generation and read use cases."""

    def __init__(
        self,
        analysis_jobs: AnalysisJobRepository,
        results: PortfolioResultRepository,
    ) -> None:
        self.analysis_jobs = analysis_jobs
        self.results = results

    def generate_for_job(self, user_id: str, job_id: str) -> Optional[PortfolioResultResponse]:
        job = self.analysis_jobs.get_owned_job(user_id, job_id)
        if not job or job.status != "completed":
            return None

        evidence = self.results.list_evidence_for_job(job.id)
        draft = build_result_draft(job, evidence)
        result = self.results.add_result(
            analysis_job_id=job.id,
            user_id=user_id,
            repository_full_name=job.repository_full_name,
            headline=draft.headline,
            project_overview=draft.project_overview,
            role_summary=draft.role_summary,
            key_contributions=draft.key_contributions,
            tech_stack=draft.tech_stack,
            evidence_summary=draft.evidence_summary,
            interview_questions=draft.interview_questions,
        )
        self.results.commit()
        self.results.refresh_result(result)

        for section_key, section_evidence in pick_section_evidence(evidence).items():
            for item in section_evidence:
                self.results.add_evidence_link(
                    result=result,
                    evidence=item,
                    section_key=section_key,
                    label=build_evidence_label(item),
                    url=item.url,
                )

        job.result_id = result.id
        self.results.commit()
        self.results.refresh_result(result)
        return self.build_result_response(result)

    def list_results(self, user_id: str) -> PortfolioResultListResponse:
        return PortfolioResultListResponse(
            items=[self.build_result_list_item(result) for result in self.results.list_owned_results(user_id)]
        )

    def get_result(self, user_id: str, result_id: str) -> Optional[PortfolioResultResponse]:
        result = self.results.get_owned_result(user_id, result_id)
        return self.build_result_response(result) if result else None

    def update_result(
        self,
        user_id: str,
        result_id: str,
        payload: PortfolioResultUpdateRequest,
    ) -> Optional[PortfolioResultResponse]:
        result = self.results.get_owned_result(user_id, result_id)
        if not result:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(result, field, value)
        result.updated_at = utc_now()
        self.results.commit()
        self.results.refresh_result(result)
        return self.build_result_response(result)

    def regenerate_result(self, user_id: str, result_id: str) -> Optional[PortfolioResultResponse]:
        source_result = self.results.get_owned_result(user_id, result_id)
        if not source_result:
            return None

        job = self.analysis_jobs.get_owned_job(user_id, source_result.analysis_job_id)
        if not job or job.status != "completed":
            return None

        evidence = self.results.list_evidence_for_job(job.id)
        draft = build_result_draft(job, evidence)
        next_version = self.results.get_max_version_for_job(job.id) + 1
        result = self.results.add_result(
            analysis_job_id=job.id,
            user_id=user_id,
            repository_full_name=job.repository_full_name,
            headline=draft.headline,
            project_overview=draft.project_overview,
            role_summary=draft.role_summary,
            key_contributions=draft.key_contributions,
            tech_stack=draft.tech_stack,
            evidence_summary=draft.evidence_summary,
            interview_questions=draft.interview_questions,
            version=next_version,
        )
        self.results.commit()
        self.results.refresh_result(result)

        for section_key, section_evidence in pick_section_evidence(evidence).items():
            for item in section_evidence:
                self.results.add_evidence_link(
                    result=result,
                    evidence=item,
                    section_key=section_key,
                    label=build_evidence_label(item),
                    url=item.url,
                )

        job.result_id = result.id
        self.results.commit()
        self.results.refresh_result(result)
        return self.build_result_response(result)

    @staticmethod
    def build_result_response(result: PortfolioResult) -> PortfolioResultResponse:
        return PortfolioResultResponse(
            result_id=result.id,
            analysis_job_id=result.analysis_job_id,
            repository_full_name=result.repository_full_name,
            version=result.version,
            headline=result.headline,
            project_overview=result.project_overview,
            role_summary=result.role_summary,
            key_contributions=list(result.key_contributions),
            tech_stack=list(result.tech_stack),
            evidence_summary=result.evidence_summary,
            interview_questions=list(result.interview_questions),
            evidence_links=[
                PortfolioEvidenceLinkResponse(
                    section_key=link.section_key,
                    label=link.label,
                    url=link.url,
                    evidence_id=link.evidence_id,
                )
                for link in result.evidence_links
            ],
            created_at=result.created_at.isoformat(),
            updated_at=result.updated_at.isoformat(),
        )

    @staticmethod
    def build_result_list_item(result: PortfolioResult) -> PortfolioResultListItemResponse:
        return PortfolioResultListItemResponse(
            result_id=result.id,
            analysis_job_id=result.analysis_job_id,
            repository_full_name=result.repository_full_name,
            headline=result.headline,
            version=result.version,
            created_at=result.created_at.isoformat(),
            updated_at=result.updated_at.isoformat(),
        )


def build_result_draft(job: AnalysisJob, evidence: list[AnalysisEvidence]) -> ResultDraft:
    counts = Counter(item.source_type for item in evidence)
    repository_name = job.repository_full_name
    tech_stack = infer_tech_stack(evidence)
    contribution_titles = extract_contribution_titles(evidence)
    total_count = sum(counts.values())

    headline = f"{repository_name}에서 근거 기반 개발 흐름을 완성한 프로젝트 경험"
    project_overview = (
        f"{repository_name} 저장소의 commit, pull request, issue, review, changed file 근거 {total_count}개를 "
        "수집해 프로젝트 활동을 포트폴리오 문서로 재구성했습니다."
    )
    role_summary = (
        "저장소 활동 전반을 분석해 기능 구현, 변경 이력, 협업 흔적, 코드 변경 범위를 연결하는 "
        "실행 중심 역할을 수행했습니다."
    )
    key_contributions = contribution_titles or [
        "GitHub 활동 데이터를 수집하고 포트폴리오 결과로 변환할 수 있는 기반을 마련했습니다.",
        "분석 job과 evidence 저장 흐름을 통해 재생성 가능한 근거 구조를 확보했습니다.",
        "진행 상태와 결과 조회 흐름을 사용자 화면에 연결했습니다.",
    ]
    evidence_summary = ", ".join(f"{source_type} {count}개" for source_type, count in sorted(counts.items()))
    if not evidence_summary:
        evidence_summary = "저장된 evidence가 없어 기본 프로젝트 설명 중심으로 결과를 생성했습니다."

    interview_questions = [
        "이 프로젝트에서 가장 중요한 기술적 의사결정은 무엇이었나요?",
        "수집된 GitHub evidence 중 본인의 기여를 가장 잘 보여주는 근거는 무엇인가요?",
        "비슷한 분석/포트폴리오 자동화 기능을 다시 만든다면 어떤 구조를 개선하겠나요?",
    ]

    return ResultDraft(
        headline=headline,
        project_overview=project_overview,
        role_summary=role_summary,
        key_contributions=key_contributions[:5],
        tech_stack=tech_stack,
        evidence_summary=evidence_summary,
        interview_questions=interview_questions,
    )


def pick_section_evidence(evidence: list[AnalysisEvidence]) -> dict[str, list[AnalysisEvidence]]:
    by_type: dict[str, list[AnalysisEvidence]] = {}
    for item in evidence:
        by_type.setdefault(item.source_type, []).append(item)

    return {
        "key_contributions": (by_type.get("pull_request") or by_type.get("commit") or evidence)[:3],
        "tech_stack": (by_type.get("changed_file") or evidence)[:3],
        "evidence_summary": evidence[:5],
    }


def extract_contribution_titles(evidence: list[AnalysisEvidence]) -> list[str]:
    contributions: list[str] = []

    for item in evidence:
        payload = item.payload_json
        title = payload.get("title") or payload.get("message") or payload.get("filename")
        if title:
            contributions.append(f"{title} 작업을 통해 {item.source_type} 근거를 남겼습니다.")

    return contributions


def infer_tech_stack(evidence: list[AnalysisEvidence]) -> list[str]:
    extension_map = {
        ".py": "Python",
        ".ts": "TypeScript",
        ".tsx": "React",
        ".js": "JavaScript",
        ".jsx": "React",
        ".css": "CSS",
        ".md": "Markdown",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".toml": "TOML",
        ".json": "JSON",
    }
    stack: list[str] = []

    for item in evidence:
        filename = str(item.payload_json.get("filename") or "")
        suffix = PurePosixPath(filename).suffix
        value = extension_map.get(suffix)
        if value and value not in stack:
            stack.append(value)

    if not stack:
        stack = ["GitHub", "FastAPI", "React"]

    return stack[:8]


def build_evidence_label(evidence: AnalysisEvidence) -> str:
    payload = evidence.payload_json
    title = payload.get("title") or payload.get("message") or payload.get("filename") or evidence.source_id
    return f"{evidence.source_type}: {title}"
