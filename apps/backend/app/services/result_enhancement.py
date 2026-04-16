from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Protocol

import httpx

from app.config import Settings
from app.models import AnalysisEvidence, AnalysisJob
from app.services.result_draft import ResultDraft


ENHANCEMENT_NOT_CONFIGURED = "not_configured"
ENHANCEMENT_ENHANCED = "enhanced"
ENHANCEMENT_FALLBACK = "fallback"


@dataclass(frozen=True)
class EnhancementResult:
    draft: ResultDraft
    status: str
    model: str | None
    message: str


class ResultEnhancer(Protocol):
    def enhance(
        self,
        *,
        job: AnalysisJob,
        evidence: list[AnalysisEvidence],
        draft: ResultDraft,
    ) -> EnhancementResult:
        ...


class NoOpResultEnhancer:
    def enhance(
        self,
        *,
        job: AnalysisJob,
        evidence: list[AnalysisEvidence],
        draft: ResultDraft,
    ) -> EnhancementResult:
        return EnhancementResult(
            draft=draft,
            status=ENHANCEMENT_NOT_CONFIGURED,
            model=None,
            message="기본 생성 사용",
        )


class OpenAIResultEnhancer:
    """Optional OpenAI post-processor with deterministic fallback."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.timeout_seconds = settings.openai_timeout_seconds

    def enhance(
        self,
        *,
        job: AnalysisJob,
        evidence: list[AnalysisEvidence],
        draft: ResultDraft,
    ) -> EnhancementResult:
        if not self.api_key:
            return EnhancementResult(
                draft=draft,
                status=ENHANCEMENT_NOT_CONFIGURED,
                model=None,
                message="기본 생성 사용",
            )

        try:
            payload = self._build_request_payload(job=job, evidence=evidence, draft=draft)
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()

            enhanced = parse_openai_result(response.json(), fallback=draft)
            return EnhancementResult(
                draft=enhanced,
                status=ENHANCEMENT_ENHANCED,
                model=self.model,
                message="OpenAI 후처리 적용",
            )
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return EnhancementResult(
                draft=draft,
                status=ENHANCEMENT_FALLBACK,
                model=self.model,
                message="OpenAI 후처리 실패, 기본 생성 사용",
            )

    def _build_request_payload(
        self,
        *,
        job: AnalysisJob,
        evidence: list[AnalysisEvidence],
        draft: ResultDraft,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "You improve a Korean developer portfolio draft. Preserve facts, evidence IDs, "
                        "repository names, and section shape. Return only valid JSON matching the schema."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "repository_full_name": job.repository_full_name,
                            "draft": result_draft_to_dict(draft),
                            "evidence_context": summarize_evidence(evidence),
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "portfolio_result_enhancement",
                    "strict": True,
                    "schema": result_draft_json_schema(),
                }
            },
            "max_output_tokens": 1600,
        }


def result_draft_to_dict(draft: ResultDraft) -> dict[str, Any]:
    return {
        "headline": draft.headline,
        "project_overview": draft.project_overview,
        "role_summary": draft.role_summary,
        "key_contributions": draft.key_contributions,
        "tech_stack": draft.tech_stack,
        "evidence_summary": draft.evidence_summary,
        "interview_questions": draft.interview_questions,
    }


def summarize_evidence(evidence: list[AnalysisEvidence]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    for item in evidence[:12]:
        payload = item.payload_json
        title = payload.get("title") or payload.get("message") or payload.get("filename") or item.source_id
        summary.append(
            {
                "id": item.id,
                "source_type": item.source_type,
                "source_id": item.source_id,
                "title": str(title),
                "url": item.url,
            }
        )
    return summary


def parse_openai_result(data: dict[str, Any], *, fallback: ResultDraft) -> ResultDraft:
    text = data.get("output_text")
    if not isinstance(text, str):
        text = extract_output_text(data)
    parsed = json.loads(text)
    return coerce_result_draft(parsed, fallback=fallback)


def extract_output_text(data: dict[str, Any]) -> str:
    output = data["output"]
    if not isinstance(output, list):
        raise TypeError("OpenAI response output must be a list")

    for item in output:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                return content["text"]
    raise KeyError("OpenAI response did not include output text")


def coerce_result_draft(value: dict[str, Any], *, fallback: ResultDraft) -> ResultDraft:
    if not isinstance(value, dict):
        raise TypeError("Enhanced result must be an object")

    return ResultDraft(
        headline=coerce_text(value.get("headline"), fallback.headline),
        project_overview=coerce_text(value.get("project_overview"), fallback.project_overview),
        role_summary=coerce_text(value.get("role_summary"), fallback.role_summary),
        key_contributions=coerce_text_list(value.get("key_contributions"), fallback.key_contributions, max_items=5),
        tech_stack=coerce_text_list(value.get("tech_stack"), fallback.tech_stack, max_items=8),
        evidence_summary=coerce_text(value.get("evidence_summary"), fallback.evidence_summary),
        interview_questions=coerce_text_list(value.get("interview_questions"), fallback.interview_questions, max_items=5),
    )


def coerce_text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def coerce_text_list(value: Any, fallback: list[str], *, max_items: int) -> list[str]:
    if not isinstance(value, list):
        return fallback

    items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return items[:max_items] or fallback


def result_draft_json_schema() -> dict[str, Any]:
    string_array = {"type": "array", "items": {"type": "string"}, "minItems": 1}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "headline",
            "project_overview",
            "role_summary",
            "key_contributions",
            "tech_stack",
            "evidence_summary",
            "interview_questions",
        ],
        "properties": {
            "headline": {"type": "string"},
            "project_overview": {"type": "string"},
            "role_summary": {"type": "string"},
            "key_contributions": string_array,
            "tech_stack": string_array,
            "evidence_summary": {"type": "string"},
            "interview_questions": string_array,
        },
    }
