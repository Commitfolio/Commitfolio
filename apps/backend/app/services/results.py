from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import PurePosixPath
import re
from typing import Iterable, Optional

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


AREA_LABELS = {
    "auth": "인증",
    "blog": "블로그",
    "calendar": "캘린더",
    "chat": "채팅",
    "comment": "댓글",
    "course": "코스",
    "detail": "상세 화면",
    "home": "홈",
    "login": "로그인",
    "main": "메인 화면",
    "mypage": "마이페이지",
    "notification": "알림",
    "onboarding": "온보딩",
    "payment": "결제",
    "profile": "프로필",
    "review": "리뷰",
    "roadmap": "로드맵",
    "schedule": "일정",
    "search": "검색",
    "settings": "설정",
    "share": "공유",
    "survey": "설문",
    "ui": "UI",
}

GENERIC_PATH_SEGMENTS = {
    "android",
    "app",
    "apps",
    "assets",
    "core",
    "data",
    "domain",
    "feature",
    "features",
    "frontend",
    "backend",
    "common",
    "components",
    "config",
    "constants",
    "ios",
    "lib",
    "main",
    "presentation",
    "res",
    "resources",
    "screen",
    "screens",
    "service",
    "services",
    "shared",
    "src",
    "state",
    "styles",
    "test",
    "tests",
    "ui",
    "utils",
    "value",
    "values",
    "view",
    "views",
    "widget",
    "widgets",
}

SOURCE_WEIGHTS = {
    "pull_request": 4,
    "commit": 3,
    "issue": 2,
    "review": 1,
    "changed_file": 1,
}

TITLE_PREFIX_PATTERN = re.compile(
    r"^(feat|fix|chore|docs|refactor|style|test|build|ci|perf)(\([^)]+\))?:\s*",
    re.IGNORECASE,
)
BRANCH_PREFIX_PATTERN = re.compile(r"^(feat|fix|chore|docs|refactor|style|test|build|ci|perf)[/\-]", re.IGNORECASE)
SEPARATOR_PATTERN = re.compile(r"[_:/\-]+")

TECH_PATTERNS = [
    ("Flutter", ("pubspec.yaml", "lib/", "flutter", ".dart")),
    ("Dart", (".dart",)),
    ("Android", ("android/", "androidmanifest.xml", "build.gradle", ".kt")),
    ("iOS", ("ios/", ".swift", "info.plist")),
    ("Firebase", ("firebase", "firestore", "google-services", "messaging")),
    ("Riverpod", ("riverpod",)),
    ("Provider", ("provider",)),
    ("BLoC", ("bloc",)),
    ("GoRouter", ("go_router",)),
    ("AutoRoute", ("auto_route",)),
    ("React", (".tsx", ".jsx", "react")),
    ("TypeScript", (".ts", ".tsx")),
    ("JavaScript", (".js", ".jsx")),
    ("FastAPI", ("fastapi", "uvicorn", "alembic")),
    ("Python", (".py",)),
    ("SQLAlchemy", ("sqlalchemy",)),
    ("PostgreSQL", ("postgres", "sql")),
]


@dataclass
class ContributionCluster:
    key: str
    label: str
    score: int = 0
    titles: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    evidence_items: list[AnalysisEvidence] = field(default_factory=list)


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
    clusters = build_contribution_clusters(evidence)
    top_clusters = [cluster for cluster in clusters if cluster.titles][:4] or clusters[:4]
    top_labels = [cluster.label for cluster in top_clusters[:3]]
    repo_kind = infer_repository_kind(evidence)
    tech_stack = infer_tech_stack(evidence, repo_kind=repo_kind)
    total_count = sum(counts.values())

    headline = build_headline(job.repository_full_name, repo_kind, top_labels)
    project_overview = build_project_overview(job.repository_full_name, repo_kind, total_count, top_labels)
    role_summary = build_role_summary(repo_kind, top_labels, tech_stack, evidence)
    key_contributions = build_key_contributions(top_clusters)
    evidence_summary = build_evidence_summary_text(counts, top_labels)
    interview_questions = build_interview_questions(top_labels, tech_stack)

    return ResultDraft(
        headline=headline,
        project_overview=project_overview,
        role_summary=role_summary,
        key_contributions=key_contributions,
        tech_stack=tech_stack,
        evidence_summary=evidence_summary,
        interview_questions=interview_questions,
    )


