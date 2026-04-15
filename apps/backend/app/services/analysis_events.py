from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Optional

from fastapi import Request

from app.api.schemas import AnalysisJobResponse
from app.models import AnalysisJobEvent
from app.repositories.analysis_jobs import AnalysisJobRepository


TERMINAL_JOB_EVENTS = {"job_completed", "job_failed"}
SSE_POLL_INTERVAL_SECONDS = 0.1
SSE_HEARTBEAT_INTERVAL_SECONDS = 1.0
SSE_MAX_STREAM_SECONDS = 30.0


class AnalysisEventService:
    """Business use cases for replaying analysis job events over SSE."""

    @staticmethod
    def resolve_event_cursor(after: Optional[int], last_event_id: Optional[str]) -> Optional[int]:
        if after is not None:
            return after

        if not last_event_id:
            return 0

        try:
            cursor = int(last_event_id)
        except ValueError:
            return None

        return cursor if cursor >= 0 else None

    async def stream_job_events(
        self,
        request: Request,
        session_factory,
        job_id: str,
        user_id: str,
        after_sequence: int,
        snapshot: AnalysisJobResponse,
    ) -> AsyncIterator[str]:
        yield self.format_sse(
            "snapshot",
            {
                "job": snapshot.model_dump(),
                "after": after_sequence,
            },
        )

        last_sequence = after_sequence
        heartbeat_elapsed = 0.0
        stream_elapsed = 0.0

        while not await request.is_disconnected():
            with session_factory() as stream_db:
                repository = AnalysisJobRepository(stream_db)
                job = repository.get_owned_job(user_id, job_id)
                events = repository.list_events_after(job_id=job_id, last_sequence=last_sequence)

            if events:
                heartbeat_elapsed = 0.0
                for event in events:
                    last_sequence = event.sequence
                    yield self.format_sse(event.event_type, self.build_event_payload(job_id, event), event.sequence)

                    if event.event_type in TERMINAL_JOB_EVENTS:
                        return
                continue

            if job and job.status in {"completed", "failed"}:
                return

            heartbeat_elapsed += SSE_POLL_INTERVAL_SECONDS
            stream_elapsed += SSE_POLL_INTERVAL_SECONDS
            if heartbeat_elapsed >= SSE_HEARTBEAT_INTERVAL_SECONDS:
                heartbeat_elapsed = 0.0
                yield self.format_sse(
                    "heartbeat",
                    {
                        "job_id": job_id,
                        "after": last_sequence,
                    },
                )

            if stream_elapsed >= SSE_MAX_STREAM_SECONDS:
                return

            await asyncio.sleep(SSE_POLL_INTERVAL_SECONDS)

    @staticmethod
    def format_sse(event_type: str, payload: dict, event_id: Optional[int] = None) -> str:
        lines = []
        if event_id is not None:
            lines.append(f"id: {event_id}")
        lines.append(f"event: {event_type}")
        lines.append(f"data: {json.dumps(payload, separators=(',', ':'))}")
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def build_event_payload(job_id: str, event: AnalysisJobEvent) -> dict:
        return {
            "job_id": job_id,
            "sequence": event.sequence,
            "event_type": event.event_type,
            "stage": event.stage,
            "percent": event.percent,
            "message": event.message,
            "payload_json": event.payload_json,
            "created_at": event.created_at.isoformat(),
        }
