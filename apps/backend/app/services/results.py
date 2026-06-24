from __future__ import annotations

from collections import Counter
from pathlib import PurePosixPath
import re
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
from app.services.result_draft import ResultDraft
from app.services.result_enhancement import NoOpResultEnhancer, ResultEnhancer


class PortfolioResultService:
    """Rule-based portfolio result generation and read use cases."""

    def __init__(
        self,
        analysis_jobs: AnalysisJobRepository,
        results: PortfolioResultRepository,
        enhancer: ResultEnhancer | None = None,
    ) -> None:
        self.analysis_jobs = analysis_jobs
        self.results = results
        self.enhancer = enhancer or NoOpResultEnhancer()

    def generate_for_job(self, user_id: str, job_id: str) -> Optional[PortfolioResultResponse]:
        job = self.analysis_jobs.get_owned_job(user_id, job_id)
        if not job or job.status != "completed":
            return None

        evidence = self.results.list_evidence_for_job(job.id)
        draft = build_result_draft(job, evidence)
        enhancement = self.enhancer.enhance(job=job, evidence=evidence, draft=draft)
        result = self.results.add_result(
            analysis_job_id=job.id,
            user_id=user_id,
            repository_full_name=job.repository_full_name,
            headline=enhancement.draft.headline,
            project_overview=enhancement.draft.project_overview,
            role_summary=enhancement.draft.role_summary,
            key_contributions=enhancement.draft.key_contributions,
            tech_stack=enhancement.draft.tech_stack,
            evidence_summary=enhancement.draft.evidence_summary,
            interview_questions=enhancement.draft.interview_questions,
            enhancement_status=enhancement.status,
            enhancement_model=enhancement.model,
            enhancement_message=enhancement.message,
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
        enhancement = self.enhancer.enhance(job=job, evidence=evidence, draft=draft)
        next_version = self.results.get_max_version_for_job(job.id) + 1
        result = self.results.add_result(
            analysis_job_id=job.id,
            user_id=user_id,
            repository_full_name=job.repository_full_name,
            headline=enhancement.draft.headline,
            project_overview=enhancement.draft.project_overview,
            role_summary=enhancement.draft.role_summary,
            key_contributions=enhancement.draft.key_contributions,
            tech_stack=enhancement.draft.tech_stack,
            evidence_summary=enhancement.draft.evidence_summary,
            interview_questions=enhancement.draft.interview_questions,
            enhancement_status=enhancement.status,
            enhancement_model=enhancement.model,
            enhancement_message=enhancement.message,
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
            enhancement_status=result.enhancement_status,
            enhancement_model=result.enhancement_model,
            enhancement_message=result.enhancement_message,
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
    repository_meta = extract_repository_meta(evidence)
    readme_text = extract_readme_text(evidence)
    structure_entries = extract_repository_structure_entries(evidence)
    tech_stack = infer_tech_stack(evidence, repository_meta=repository_meta, readme_text=readme_text, structure_entries=structure_entries)
    project_profile = infer_project_profile(tech_stack, readme_text=readme_text, structure_entries=structure_entries)
    contribution_titles = build_contribution_titles(
        evidence,
        project_profile=project_profile,
        readme_text=readme_text,
        structure_entries=structure_entries,
    )
    total_count = sum(counts.values())
    project_summary = build_project_summary(repository_name, repository_meta, readme_text, project_profile)
    role_summary = build_role_summary(project_profile, counts, tech_stack)

    headline = f"{repository_name}에서 {project_profile['headline_focus']} 구현 경험"
    project_overview = (
        f"{project_summary} "
        f"분석 과정에서는 GitHub 근거 {total_count}개를 연결해 사용 기술, 구현 기능, 협업 흔적을 포트폴리오 문서로 재구성했습니다."
    )
    key_contributions = contribution_titles or [
        f"{project_profile['implementation_focus']} 관련 구현 범위를 commit과 pull request 근거로 정리했습니다.",
        f"{project_profile['stack_focus']} 중심 기술 선택을 changed file과 repository structure 근거로 설명할 수 있게 만들었습니다.",
        "이슈, 리뷰, 변경 파일 근거를 함께 묶어 협업 과정과 품질 검토 흔적을 포트폴리오 서술에 반영했습니다.",
    ]
    evidence_summary = build_evidence_summary(counts, repository_meta, readme_text, tech_stack)

    interview_questions = build_interview_questions(project_profile, tech_stack)

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
        "project_overview": (
            by_type.get("readme")
            or by_type.get("repository_meta")
            or by_type.get("pull_request")
            or evidence
        )[:3],
        "role_summary": (
            by_type.get("pull_request")
            or by_type.get("review")
            or by_type.get("issue")
            or evidence
        )[:3],
        "key_contributions": (by_type.get("pull_request") or by_type.get("commit") or evidence)[:3],
        "tech_stack": (
            by_type.get("language")
            or by_type.get("repository_structure")
            or by_type.get("changed_file")
            or evidence
        )[:3],
        "evidence_summary": evidence[:5],
        "interview_questions": (
            by_type.get("readme")
            or by_type.get("pull_request")
            or by_type.get("issue")
            or evidence
        )[:3],
    }


def extract_repository_meta(evidence: list[AnalysisEvidence]) -> dict:
    for item in evidence:
        if item.source_type == "repository_meta" and isinstance(item.payload_json, dict):
            return item.payload_json
    return {}


def extract_readme_text(evidence: list[AnalysisEvidence]) -> str:
    for item in evidence:
        if item.source_type == "readme":
            content = item.payload_json.get("content")
            if isinstance(content, str):
                return content
    return ""


def extract_repository_structure_entries(evidence: list[AnalysisEvidence]) -> list[str]:
    for item in evidence:
        if item.source_type != "repository_structure":
            continue
        entries = item.payload_json.get("entries")
        if not isinstance(entries, list):
            continue
        names: list[str] = []
        for entry in entries:
            if isinstance(entry, dict) and isinstance(entry.get("name"), str):
                names.append(entry["name"])
        return names
    return []


def build_contribution_titles(
    evidence: list[AnalysisEvidence],
    *,
    project_profile: dict[str, str],
    readme_text: str,
    structure_entries: list[str],
) -> list[str]:
    contributions: list[str] = []
    feature_candidates = extract_feature_candidates(readme_text)
    pull_request_titles = extract_titles_by_source_type(evidence, "pull_request")
    commit_titles = extract_titles_by_source_type(evidence, "commit")
    issue_titles = extract_titles_by_source_type(evidence, "issue")
    changed_files = extract_changed_filenames(evidence)
    layer_summary = build_layer_summary(
        project_profile=project_profile,
        changed_files=changed_files,
        structure_entries=structure_entries,
        readme_text=readme_text,
    )

    for feature in feature_candidates[:2]:
        contributions.append(
            f"'{feature}' 흐름을 중심으로 기능을 확장하고, {layer_summary}까지 함께 정리해 사용자가 실제로 완료하는 흐름으로 연결했습니다."
        )

    for title in pull_request_titles[:2]:
        contributions.append(
            f"'{title}' 작업에서는 {project_profile['implementation_focus']} 구현을 진행하면서 {layer_summary}을 함께 다듬어 기능 단위 변경이 화면, 상태, 데이터 흐름까지 이어지도록 만들었습니다."
        )

    for title in commit_titles[:2]:
        contributions.append(
            f"'{title}' 변경을 통해 세부 구현과 운영 설정을 보강하고, {layer_summary} 관점에서 실제 동작에 필요한 마무리 작업까지 연결했습니다."
        )

    if project_profile["kind"] == "flutter":
        contributions.append(
            "Flutter/Dart 기반 모바일 앱 구조에서 화면 흐름, 상태 관리, 네트워크 연동, 플랫폼 권한 및 리소스 설정 근거를 함께 묶어 앱 구현 경험을 더 입체적으로 설명할 수 있게 했습니다."
        )
    elif project_profile["kind"] == "backend":
        contributions.append(
            "API, 데이터 모델, 서버 구조 변경을 commit과 changed file 근거로 연결하고, 요청 처리부터 저장 계층까지 이어지는 구현 범위를 한 문장 안에서 설명할 수 있게 했습니다."
        )
    elif project_profile["kind"] == "frontend":
        contributions.append(
            "UI 구조와 사용자 상호작용 변경을 changed file과 PR 근거로 연결하고, 컴포넌트 구성과 데이터 연결이 함께 움직였다는 점을 드러내도록 정리했습니다."
        )

    if issue_titles:
        contributions.append(
            f"이슈 '{issue_titles[0]}' 를 통해 요구사항 추적 흔적을 남기고, 구현 결과가 어떤 문제를 해결하려는 변경이었는지 협업 맥락까지 함께 설명할 수 있게 했습니다."
        )

    if {"android", "ios", "lib"} & {entry.lower() for entry in structure_entries}:
        contributions.append(
            "저장소 구조를 기준으로 앱 코드와 플랫폼별 설정 범위를 함께 설명해 구현 범위가 단순 기능 나열이 아니라 실제 코드 구조와 릴리즈 준비 단계까지 닿도록 만들었습니다."
        )

    return dedupe_preserve_order(contributions)[:5]


def extract_titles_by_source_type(evidence: list[AnalysisEvidence], source_type: str) -> list[str]:
    titles: list[str] = []

    for item in evidence:
        if item.source_type != source_type:
            continue
        payload = item.payload_json
        title = payload.get("title") or payload.get("message") or payload.get("filename")
        if isinstance(title, str) and title.strip():
            titles.append(clean_markdown_text(title))

    return dedupe_preserve_order(titles)


def extract_changed_filenames(evidence: list[AnalysisEvidence]) -> list[str]:
    filenames: list[str] = []
    for item in evidence:
        if item.source_type != "changed_file":
            continue
        filename = item.payload_json.get("filename")
        if isinstance(filename, str) and filename.strip():
            filenames.append(filename.strip())
    return dedupe_preserve_order(filenames)


def build_layer_summary(
    *,
    project_profile: dict[str, str],
    changed_files: list[str],
    structure_entries: list[str],
    readme_text: str,
) -> str:
    lowered_files = [value.lower() for value in changed_files]
    structure_set = {value.lower() for value in structure_entries}
    readme_lower = readme_text.lower()

    layer_labels: list[str] = []

    if any(token in path for path in lowered_files for token in ("widget", "screen", "page", "view", "ui", "presentation")):
        layer_labels.append("UI 컴포넌트와 화면 구성")
    if any(token in path for path in lowered_files for token in ("riverpod", "provider", "bloc", "state", "controller", "viewmodel")):
        layer_labels.append("상태 관리 로직")
    if any(token in path for path in lowered_files for token in ("repository", "datasource", "api", "client", "service", "network")):
        layer_labels.append("데이터 연동 계층")
    if any(token in path for path in lowered_files for token in ("router", "route", "navigation")):
        layer_labels.append("화면 이동 흐름")
    if any(token in path for path in lowered_files for token in ("android", "ios", "permission", "image_picker", "camera", "photo", "assets")):
        layer_labels.append("플랫폼 권한과 리소스 설정")

    if "riverpod" in readme_lower and "상태 관리 로직" not in layer_labels:
        layer_labels.append("상태 관리 로직")
    if any(keyword in readme_lower for keyword in ("api", "dio", "retrofit", "repository")) and "데이터 연동 계층" not in layer_labels:
        layer_labels.append("데이터 연동 계층")
    if {"android", "ios"} & structure_set and "플랫폼 권한과 리소스 설정" not in layer_labels:
        layer_labels.append("플랫폼 권한과 리소스 설정")
    if "lib" in structure_set and "UI 컴포넌트와 화면 구성" not in layer_labels and project_profile["kind"] == "flutter":
        layer_labels.append("UI 컴포넌트와 화면 구성")

    if not layer_labels:
        if project_profile["kind"] == "flutter":
            layer_labels = ["UI 컴포넌트와 화면 구성", "상태 관리 로직", "데이터 연동 계층"]
        elif project_profile["kind"] == "backend":
            layer_labels = ["API 계층", "데이터 모델", "서비스 로직"]
        elif project_profile["kind"] == "frontend":
            layer_labels = ["UI 컴포넌트와 화면 구성", "상태 관리 로직", "데이터 연동 계층"]
        else:
            layer_labels = ["핵심 구현 계층"]

    return join_korean_list(layer_labels[:4])


def join_korean_list(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return ", ".join(values[:-1]) + f"와 {values[-1]}"


def infer_tech_stack(
    evidence: list[AnalysisEvidence],
    *,
    repository_meta: dict,
    readme_text: str,
    structure_entries: list[str],
) -> list[str]:
    stack: list[str] = []
    languages = repository_meta.get("primary_language")
    if isinstance(languages, str) and languages.strip():
        stack.append(languages.strip())

    for item in evidence:
        if item.source_type == "language":
            payload_languages = item.payload_json.get("languages")
            if isinstance(payload_languages, dict):
                for language_name, _ in sorted(
                    payload_languages.items(),
                    key=lambda entry: entry[1] if isinstance(entry[1], int) else 0,
                    reverse=True,
                ):
                    if isinstance(language_name, str) and language_name not in stack:
                        stack.append(language_name)

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
        ".dart": "Dart",
    }

    for item in evidence:
        filename = str(item.payload_json.get("filename") or "")
        suffix = PurePosixPath(filename).suffix
        value = extension_map.get(suffix)
        if value and value not in stack:
            stack.append(value)

    readme_lower = readme_text.lower()
    structure_lower = {entry.lower() for entry in structure_entries}
    keyword_stack = [
        ("flutter", "Flutter"),
        ("riverpod", "Riverpod"),
        ("provider", "Provider"),
        ("bloc", "BLoC"),
        ("getx", "GetX"),
        ("go_router", "go_router"),
        ("dio", "Dio"),
        ("retrofit", "Retrofit"),
        ("freezed", "freezed"),
        ("firebase", "Firebase"),
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("alembic", "Alembic"),
        ("postgres", "PostgreSQL"),
        ("react", "React"),
        ("vite", "Vite"),
        ("zustand", "Zustand"),
        ("tanstack query", "TanStack Query"),
    ]

    for keyword, label in keyword_stack:
        if keyword in readme_lower and label not in stack:
            stack.append(label)

    if "pubspec.yaml" in structure_lower:
        for label in ["Flutter", "Dart"]:
            if label not in stack:
                stack.append(label)

    if {"android", "ios"} & structure_lower and "Flutter" in stack and "Android/iOS" not in stack:
        stack.append("Android/iOS")

    if not stack:
        stack = ["GitHub", "FastAPI", "React"]

    return stack[:8]


def infer_project_profile(
    tech_stack: list[str],
    *,
    readme_text: str,
    structure_entries: list[str],
) -> dict[str, str]:
    stack_set = {value.lower() for value in tech_stack}
    structure_set = {value.lower() for value in structure_entries}
    readme_lower = readme_text.lower()

    if (
        "flutter" in stack_set
        or "dart" in stack_set
        or "pubspec.yaml" in structure_set
        or ("android" in structure_set and "ios" in structure_set and "lib" in structure_set)
    ):
        return {
            "kind": "flutter",
            "headline_focus": "모바일 사용자 기능과 앱 구조",
            "implementation_focus": "모바일 사용자 기능과 화면 흐름",
            "stack_focus": "Flutter/Dart와 앱 아키텍처",
            "role_summary": "Flutter 기반 모바일 클라이언트에서 사용자 흐름, 화면 구조, 의존성 선택을 구현한 역할",
        }

    if "fastapi" in stack_set or "python" in stack_set or "server" in readme_lower:
        return {
            "kind": "backend",
            "headline_focus": "백엔드 기능과 API 흐름",
            "implementation_focus": "API와 서버 기능",
            "stack_focus": "Python/FastAPI 기반 서버 구조",
            "role_summary": "백엔드 서비스에서 API, 데이터 흐름, 운영 구조를 구현한 역할",
        }

    if "react" in stack_set or "typescript" in stack_set or "frontend" in readme_lower:
        return {
            "kind": "frontend",
            "headline_focus": "사용자 화면과 인터랙션",
            "implementation_focus": "사용자 화면과 인터랙션",
            "stack_focus": "프론트엔드 구성과 화면 구조",
            "role_summary": "프론트엔드에서 화면 구조와 사용자 상호작용을 구현한 역할",
        }

    return {
        "kind": "general",
        "headline_focus": "핵심 기능",
        "implementation_focus": "핵심 기능",
        "stack_focus": "핵심 기술 스택",
        "role_summary": "저장소 전반의 기능 구현과 협업 흔적을 연결해 설명할 수 있는 역할",
    }


def build_project_summary(
    repository_name: str,
    repository_meta: dict,
    readme_text: str,
    project_profile: dict[str, str],
) -> str:
    description = repository_meta.get("description")
    readme_summary = extract_readme_summary(readme_text)
    if isinstance(description, str) and description.strip():
        return f"{repository_name}는 {description.strip()} 프로젝트입니다."
    if readme_summary:
        return f"{repository_name}는 {readme_summary}"
    return f"{repository_name}는 {project_profile['implementation_focus']} 중심으로 발전한 저장소입니다."


def build_role_summary(project_profile: dict[str, str], counts: Counter[str], tech_stack: list[str]) -> str:
    stack_summary = ", ".join(tech_stack[:4]) if tech_stack else "주요 기술 스택"
    collaboration_parts: list[str] = []
    if counts.get("pull_request"):
        collaboration_parts.append(f"pull request {counts['pull_request']}건")
    if counts.get("review"):
        collaboration_parts.append(f"review {counts['review']}건")
    if counts.get("issue"):
        collaboration_parts.append(f"issue {counts['issue']}건")

    collaboration_summary = ", ".join(collaboration_parts) if collaboration_parts else "구현 근거"
    return (
        f"{project_profile['role_summary']}입니다. "
        f"{stack_summary}를 바탕으로 구현 범위를 설명하고, {collaboration_summary}을 통해 협업 맥락까지 함께 전달할 수 있습니다."
    )


def build_evidence_summary(
    counts: Counter[str],
    repository_meta: dict,
    readme_text: str,
    tech_stack: list[str],
) -> str:
    parts = [f"{source_type} {count}개" for source_type, count in sorted(counts.items())]
    count_summary = ", ".join(parts) if parts else "저장된 evidence가 없습니다"
    readme_features = extract_feature_candidates(readme_text)
    description = repository_meta.get("description")
    stack_summary = ", ".join(tech_stack[:4]) if tech_stack else "기본 기술"

    detail_parts = [count_summary]
    if isinstance(description, str) and description.strip():
        detail_parts.append(f"저장소 설명: {description.strip()}")
    if readme_features:
        detail_parts.append(f"README 기준 주요 기능: {', '.join(readme_features[:3])}")
    detail_parts.append(f"추정 기술 스택: {stack_summary}")
    return " / ".join(detail_parts)


def build_interview_questions(project_profile: dict[str, str], tech_stack: list[str]) -> list[str]:
    if project_profile["kind"] == "flutter":
        questions = [
            "Flutter 앱에서 가장 중요한 사용자 흐름을 어떤 화면 구조와 상태 관리 방식으로 풀어냈나요?",
            "모바일 앱에서 사용한 네트워크/의존성 선택이 사용자 경험에 어떤 영향을 줬나요?",
        ]
    elif project_profile["kind"] == "backend":
        questions = [
            "이 프로젝트에서 가장 중요한 API 또는 데이터 모델 설계 결정은 무엇이었나요?",
            "서버 구조를 바꿀 때 성능, 운영, 협업 중 무엇을 우선순위로 두었나요?",
        ]
    elif project_profile["kind"] == "frontend":
        questions = [
            "사용자 화면과 상태 흐름을 설계할 때 가장 중요하게 본 상호작용은 무엇이었나요?",
            "프론트엔드 구조를 나눌 때 유지보수성과 구현 속도 사이의 균형을 어떻게 잡았나요?",
        ]
    else:
        questions = [
            "이 프로젝트에서 가장 중요한 기술적 의사결정은 무엇이었나요?",
            "핵심 기능을 구현할 때 요구사항을 코드 구조로 바꾸는 과정에서 어떤 기준을 사용했나요?",
        ]

    questions.append("수집된 GitHub evidence 중 본인의 기여를 가장 잘 보여주는 근거는 무엇인가요?")
    questions.append(f"비슷한 기능을 다시 만든다면 {', '.join(tech_stack[:2]) if tech_stack else '현재 구조'} 관점에서 무엇을 개선하겠나요?")
    return questions[:5]


def extract_readme_summary(readme_text: str) -> str:
    if not readme_text:
        return ""

    paragraphs = re.split(r"\n\s*\n", readme_text)
    for paragraph in paragraphs:
        cleaned_lines = []
        for raw_line in paragraph.splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("![" ) or stripped.startswith("[!"):
                continue
            cleaned = clean_markdown_text(stripped)
            if cleaned:
                cleaned_lines.append(cleaned)
        if cleaned_lines:
            summary = " ".join(cleaned_lines)
            return summary[:280]
    return ""


def extract_feature_candidates(readme_text: str) -> list[str]:
    if not readme_text:
        return []

    features: list[str] = []
    in_feature_section = False
    for raw_line in readme_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        normalized = line.lower().lstrip("#").strip()
        if line.startswith("#"):
            in_feature_section = any(
                keyword in normalized
                for keyword in ("feature", "features", "기능", "주요 기능", "핵심 기능")
            )
            continue

        if in_feature_section and is_markdown_list_item(line):
            cleaned = clean_markdown_text(remove_list_marker(line))
            if is_meaningful_feature_text(cleaned):
                features.append(cleaned)
            continue

        if is_markdown_list_item(line):
            cleaned = clean_markdown_text(remove_list_marker(line))
            if is_meaningful_feature_text(cleaned):
                features.append(cleaned)

    return dedupe_preserve_order(features)[:5]


def is_markdown_list_item(line: str) -> bool:
    return bool(re.match(r"^([-*+]|\d+\.)\s+", line))


def remove_list_marker(line: str) -> str:
    return re.sub(r"^([-*+]|\d+\.)\s+", "", line).strip()


def is_meaningful_feature_text(value: str) -> bool:
    if len(value) < 6 or len(value) > 120:
        return False
    lower = value.lower()
    ignored = ("installation", "license", "contributing", "todo", "usage", "screenshot")
    return not any(token in lower for token in ignored)


def clean_markdown_text(value: str) -> str:
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" -:\t")


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result

def build_evidence_label(evidence: AnalysisEvidence) -> str:
    payload = evidence.payload_json
    title = payload.get("title") or payload.get("message") or payload.get("filename") or evidence.source_id
    return f"{evidence.source_type}: {title}"
