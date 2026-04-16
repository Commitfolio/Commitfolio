# Task: PDF 내보내기

## Summary
- Title: PDF 내보내기
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/20
- PRD: `docs/prd/pdf-export.md`
- Branch: `기능/이슈-20-pdf-내보내기`
- PR:

## Objective
편집된 포트폴리오 결과를 브라우저 print/save-as-PDF 방식으로 저장할 수 있는 MVP export 흐름을 제공한다.

## Preconditions
- [x] PRD is approved
- [x] Scope is narrow enough for one branch / PR
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] Add frontend print action test
- [x] Implement result export button and print handler
- [x] Add print media CSS for result document
- [x] Update roadmap and completion notes

## Verification Checklist
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `git diff --check`

## Deliverables
- Code: result panel print action, print CSS, frontend test
- Docs: PRD/task/roadmap updates
- Follow-up: server-side PDF binary endpoint는 필요성이 확인되면 별도 stage로 분리

## Notes for Codex / OMX
- 새 dependency 없이 browser print fallback을 우선한다.
- `GET /download.pdf` endpoint는 이번 MVP slice에서 구현하지 않는다.
- 사용자가 결과를 저장한 뒤 print dialog에서 Save as PDF를 선택하도록 안내한다.

## Execution Log
- 2026-04-16: Stage 8를 issue-first/document-first로 시작했다.
- 2026-04-16: 브라우저 print/save-as-PDF 기반 export 버튼, 출력용 CSS, frontend test를 완료했다.

## Completion Notes
- What changed: 결과 화면에 `PDF로 저장/출력` 버튼과 Save as PDF 안내를 추가하고, print media에서 결과 문서만 출력되도록 정리했다.
- Evidence: frontend lint/typecheck/test/build, backend pytest, git diff --check 통과.
- Remaining risks: 실제 브라우저 print preview는 자동화 테스트가 아니라 수동 확인이 필요하다. 서버-side PDF binary endpoint는 후속 필요성이 확인되면 별도 작업으로 분리한다.
