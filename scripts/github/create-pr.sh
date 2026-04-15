#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

TITLE=""
BODY_FILE=""
BASE_BRANCH="develop"
ISSUE_NUMBER=""
SLUG=""
DRAFT=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/github/create-pr.sh [options]

Options:
  --title "<title>"         PR title override
  --body-file <path>        PR body file override
  --base <branch>           PR base branch (default: develop)
  --issue-number <number>   Related issue number override
  --slug <slug>             Doc slug override
  --draft                   Open as draft PR
  --dry-run                 Print actions without mutating GitHub
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE="${2:-}"; shift 2 ;;
    --body-file) BODY_FILE="${2:-}"; shift 2 ;;
    --base) BASE_BRANCH="${2:-}"; shift 2 ;;
    --issue-number) ISSUE_NUMBER="${2:-}"; shift 2 ;;
    --slug) SLUG="${2:-}"; shift 2 ;;
    --draft) DRAFT=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

branch_name="$(git branch --show-current)"
if [[ -z "$branch_name" || "$branch_name" == "develop" || "$branch_name" == "main" ]]; then
  echo "Run this from a feature branch, not ${branch_name:-<detached>}." >&2
  exit 1
fi

if [[ -z "$ISSUE_NUMBER" && "$branch_name" =~ ^[^/]+/([0-9]+)- ]]; then
  ISSUE_NUMBER="${BASH_REMATCH[1]}"
fi

if [[ -z "$SLUG" ]]; then
  SLUG="$(python3 - "$branch_name" <<'PY'
import re
import sys

branch = sys.argv[1]
match = re.match(r"^[^/]+/[0-9]+-(.+)$", branch)
print(match.group(1) if match else "")
PY
)"
fi

if [[ -z "$TITLE" ]]; then
  if [[ -n "$ISSUE_NUMBER" ]]; then
    TITLE="$(gh issue view "$ISSUE_NUMBER" --json title -q .title 2>/dev/null || true)"
  fi
  if [[ -z "$TITLE" ]]; then
    TITLE="$branch_name"
  fi
fi

temp_body=""
if [[ -z "$BODY_FILE" ]]; then
  temp_body="$(mktemp)"
  {
    echo "## Summary"
    echo "- What changed?"
    echo "- Why did this change happen?"
    echo
    echo "## Linked Docs"
    if [[ -n "$SLUG" ]]; then
      echo "- PRD: docs/prd/${SLUG}.md"
      echo "- Task: docs/tasks/${SLUG}.md"
    else
      echo "- PRD:"
      echo "- Task:"
    fi
    if [[ -n "$ISSUE_NUMBER" ]]; then
      echo "- Issue: #${ISSUE_NUMBER}"
      echo
      echo "Closes #${ISSUE_NUMBER}"
    else
      echo "- Issue:"
    fi
    echo
    echo "## Verification"
    echo "- [ ] Lint"
    echo "- [ ] Typecheck"
    echo "- [ ] Tests"
    echo "- [ ] Manual critical path check"
    echo
    echo "## Evidence"
    echo "- Commands run:"
    echo "- Screenshots or notes:"
    echo "- Remaining risks:"
    echo
    echo "## Docs Updated"
    echo "- [ ] Architecture docs"
    echo "- [ ] PRD / task docs"
    echo "- [ ] API contract"
    echo "- [ ] Domain model"
  } >"$temp_body"
  BODY_FILE="$temp_body"
fi

push_cmd=(git push -u origin HEAD)
pr_cmd=(gh pr create --base "$BASE_BRANCH" --title "$TITLE" --body-file "$BODY_FILE")
if [[ "$DRAFT" -eq 1 ]]; then
  pr_cmd+=(--draft)
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '[DRY-RUN] '
  printf '%q ' "${push_cmd[@]}"
  printf '\n'
  printf '[DRY-RUN] '
  printf '%q ' "${pr_cmd[@]}"
  printf '\n'
else
  "${push_cmd[@]}"
  "${pr_cmd[@]}"
fi

if [[ -n "$temp_body" ]]; then
  rm -f "$temp_body"
fi
