# PRD: 포트폴리오 결과 편집과 재생성

## Summary
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/16
- Branch: `기능/이슈-16-결과-편집-재생성`
- Roadmap stage: Stage 6 — Result editing + save/regenerate

## Problem
Stage 5에서 포트폴리오 결과 초안 생성과 조회가 가능해졌지만, 사용자가 문장을 수정하거나 같은 evidence로 새 버전을 재생성할 수 없다. 결과물이 실제 포트폴리오로 쓰이려면 사용자가 편집하고 저장할 수 있어야 한다.

## Goal
저장된 포트폴리오 결과를 편집/저장하고, 기존 evidence를 기반으로 새 버전의 결과를 재생성할 수 있게 한다.

## Non-goals
- PDF 다운로드
- OpenAI 기반 문장 개선
- 결과 버전 diff UI
- React Router 도입

## Requirements

### Backend
- `PATCH /api/v1/results/{result_id}`로 결과 섹션을 부분 수정한다.
- `POST /api/v1/results/{result_id}/regenerate`로 같은 analysis job/evidence 기반 새 result version을 만든다.
- regenerate 후 `analysis_jobs.result_id`는 새 result를 가리킨다.
- 본인 소유 result만 수정/재생성할 수 있다.

### Frontend
- result editor UI를 제공한다.
- headline, overview, role, contribution list, tech stack, evidence summary, interview questions를 수정할 수 있다.
- 저장 후 viewer에 수정 내용이 반영된다.
- regenerate 후 새 version result가 표시된다.

## Acceptance Criteria
- [x] result를 수정 저장할 수 있다.
- [x] 저장 후 다시 상세 조회해도 수정 내용이 유지된다.
- [x] regenerate가 새 result id와 증가된 version을 반환한다.
- [x] regenerate 후 최근 결과 목록에서 새 result를 확인할 수 있다.
- [x] 기존 Stage 5 result viewer가 유지된다.

## Verification
- Backend pytest
- Frontend lint/typecheck/test/build
- Alembic SQLite smoke
