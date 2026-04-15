#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

TARGET_PANE="${1:-${TMUX_PANE:-}}"

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is not installed. Install tmux first, then rerun this script." >&2
  exit 1
fi

if [[ -z "$TARGET_PANE" ]]; then
  echo "No tmux pane target detected. Run this inside tmux or pass a pane id like %12." >&2
  exit 1
fi

python3 <<'PY' "$TARGET_PANE"
import json
import sys
from pathlib import Path

target_pane = sys.argv[1]
path = Path(".omx/tmux-hook.json")

if path.exists():
    data = json.loads(path.read_text())
else:
    data = {}

data.setdefault("allowed_modes", ["ralph", "ultrawork", "team"])
data.setdefault("cooldown_ms", 15000)
data.setdefault("max_injections_per_session", 200)
data.setdefault("prompt_template", "Continue from current mode state. [OMX_TMUX_INJECT]")
data.setdefault("marker", "[OMX_TMUX_INJECT]")
data.setdefault("dry_run", False)
data.setdefault("log_level", "info")
data.setdefault("skip_if_scrolling", True)
data["enabled"] = True
data["target"] = {"type": "pane", "value": target_pane}

path.write_text(json.dumps(data, indent=2) + "\n")
PY

echo "Updated .omx/tmux-hook.json with pane target: $TARGET_PANE"
omx tmux-hook status
omx tmux-hook validate
