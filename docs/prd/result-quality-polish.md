# PRD: 결과 품질 개선과 선택형 OpenAI 후처리

## Summary
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/18
- Branch: `기능/이슈-18-결과-품질-개선-openai`
- Roadmap stage: Stage 7 — Result quality polish + optional OpenAI
- Related task: `docs/tasks/result-quality-polish.md`

## Problem
Stage 5/6에서 rule-based 포트폴리오 결과 생성, 조회, 편집, 재생성이 가능해졌다. 하지만 결과 문장과 면접 질문은 아직 deterministic 템플릿 중심이라 실제 제출용 문서로 쓰기에는 문장 자연스러움과 후보자 관점의 설득력이 부족할 수 있다.

동시에 MVP 핵심 경로는 OpenAI API 키나 외부 LLM 안정성에 의존하면 안 된다. 따라서 OpenAI는 결과 품질을 높이는 선택형 후처리 레이어여야 하며, 실패하거나 설정되지 않아도 기존 결과 생성 흐름은 그대로 성공해야 한다.

## Goal
- 기존 rule-based result generation을 기본 fallback으로 유지한다.
- OpenAI API key가 설정된 경우에만 optional quality enhancement를 실행한다.
- LLM 실패/미설정 시 기존 결과 생성 흐름을 실패시키지 않는다.
- evidence link 구조와 result section shape를 유지한다.
- 생성된 결과에 enhancement 적용 여부를 사용자가 이해할 수 있는 최소 상태를 제공한다.

## Non-goals
- OpenAI를 필수 생성 경로로 만들기
- streaming generation UI
- PDF 다운로드
- 복잡한 prompt 관리 시스템
- evidence link 재작성 또는 재매칭
- 다중 모델/벤더 추상화

## Requirements

### Backend
- OpenAI 설정은 환경 변수 기반으로 선택적으로 읽는다.
- API key가 없으면 기존 deterministic generator만 실행한다.
- OpenAI 호출 실패, timeout, invalid response는 fallback으로 처리한다.
- 후처리 입력에는 result section content와 근거 요약에 필요한 최소 evidence context만 포함한다.
- 후처리 출력은 기존 result section shape 안에서만 반영한다.
- evidence links는 기존 link id/source mapping을 유지한다.
- result 응답에는 enhancement 상태를 최소 필드로 포함한다.

### Frontend
- result detail 화면에서 enhancement 적용 여부를 이해할 수 있는 작은 상태 표시를 제공한다.
- OpenAI 미설정/fallback 상태는 오류처럼 보이지 않아야 한다.
- 기존 edit/save/regenerate UI는 유지한다.
- regenerate 후 enhancement 상태가 새 result에 맞게 표시된다.

### Configuration
- OpenAI key가 없는 로컬 개발 환경이 기본이다.
- `.env.example` 또는 backend setup docs에 선택형 설정을 문서화한다.
- 기본 model/timeout은 안전한 server-side default를 둔다.

## Acceptance Criteria
- [ ] OpenAI key 없이 backend result 생성/regenerate 테스트가 통과한다.
- [ ] OpenAI 성공 fake에서 section shape와 evidence links가 유지된다.
- [ ] OpenAI 실패 fake에서 fallback result가 저장되고 API는 성공한다.
- [ ] frontend detail 화면에서 enhancement 상태가 표시된다.
- [ ] 기존 Stage 5/6 result viewer/editor 흐름이 깨지지 않는다.
- [ ] 설정 문서가 OpenAI를 optional enhancement로 설명한다.

## Verification
- Backend pytest
- Frontend lint/typecheck/test/build
- Alembic SQLite smoke if schema changes are introduced
- `git diff --check`

## Risks
- LLM 응답이 schema를 벗어나면 result shape가 깨질 수 있다.
- OpenAI 호출 지연이 analysis job 완료 시간을 늘릴 수 있다.
- 너무 많은 evidence를 prompt에 넣으면 비용과 latency가 증가한다.
- frontend가 fallback을 실패처럼 표현하면 사용자가 불필요하게 불안해질 수 있다.

## Risk Responses
- schema validation에 실패하면 enhancement를 버리고 fallback을 저장한다.
- timeout을 짧게 두고 실패를 정상 fallback으로 기록한다.
- prompt 입력은 대표 section/evidence 요약으로 제한한다.
- UI 문구는 “기본 생성 사용”처럼 중립적으로 표시한다.
