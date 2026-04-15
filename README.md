# Commitfolio

## Hi there 👋

Commitfolio는 GitHub 활동을 근거 링크와 함께 포트폴리오 문서로 바꿔주는 서비스입니다.
사용자는 GitHub OAuth로 접근 가능한 public/private/org repository 중 하나를 선택하고, 해당 프로젝트의 `commit`, `PR`, `issue`, `review`, `changed files` 데이터를 바탕으로 포트폴리오 초안을 생성할 수 있습니다.

생성된 결과물은 단순 요약이 아니라 실제 제출 가능한 문서 형태를 목표로 합니다.
한 줄 소개, 프로젝트 개요, 담당 역할, 핵심 기여 내용, 기술 스택, 활동 근거 요약, 면접 예상 질문까지 한 번에 정리하고, 각 문장에는 가능한 한 PR/commit/issue 링크를 근거로 연결합니다.

### What we are building

- GitHub OAuth 기반 저장소 접근 및 단일 프로젝트 선택
- 활동 데이터 수집과 분석 파이프라인 구축
- SSE 기반 실시간 분석 진행 상태 표시
- 포트폴리오 결과 생성, 저장, 재분석
- 결과 텍스트 직접 수정 및 PDF 다운로드

### Why Commitfolio

Commitfolio는 "GitHub에서 실제로 한 일"을 "설득력 있는 포트폴리오 문장"으로 연결하는 데 집중합니다.
단순히 데이터를 나열하는 대신, 활동 근거와 결과 문장을 함께 제공해 포트폴리오의 신뢰도와 활용성을 높이는 것이 목표입니다.

이 프로젝트는 동시에 다음 역량을 보여주기 위해 설계되었습니다.

- GitHub 데이터 기반 제품 설계 능력
- 프론트엔드, 백엔드, 배포까지 끝까지 가져가는 end-to-end 구현 능력
- 문서, 자동화, 검증 흐름까지 포함한 하네스 엔지니어링 사고방식

### Tech stack

- Frontend: React + Vite + TypeScript
- UI: Tailwind CSS + shadcn/ui
- Backend: FastAPI
- Database: PostgreSQL
- Realtime: SSE
- Deployment: Vercel + Render + Neon

### Current MVP scope

Commitfolio의 첫 번째 목표는 공개 가능한 MVP를 빠르게 완성하는 것입니다.
초기 버전은 규칙 기반 분석으로 시작하고, 이후 OpenAI API를 연결해 결과 문장의 품질을 더 자연스럽게 다듬는 방향으로 확장합니다.
