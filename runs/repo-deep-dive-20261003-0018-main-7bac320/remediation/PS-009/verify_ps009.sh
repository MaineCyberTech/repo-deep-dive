#!/usr/bin/env bash
# PS-009 verification runner (repo-deep-dive). Captures raw output + exit codes.
set -uo pipefail
REPO=/mnt/c/temp/repo-deep-dive-rem
cd "$REPO"

echo "# PS-009 verification log"
echo
echo "run:      20261003-0018-main-7bac320"
echo "patch set: PS-009"
echo "findings:  INV-P1-001, INV-P2-002, INV-P3-003"
echo "branch:   $(git rev-parse --abbrev-ref HEAD)"
echo "base:     origin/main @ $(git rev-parse --short origin/main)"
echo "date:     $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

run() {
  echo "===== COMMAND: $* ====="
  "$@" 2>&1
  local rc=$?
  echo "[exit=$rc]"
  echo
  return $rc
}

run bash tools/self_test.sh
run bash tools/lint_pack.sh
run bash tools/check_run.sh runs/repo-deep-dive-20261003-0018-main-7bac320

if command -v gitleaks >/dev/null 2>&1; then
  echo "===== COMMAND: gitleaks detect --no-git --redact --source . -v ====="
  gitleaks detect --no-git --redact --source . -v 2>&1
  echo "[exit=$?]"
else
  echo "===== gitleaks: NOT RUN (binary not installed on this host) ====="
fi
