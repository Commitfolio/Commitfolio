# PRD: GitHub Primer 톤 메인 UI 리디자인

## Metadata
- Title: GitHub Primer 톤 메인 UI 리디자인
- Owner: Codex
- Status: Done
- Target milestone: Public MVP UI polish
- Related issue: https://github.com/Commitfolio/Commitfolio/issues/24
- Related task doc: `docs/tasks/github-like-ui-polish.md`

## Problem
현재 Commitfolio 메인 화면은 큰 hero, 둥근 카드, 그라데이션 배경 중심이라 AI가 생성한 랜딩페이지처럼 보이고, 실제 작업 흐름이 한눈에 들어오지 않는다. MVP는 GitHub 활동 데이터를 다루는 도구이므로 GitHub repository/dashboard에 가까운 실용적인 정보 구조와 차분한 시각 톤이 더 적합하다.

## Goal
- GitHub Primer 느낌의 색상, border, panel, button 밀도를 적용한다.
- 큰 마케팅 hero를 줄이고 앱형 header + workflow panels 구조로 바꾼다.
- 저장소 선택 → 분석 → 결과 문서 흐름이 한눈에 보이게 한다.
- 한국어 UI와 접근성 label은 유지한다.

## Non-goals
- Primer CSS dependency 추가
- GitHub UI 완전 복제
- dark mode
- 복잡한 navigation/routing 추가
- Figma 시안 제작

## Design Direction
- Reference: GitHub Primer design system의 보수적 색상/타이포/간격/버튼 관성
- Page chrome: 흰 배경, 얇은 border, 은은한 gray canvas, repo header 느낌
- Components: panels는 GitHub `Box` 느낌의 1px border + 작은 radius + 명확한 heading
- Buttons: primary는 GitHub green, secondary는 gray bordered button
- Typography: 큰 hero 대신 작고 선명한 heading과 설명
- Layout: top app header, compact intro, task panels

## Scope
### In scope
- App shell/header 구조 변경
- CSS token 전면 정리
- panel/button/badge/list/input 스타일 GitHub-like로 변경
- result/repository/analysis layout 가독성 개선
- frontend tests label 유지/보강

### Out of scope
- backend changes
- new dependencies
- full component system extraction
- visual snapshot tooling

## Acceptance Criteria
- [ ] 화면 첫 인상이 AI 랜딩페이지보다 GitHub app/dashboard에 가깝다.
- [ ] 큰 hero/그라데이션 느낌이 줄고 정보 구조가 선명하다.
- [ ] 주요 버튼/패널/배지가 GitHub-like neutral styling이다.
- [ ] 한국어 문구와 기존 기능 흐름이 유지된다.
- [ ] frontend lint/typecheck/test/build가 통과한다.

## Verification Plan
- Unit: 기존 App tests 유지
- Integration: result/repository/analysis UI flow test 유지
- Manual: 로컬 화면에서 header/panel/button/readability 확인

## Risks
- GitHub 느낌을 과하게 복제하면 제품 고유성이 약해질 수 있다.
- 단일 CSS 파일에서 변경 폭이 커질 수 있으므로 새 dependency 없이 스타일만 조정한다.

## References
- Primer design system: https://primer.github.io/design/
- Primer primitives: https://github.com/primer/primitives
- Primer button guidance: https://primer.github.io/design/components/button/
