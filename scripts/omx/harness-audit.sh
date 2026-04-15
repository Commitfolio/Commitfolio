#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

pass() { printf '[PASS] %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; }

section() {
  printf '\n== %s ==\n' "$1"
}

require_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    pass "$path"
  else
    fail "$path missing"
  fi
}

section "Core OMX files"
require_file "AGENTS.md"
require_file ".codex/config.toml"
require_file ".omx/setup-scope.json"
require_file ".omx/tmux-hook.json"

section "Planning artifact presence"
for path in docs/prd docs/tasks .omx/plans; do
  if [[ -d "$path" ]]; then
    pass "$path"
  else
    fail "$path missing"
  fi
done

section "Doctor"
if omx doctor; then
  pass "omx doctor"
else
  fail "omx doctor"
fi

section "tmux runtime prerequisites"
if command -v tmux >/dev/null 2>&1; then
  pass "tmux installed: $(command -v tmux)"
else
  warn "tmux not installed; team/ralph tmux injection cannot run locally yet"
fi

python3 <<'PY'
import json
from pathlib import Path

path = Path(".omx/tmux-hook.json")
raw = json.loads(path.read_text())
target = raw.get("target") or {}
value = (target.get("value") or "").strip()
enabled = raw.get("enabled") is True
placeholder = value.lower() in {"replace-with-tmux-pane-id", "replace-with-tmux-session-name", "unset", ""}

print("\n== tmux-hook config ==")
print(f"enabled={enabled}")
print(f"target_type={target.get('type', '')}")
print(f"target_value={value or '<empty>'}")
print(f"placeholder_target={placeholder}")

if enabled and placeholder:
    print("[WARN] tmux-hook is enabled with a placeholder target")
elif not enabled and placeholder:
    print("[PASS] tmux-hook is safely disabled until a real tmux target is configured")
elif enabled and not placeholder:
    print("[PASS] tmux-hook has an active concrete target")
else:
    print("[WARN] tmux-hook is disabled even though a concrete target exists")
PY

section "tmux-hook CLI status"
if omx tmux-hook status; then
  :
else
  warn "omx tmux-hook status returned non-zero"
fi

section "tmux-hook validation"
if omx tmux-hook validate; then
  pass "omx tmux-hook validate"
else
  warn "omx tmux-hook validate failed (expected outside tmux or when tmux is missing)"
fi