def build_headline(repository_name: str, repo_kind: str, top_labels: list[str]) -> str:
    focus = " · ".join(top_labels[:2]) if top_labels else "핵심 사용자 흐름"
    return f"{repository_name}에서 {focus} 기능을 고도화한 {repo_kind} 개발 경험"


def build_project_overview(
    repository_name: str,
    repo_kind: str,
    total_count: int,
    top_labels: list[str],
) -> str:
    focus = ", ".join(top_labels[:3]) if top_labels else "핵심 기능 흐름"
    return (
        f"{repository_name}는 {repo_kind} 저장소로, {focus} 영역을 중심으로 "
        f"commit · pull request · issue · review · changed file 근거 {total_count}개를 수집해 "
        "실제 구현 내역과 사용자 흐름을 포트폴리오 문서로 재구성했습니다."
    )


def build_role_summary(
    repo_kind: str,
    top_labels: list[str],
    tech_stack: list[str],
    evidence: list[AnalysisEvidence],
) -> str:
    focus = ", ".join(top_labels[:2]) if top_labels else "핵심 기능"
    detail_labels = infer_file_signal_labels(
        [str(item.payload_json.get("filename") or "") for item in evidence if item.source_type == "changed_file"]
    )
    detail_summary = ", ".join(detail_labels[:2]) if detail_labels else "화면과 구조 연결"
    tech_summary = " / ".join(tech_stack[:3]) if tech_stack else repo_kind
    return (
        f"{tech_summary} 기반의 {repo_kind}에서 {focus} 흐름을 직접 구현하고, "
        f"{detail_summary}까지 함께 다듬는 구현 중심 역할을 수행했습니다."
    )


def build_key_contributions(clusters: list[ContributionCluster]) -> list[str]:
    contributions: list[str] = []

    for cluster in clusters:
        if not cluster.titles and cluster.score <= SOURCE_WEIGHTS["changed_file"]:
            continue
        title_summary = summarize_cluster_titles(cluster.titles)
        file_detail = summarize_cluster_files(cluster.files)
        if file_detail:
            contributions.append(
                f"{cluster.label} 영역에서 {title_summary}를 중심으로 기능을 확장하고, {file_detail}까지 함께 정리해 사용자 흐름을 완성했습니다."
            )
        else:
            contributions.append(
                f"{cluster.label} 영역에서 {title_summary}를 구현해 실제 사용자 기능으로 연결했습니다."
            )

    if contributions:
        return contributions[:5]

    return [
        "GitHub 활동 근거를 구조화해 포트폴리오 결과로 재구성할 수 있는 분석 흐름을 만들었습니다.",
        "기능 단위 evidence를 묶어 사용자가 바로 활용할 수 있는 결과 초안을 생성했습니다.",
        "결과 문서와 근거 링크를 함께 제공해 검증 가능한 포트폴리오 형태로 정리했습니다.",
    ]


def build_evidence_summary_text(counts: Counter[str], top_labels: list[str]) -> str:
    focus = ", ".join(top_labels[:3]) if top_labels else "핵심 기능"
    parts = [f"{source_type} {count}개" for source_type, count in sorted(counts.items()) if count]
    return f"{focus} 관련 변경이 중심이었고, 총 근거는 {', '.join(parts)}로 구성되었습니다." if parts else "수집된 근거가 아직 없습니다."


def build_interview_questions(top_labels: list[str], tech_stack: list[str]) -> list[str]:
    primary_label = top_labels[0] if top_labels else "핵심 기능"
    primary_tech = tech_stack[0] if tech_stack else "주요 기술"
    secondary_tech = tech_stack[1] if len(tech_stack) > 1 else primary_tech
    return [
        f"{primary_label} 기능을 구현할 때 가장 중요한 기술적 의사결정은 무엇이었나요?",
        f"{primary_tech}와 {secondary_tech}를 실제 화면/구조에 녹여낼 때 어떤 제약을 해결했나요?",
        "가장 대표적인 근거 링크 하나를 골라 본인의 기여를 어떻게 설명할지 말해 주세요.",
    ]


