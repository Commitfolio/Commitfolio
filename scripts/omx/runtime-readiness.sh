#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

pass() { printf '[PASS] %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
section() { printf '\n== %s ==\n' "$1"; }

section "Local runtime readiness"

if command -v tmux >/dev/null 2>&1; then
  pass "tmux installed: $(command -v tmux)"
else
  warn "tmux is not installed"
fi

if [[ -n "${TMUX:-}" ]]; then
  pass "inside tmux session"
else
  warn "not currently inside tmux"
fi

if [[ -n "${TMUX_PANE:-}" ]]; then
  pass "TMUX_PANE=${TMUX_PANE}"
else
  warn "TMUX_PANE is empty"
fi

section "OMX status"
if omx doctor >/dev/null 2>&1; then
  pass "omx doctor"
else
  warn "omx doctor failed"
fi

omx tmux-hook status || true

section "Recommended next commands"
if ! command -v tmux >/dev/null 2>&1; then
  cat <<'EOF'
1. Install tmux
   - macOS (Homebrew): brew install tmux
2. Start tmux
   - tmux new -s omx
3. Open this repo and run Codex/OMX inside that pane
4. Enable the repo hook target
   - scripts/omx/enable-tmux-hook.sh
5. Re-run readiness checks
   - scripts/omx/runtime-readiness.sh
   - scripts/omx/harness-audit.sh
EOF
elif [[ -z "${TMUX_PANE:-}" ]]; then
  cat <<'EOF'
1. Start or attach tmux
   - tmux new -s omx
   - tmux attach -t omx
2. Run Codex/OMX from the target pane
3. Enable the repo hook target
   - scripts/omx/enable-tmux-hook.sh
4. Verify
   - omx tmux-hook validate
   - scripts/omx/harness-audit.sh
EOF
else
  cat <<'EOF'
1. Enable the repo hook target from this pane
   - scripts/omx/enable-tmux-hook.sh
2. Verify
   - omx tmux-hook validate
   - scripts/omx/harness-audit.sh
3. Smoke-test runtime workflows
   - ralph / team / ultrawork in the same tmux session
EOF
fi
