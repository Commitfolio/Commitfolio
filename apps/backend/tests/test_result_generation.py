from __future__ import annotations

from app.models import AnalysisEvidence, AnalysisJob
from app.services.results import build_result_draft


def make_evidence(source_type: str, source_id: str, payload_json: dict) -> AnalysisEvidence:
    return AnalysisEvidence(
        id=f"ev_{source_id}",
        analysis_job_id="job_1",
        source_type=source_type,
        source_id=source_id,
        url=f"https://example.com/{source_type}/{source_id}",
        payload_json=payload_json,
    )


def test_build_result_draft_creates_feature_focused_flutter_narrative() -> None:
    job = AnalysisJob(
        id="job_1",
        user_id="user_1",
        repository_snapshot_id="repo_1",
        repository_full_name="SERVICE-MOHAENG/Mohaeng-Flutter",
        branch="main",
        status="completed",
    )
    evidence = [
        make_evidence(
            "commit",
            "c1",
            {"message": "feat: add blog detail flow and fix mypage schedule swipe"},
        ),
        make_evidence(
            "commit",
            "c2",
            {"message": "feat(blog): add course-based blog writing flow"},
        ),
        make_evidence(
            "pull_request",
            "25",
            {"title": "feat: roadmap ui publishing"},
        ),
        make_evidence(
            "changed_file",
            "f1",
            {"filename": "lib/core/constants/app_routes.dart"},
        ),
        make_evidence(
            "changed_file",
            "f2",
            {"filename": "lib/features/blog/presentation/blog_detail_page.dart"},
        ),
        make_evidence(
            "changed_file",
            "f3",
            {"filename": "android/app/src/main/res/values/strings.xml"},
        ),
        make_evidence(
            "changed_file",
            "f4",
            {"filename": "pubspec.yaml"},
        ),
    ]

    draft = build_result_draft(job, evidence)

    assert "Flutter 앱 개발 경험" in draft.headline
    assert "블로그" in draft.headline or "마이페이지" in draft.headline
    assert "Flutter" in draft.tech_stack
    assert "Dart" in draft.tech_stack
    assert "Android" in draft.tech_stack
    assert any("블로그 영역" in contribution or "마이페이지 영역" in contribution for contribution in draft.key_contributions)
    assert all("근거를 남겼습니다" not in contribution for contribution in draft.key_contributions)
    assert "라우팅과 화면 이동 구조" in draft.role_summary or "UI 컴포넌트와 화면 구성" in draft.role_summary
    assert "changed_file" in draft.evidence_summary
