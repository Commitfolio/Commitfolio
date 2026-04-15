#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

TITLE=""
SLUG=""
BODY_FILE=""
ISSUE_NUMBER=""
LABEL="feature"
BASE_BRANCH="develop"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/github/start-feature.sh --title "<title>" [options]

Options:
  --title "<title>"         Feature issue title (required unless --issue-number is provided)
  --slug "<slug>"           Branch/doc slug override
  --body-file <path>        Use an existing issue body file
  --issue-number <number>   Reuse an existing issue instead of creating one
  --label <label>           GitHub label to apply when creating an issue (default: feature)
  --base <branch>           Base branch to branch from (default: develop)
  --dry-run                 Print actions without mutating Git or GitHub
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE="${2:-}"; shift 2 ;;
    --slug) SLUG="${2:-}"; shift 2 ;;
    --body-file) BODY_FILE="${2:-}"; shift 2 ;;
    --issue-number) ISSUE_NUMBER="${2:-}"; shift 2 ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    --base) BASE_BRANCH="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$ISSUE_NUMBER" && -z "$TITLE" ]]; then
  echo "--title is required when --issue-number is not provided." >&2
  exit 1
fi

if [[ -z "$SLUG" ]]; then
  SLUG="$(python3 - "$TITLE" <<'PY'
import re
import sys
import unicodedata

title = sys.argv[1] if len(sys.argv) > 1 else ""
ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
print(slug)
PY
)"
fi

if [[ -z "$SLUG" ]]; then
  echo "Could not derive an ASCII slug from the title. Pass --slug explicitly." >&2
  exit 1
fi

if [[ -n "$(git status --short)" && "$DRY_RUN" -eq 0 ]]; then
  echo "Working tree must be clean before starting a feature branch." >&2
  exit 1
fi

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$BASE_BRANCH" && "$DRY_RUN" -eq 0 ]]; then
  echo "Current branch is '$current_branch'. Switch to '$BASE_BRANCH' before starting a feature branch." >&2
  exit 1
fi

if [[ -z "$ISSUE_NUMBER" ]]; then
  issue_cmd=(gh issue create --title "$TITLE" --label "$LABEL")
  if [[ -n "$BODY_FILE" ]]; then
    issue_cmd+=(--body-file "$BODY_FILE")
  else
    issue_cmd+=(--body "Feature requested via Commitfolio issue-first flow.")
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[DRY-RUN] '
    printf '%q ' "${issue_cmd[@]}"
    printf '\n'
    ISSUE_NUMBER="0000"
  else
    issue_url="$("${issue_cmd[@]}")"
    ISSUE_NUMBER="${issue_url##*/}"
  fi
fi

branch_name="feat/${ISSUE_NUMBER}-${SLUG}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[DRY-RUN] git switch -c ${branch_name}"
else
  git switch -c "$branch_name"
fi

cat <<EOF
Issue: #${ISSUE_NUMBER}
Branch: ${branch_name}
Suggested docs:
- docs/prd/${SLUG}.md
- docs/tasks/${SLUG}.md
- .omx/plans/prd-${SLUG}.md
- .omx/plans/test-spec-${SLUG}.md
EOF
