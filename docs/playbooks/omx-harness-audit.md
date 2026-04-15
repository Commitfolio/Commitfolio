# OMX Harness Audit

이 문서는 Commitfolio 저장소에서 OMX 하네스를 점검하고, tmux 기반 런타임 기능을 안전하게 켜는 기준 문서다.

## Current repo stance

- `omx doctor` 통과가 코어 하네스 기준선이다.
- `.omx/tmux-hook.json` 은 **실제 tmux pane 타깃이 잡히기 전까지 비활성화** 상태를 유지한다.
- `team`, `ralph`, `ultrawork` 의 tmux 주입 기능은 **tmux 설치 + 유효한 pane id 설정**이 완료된 뒤에만 켠다.

## Quick audit

프로젝트 루트에서 실행:

```bash
scripts/omx/harness-audit.sh
```

이 스크립트는 다음을 확인한다.

1. 루트 `AGENTS.md`, `.codex/config.toml`, `.omx/*` 핵심 파일
2. `docs/prd`, `docs/tasks`, `.omx/plans` 계획 아티팩트 존재 여부
3. `omx doctor` 결과
4. tmux 설치 여부
5. `.omx/tmux-hook.json` 이 placeholder target 으로 잘못 활성화되어 있지 않은지
6. `omx tmux-hook status` / `validate` 결과

## Enable tmux injection safely

tmux 안에서 Codex/OMX 세션을 띄운 다음 실행:

```bash
scripts/omx/enable-tmux-hook.sh
```

특정 pane id 를 직접 넘기고 싶다면:

```bash
scripts/omx/enable-tmux-hook.sh %12
```

이 스크립트는 현재 pane id(또는 전달된 pane id)를 `.omx/tmux-hook.json` 에 기록하고, 즉시 `omx tmux-hook status` / `validate` 로 검증한다.

## Expected healthy states

### Core harness healthy

- `omx doctor` 성공
- `.codex/config.toml` 에 OMX MCP / settings 존재
- 루트 `AGENTS.md` 존재
- `.omx/state`, `.omx/plans` 존재

### tmux runtime healthy

- `tmux` 명령 사용 가능
- `omx tmux-hook status` 에서 실제 pane target 표시
- `omx tmux-hook validate` 성공
- `Last Reason` 이 `invalid_config` 가 아님

## Known caveat in sandboxed agent sessions

- 일부 sandbox 환경에서는 `omx explore` 가 `.codex/sessions` 권한 또는 세션 생성 제한 때문에 실패할 수 있다.
- 일부 sandbox 환경에서는 `tmux` 가 설치되어 있어도 tmux socket 접근 제한 때문에 `omx tmux-hook validate` 가 `Operation not permitted` 로 실패할 수 있다.
- 이 경우 repo 설정 불량으로 단정하지 말고, **로컬 터미널 세션에서 다시 검증**한다.
- `omx doctor` 가 통과하고 로컬 셸에서 `omx explore --prompt ...` 가 동작하면 repo 설정은 정상으로 본다.
- `omx tmux-hook validate` 가 로컬 tmux 세션에서 성공하면 tmux runtime wiring 도 정상으로 본다.