def pick_section_evidence(evidence: list[AnalysisEvidence]) -> dict[str, list[AnalysisEvidence]]:
    by_type: dict[str, list[AnalysisEvidence]] = {}
    for item in evidence:
        by_type.setdefault(item.source_type, []).append(item)

    summary_evidence = (by_type.get("pull_request") or by_type.get("commit") or evidence)[:5]
    return {
        "key_contributions": summary_evidence[:3],
        "tech_stack": (by_type.get("changed_file") or evidence)[:4],
        "evidence_summary": summary_evidence[:5],
    }


def build_contribution_clusters(evidence: list[AnalysisEvidence]) -> list[ContributionCluster]:
    clusters: dict[str, ContributionCluster] = {}

    for item in evidence:
        cluster_key = infer_cluster_key(item)
        cluster = clusters.setdefault(
            cluster_key,
            ContributionCluster(
                key=cluster_key,
                label=display_cluster_label(cluster_key),
            ),
        )
        cluster.score += SOURCE_WEIGHTS.get(item.source_type, 1)
        cluster.evidence_items.append(item)

        title = extract_primary_title(item)
        if title and item.source_type != "changed_file":
            cluster.titles.append(title)

        filename = str(item.payload_json.get("filename") or "")
        if filename:
            cluster.files.append(filename)

    return sorted(
        clusters.values(),
        key=lambda cluster: (cluster.score, len(cluster.titles), len(cluster.files)),
        reverse=True,
    )


def infer_cluster_key(evidence: AnalysisEvidence) -> str:
    candidates = list(extract_area_candidates(extract_primary_title(evidence), str(evidence.payload_json.get("filename") or "")))
    if candidates:
        return candidates[0]

    filename = str(evidence.payload_json.get("filename") or "")
    return infer_path_area(filename) or evidence.source_type


def extract_primary_title(evidence: AnalysisEvidence) -> str:
    payload = evidence.payload_json
    raw = payload.get("title") or payload.get("message") or payload.get("filename") or evidence.source_id
    return normalize_title(str(raw))


def extract_area_candidates(title: str, filename: str) -> Iterable[str]:
    text = f"{title} {filename}".lower()
    seen: set[str] = set()
    for key in AREA_LABELS:
        if key in text and key not in seen:
            seen.add(key)
            yield key


def infer_path_area(filename: str) -> str | None:
    parts = [segment.lower() for segment in PurePosixPath(filename).parts if segment]
    for part in parts:
        if part in AREA_LABELS:
            return part
        if part not in GENERIC_PATH_SEGMENTS and len(part) > 2:
            return part
    return None


def display_cluster_label(cluster_key: str) -> str:
    return AREA_LABELS.get(cluster_key, humanize_text(cluster_key))


def summarize_cluster_titles(titles: list[str]) -> str:
    unique_titles = unique_preserving_order(clean_title_phrase(title) for title in titles if title)
    if not unique_titles:
        return "핵심 사용자 기능"
    if len(unique_titles) == 1:
        return unique_titles[0]
    if len(unique_titles) == 2:
        return f"{unique_titles[0]} 및 {unique_titles[1]}"
    return f"{unique_titles[0]}, {unique_titles[1]} 등"


def summarize_cluster_files(files: list[str]) -> str:
    labels = infer_file_signal_labels(files)
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return f"{labels[0]}와 {labels[1]}"


