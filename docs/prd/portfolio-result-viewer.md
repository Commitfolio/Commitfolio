# PRD: 포트폴리오 결과 생성 화면

## Summary
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/14
- Branch: `기능/이슈-14-포트폴리오-결과-화면`
- Roadmap stage: Stage 5 — Portfolio result generation + view

## Problem
Stage 4까지 repository 선택, analysis job 생성, GitHub evidence 수집, SSE 진행 상태 표시가 가능해졌다. 하지만 사용자가 최종적으로 확인할 포트폴리오 문서가 없어 Commitfolio의 핵심 가치가 아직 완성되지 않았다.

## Goal
수집된 `AnalysisEvidence`를 deterministic rule 기반으로 조합해 포트폴리오 결과 초안을 생성하고, 저장된 결과를 프론트엔드에서 읽기 쉬운 문서 형태로 볼 수 있게 한다.

## Non-goals
- OpenAI API 기반 문장 품질 개선
- 결과 편집 저장
- regenerate API
- PDF 다운로드
- 별도 결과 상세 라우팅 도입

## User Story
GitHub로 로그인한 사용자는 repository를 선택하고 analysis를 실행한 뒤, 수집된 evidence를 근거로 생성된 포트폴리오 초안을 즉시 확인할 수 있다.

## Requirements

### Backend
- `PortfolioResult` 저장 모델을 추가한다.
- 섹션별 evidence link 구조를 저장한다.
- completed analysis job에서 result를 생성하는 endpoint를 제공한다.
- 최근 result 목록과 result 상세 조회 endpoint를 제공한다.
- result 생성은 OpenAI 없이 deterministic rule로 동작한다.

### Frontend
- analysis 완료 후 result 생성을 요청할 수 있다.
- 생성된 result를 문서형 UI로 표시한다.
- 최근 result 목록의 최소 조회 경로를 제공한다.
- 각 섹션의 evidence link를 최소한 제목/URL 형태로 표시한다.

## Result Sections
- 한 줄 소개 (`headline`)
- 프로젝트 개요 (`project_overview`)
- 담당 역할 (`role_summary`)
- 핵심 기여 (`key_contributions`)
- 기술 스택 (`tech_stack`)
- 활동·근거 요약 (`evidence_summary`)
- 면접 예상 질문 (`interview_questions`)

## API Shape
- `POST /api/v1/analysis-jobs/{job_id}/result`
- `GET /api/v1/results`
- `GET /api/v1/results/{result_id}`

## Data Notes
- `analysis_jobs.result_id`는 최신 생성 결과를 가리킨다.
- Stage 6에서 편집/재생성을 추가할 수 있도록 result content와 evidence links를 분리한다.
- Stage 5에서는 result versioning을 최소화하고 최초 version `1`을 저장한다.

## Acceptance Criteria
- [x] completed job에서 result를 생성할 수 있다.
- [x] result 상세 API가 모든 섹션과 evidence links를 반환한다.
- [x] result 목록 API가 최근 결과를 반환한다.
- [x] 프론트엔드에서 result 문서와 evidence links를 볼 수 있다.
- [x] OpenAI key 없이 result 생성이 동작한다.

## Verification
- Backend pytest
- Alembic SQLite upgrade smoke
- Frontend lint/typecheck/test/build
- Manual: run analysis 이후 result 생성 버튼과 문서 표시 확인
