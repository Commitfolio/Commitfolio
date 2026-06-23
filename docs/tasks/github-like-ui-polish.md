# Task: GitHub Primer 톤 메인 UI 리디자인

## Summary
- Title: GitHub Primer 톤 메인 UI 리디자인
- Status: Done
- Owner: Codex
- Issue: https://github.com/Commitfolio/Commitfolio/issues/24
- PRD: `docs/prd/github-like-ui-polish.md`
- Branch: `기능/이슈-24-github-primer-ui-리디자인`
- PR:

## Objective
현재 AI 랜딩페이지처럼 보이는 메인 화면을 GitHub repository/dashboard 느낌의 정보 중심 UI로 바꾼다.

## Preconditions
- [x] PRD is approved
- [x] Scope is CSS/App shell 중심으로 좁혀짐
- [x] Verification approach is known

## Implementation Checklist
- [x] Confirm touched files/modules
- [x] App shell/header 구조 정리
- [x] CSS token/color/button/panel 재정의
- [x] repository/analysis/result panel spacing 조정
- [x] App tests 유지 또는 보강
- [x] Docs completion notes 업데이트

## Verification Checklist
- [x] `npm --prefix apps/frontend run lint`
- [x] `npm --prefix apps/frontend run typecheck`
- [x] `npm --prefix apps/frontend run test -- --run`
- [x] `npm --prefix apps/frontend run build`
- [x] `git diff --check`

## Completion Notes
- What changed: 큰 hero/그라데이션 중심 화면을 GitHub Primer 느낌의 header, workflow strip, bordered panels, neutral buttons, repository-like list로 재정리했다.
- Evidence: frontend lint/typecheck/test/build와 git diff --check 통과.
- Remaining risks: 실제 브라우저 시각 QA는 사용자 피드백이 필요하다. Primer dependency를 도입하지 않고 CSS로 톤만 맞췄다.
