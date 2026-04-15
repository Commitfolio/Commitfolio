#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

STRICT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict) STRICT=1 ;;
    -h|--help)
      cat <<'EOF'
Usage: scripts/github/check-flow.sh [--strict]

Checks:
- gh installation
- gh auth status
- repository visibility via gh repo view
- push readiness via git push --dry-run
- PR readiness via gh pr list
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
  shift
done

pass() { printf '[PASS] %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; }
section() { printf '\n== %s ==\n' "$1"; }

FAILURES=0

mark_failure() {
  FAILURES=$((FAILURES + 1))
}

repo_remote="$(git remote get-url origin)"
current_branch="$(git branch --show-current)"

section "Local git context"
pass "origin=$repo_remote"
pass "branch=${current_branch}"

section "gh CLI"
if command -v gh >/dev/null 2>&1; then
  pass "gh installed: $(command -v gh)"
else
  fail "gh is not installed"
  mark_failure
fi

section "Authentication"
if gh auth status >/tmp/commitfolio-gh-auth.out 2>/tmp/commitfolio-gh-auth.err; then
  pass "gh auth status"
else
  fail "gh auth is not ready"
  sed -n '1,40p' /tmp/commitfolio-gh-auth.err || true
  mark_failure
fi

section "Repository access"
if gh repo view --json nameWithOwner,defaultBranchRef,viewerPermission >/tmp/commitfolio-gh-repo.json 2>/tmp/commitfolio-gh-repo.err; then
  python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('/tmp/commitfolio-gh-repo.json').read_text())
name = payload.get('nameWithOwner')
default_branch = ((payload.get('defaultBranchRef') or {}).get('name')) or ''
permission = payload.get('viewerPermission') or ''
print(f"[PASS] repo={name} default_branch={default_branch} viewer_permission={permission}")
PY
else
  fail "gh repo view could not access the current repository"
  sed -n '1,40p' /tmp/commitfolio-gh-repo.err || true
  mark_failure
fi

section "Push readiness"
if git push --dry-run origin HEAD >/tmp/commitfolio-git-push.out 2>/tmp/commitfolio-git-push.err; then
  pass "git push --dry-run origin HEAD"
else
  fail "push dry-run failed"
  sed -n '1,40p' /tmp/commitfolio-git-push.err || true
  mark_failure
fi

section "PR readiness"
if gh pr list --limit 1 >/tmp/commitfolio-gh-pr.out 2>/tmp/commitfolio-gh-pr.err; then
  pass "gh pr list"
else
  fail "gh pr list failed"
  sed -n '1,40p' /tmp/commitfolio-gh-pr.err || true
  mark_failure
fi

section "Summary"
if [[ "$FAILURES" -eq 0 ]]; then
  pass "GitHub feature delivery flow is ready"
else
  warn "GitHub feature delivery flow has ${FAILURES} blocking check(s)"
fi

if [[ "$STRICT" -eq 1 && "$FAILURES" -gt 0 ]]; then
  exit 1
fi