def infer_file_signal_labels(files: list[str]) -> list[str]:
    labels: list[str] = []
    joined = " ".join(file.lower() for file in files)
    if any(token in joined for token in ("route", "routes", "router", "navigation", "app_routes")):
        labels.append("라우팅과 화면 이동 구조")
    if any(token in joined for token in ("widget", "screen", "page", "view", "ui")):
        labels.append("UI 컴포넌트와 화면 구성")
    if any(token in joined for token in ("permission", "manifest", "strings.xml", "info.plist", "android/app/src/main/res")):
        labels.append("플랫폼 권한과 리소스 설정")
    if any(token in joined for token in ("repository", "service", "remote", "api", "network")):
        labels.append("데이터 연동 계층")
    if any(token in joined for token in ("model", "response", "entity", "state")):
        labels.append("응답 모델과 상태 구조")
    if any(token in joined for token in ("image", "picker", "photo", "upload")):
        labels.append("이미지 선택과 미디어 흐름")
    if any(token in joined for token in ("firebase", "firestore", "messaging")):
        labels.append("Firebase 연동")
    return unique_preserving_order(labels)[:3]


def infer_repository_kind(evidence: list[AnalysisEvidence]) -> str:
    filenames = " ".join(str(item.payload_json.get("filename") or "").lower() for item in evidence)
    if ".dart" in filenames or "pubspec.yaml" in filenames:
        return "Flutter 앱"
    if ".tsx" in filenames or ".jsx" in filenames:
        return "React 프런트엔드"
    if ".py" in filenames:
        return "Python 백엔드"
    if ".kt" in filenames or ".swift" in filenames:
        return "모바일 앱"
    return "프로덕트"


def infer_tech_stack(evidence: list[AnalysisEvidence], *, repo_kind: str) -> list[str]:
    normalized_signals = {
        str(item.payload_json.get("filename") or "").lower()
        for item in evidence
        if item.source_type == "changed_file"
    }
    normalized_signals.update(extract_primary_title(item).lower() for item in evidence)

    stack: list[str] = []
    if repo_kind == "Flutter 앱":
        stack.extend(["Flutter", "Dart"])

    flattened = " ".join(sorted(normalized_signals))
    for label, patterns in TECH_PATTERNS:
        if label in stack:
            continue
        if any(pattern in flattened for pattern in patterns):
            stack.append(label)

    if not stack:
        extension_map = {
            ".py": "Python",
            ".ts": "TypeScript",
            ".tsx": "React",
            ".js": "JavaScript",
            ".jsx": "React",
            ".css": "CSS",
            ".md": "Markdown",
            ".yaml": "YAML",
            ".yml": "YAML",
        }
        for item in evidence:
            filename = str(item.payload_json.get("filename") or "")
            value = extension_map.get(PurePosixPath(filename).suffix)
            if value and value not in stack:
                stack.append(value)

    return stack[:8] or ["GitHub", "FastAPI", "React"]


def build_evidence_label(evidence: AnalysisEvidence) -> str:
    payload = evidence.payload_json
    title = payload.get("title") or payload.get("message") or payload.get("filename") or evidence.source_id
    return f"{evidence.source_type}: {title}"


def normalize_title(raw: str) -> str:
    value = raw.strip()
    value = TITLE_PREFIX_PATTERN.sub("", value)
    value = BRANCH_PREFIX_PATTERN.sub("", value)
    value = SEPARATOR_PATTERN.sub(" ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_title_phrase(title: str) -> str:
    normalized = humanize_text(title.strip())
    patterns = [
        (r"^add (.+?) and fix (.+)$", r"\1 추가와 \2 개선"),
        (r"^add (.+?) and update (.+)$", r"\1 추가와 \2 개편"),
        (r"^add (.+)$", r"\1 추가"),
        (r"^fix (.+)$", r"\1 개선"),
        (r"^update (.+)$", r"\1 개편"),
        (r"^support (.+)$", r"\1 지원"),
        (r"^refactor (.+)$", r"\1 구조 정리"),
        (r"^cleanup (.+)$", r"\1 정리"),
        (r"^chore (.+)$", r"\1 정비"),
        (r"^implement (.+)$", r"\1 구현"),
        (r"^create (.+)$", r"\1 구현"),
    ]
    for pattern, replacement in patterns:
        candidate = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        if candidate != normalized:
            normalized = candidate
            break
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def humanize_text(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip()


def unique_preserving_order(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result
