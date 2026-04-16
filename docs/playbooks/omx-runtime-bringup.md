# OMX Runtime Bring-up

이 문서는 Commitfolio 저장소에서 **tmux 기반 OMX 런타임**을 실제로 켜는 절차를 정리한다.

관련 문서:

- 기본 감사: `docs/playbooks/omx-harness-audit.md`
- 빠른 상태 점검: `scripts/omx/runtime-readiness.sh`
- 실제 target 설정: `scripts/omx/enable-tmux-hook.sh`

## 목표

다음 상태까지 가는 것이 목적이다.

- `omx doctor` 성공
- `tmux` 설치 완료
- tmux 안에서 Codex/OMX 세션 실행
- `.omx/tmux-hook.json` 에 실제 pane target 기록
- `omx tmux-hook validate` 성공

## 1. tmux 설치

### macOS (Homebrew)

```bash
brew install tmux
```

설치 확인:

```bash
tmux -V
```

## 2. tmux 세션 시작

```bash
tmux new -s omx
```

이미 세션이 있으면:

```bash
tmux attach -t omx
```

## 3. tmux 안에서 Codex/OMX 실행

tmux pane 안에서 이 repo로 이동해 Codex/OMX 작업을 시작한다.

핵심은 **실제로 작업을 계속할 pane 하나를 target pane으로 삼는 것**이다.

Commitfolio 작업 세션은 기본적으로 현재 OMX CLI의 실제 옵션인 `--madmax`로 실행한다. `omx --madmode`는 현재 버전에서 유효하지 않은 플래그이므로 사용하지 않는다.

```bash
omx --madmax
```

`--madmax`는 승인/샌드박스 우회 옵션이므로, 일반적인 비파괴 작업은 자동 진행하되 destructive/irreversible 작업은 명시적 요청이 있을 때만 수행한다.

현재 pane id 확인:

```bash
echo "$TMUX_PANE"
```

## 4. repo hook target 활성화

같은 pane에서 실행:

```bash
scripts/omx/enable-tmux-hook.sh
```

다른 pane id를 직접 지정하려면:

```bash
scripts/omx/enable-tmux-hook.sh %12
```

기대 결과:

- `.omx/tmux-hook.json` 의 `enabled` 가 `true`
- `target.value` 가 실제 `%숫자` 형태 pane id
- `omx tmux-hook validate` 성공

## 5. 검증

```bash
scripts/omx/runtime-readiness.sh
scripts/omx/harness-audit.sh
omx tmux-hook validate
```

정상 상태라면:

- `tmux installed`
- `inside tmux session`
- `TMUX_PANE=...`
- `tmux-hook has an active concrete target`
- `omx tmux-hook validate` 성공

## 6. 런타임 smoke test

같은 tmux 세션 안에서 다음 중 하나를 짧게 실행해 본다.

- `ralph`
- `team`
- `ultrawork`

검증 포인트:

- hook 상태가 `invalid_config` 로 떨어지지 않는지
- tmux target 이 실제 pane 을 가리키는지
- `.omx/logs/tmux-hook-YYYY-MM-DD.jsonl` 에 이벤트가 쌓이는지

## Troubleshooting

### `spawnSync tmux ENOENT`

원인: tmux 미설치  
조치: `brew install tmux`

### `No tmux pane target detected`

원인: tmux 밖에서 `scripts/omx/enable-tmux-hook.sh` 실행  
조치: tmux 안으로 들어가서 다시 실행하거나 pane id를 직접 전달

### `invalid_config`

원인: placeholder target 또는 빈 target  
조치: `scripts/omx/enable-tmux-hook.sh` 재실행

### `omx explore` 가 sandbox에서 실패

원인: sandbox 세션 권한/세션 파일 제약  
조치: 로컬 터미널 세션에서 다시 검증하고, repo 설정 불량과 분리해서 판단
