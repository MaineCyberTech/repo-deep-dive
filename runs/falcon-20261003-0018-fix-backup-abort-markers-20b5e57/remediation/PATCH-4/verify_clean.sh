#!/usr/bin/env bash
# PATCH-4 verification in a clean LF worktree (/root/falcon-p4).
# Writes raw output + exit codes to verify.log next to this script.
set -u
WT=/root/falcon-p4
LOG=/mnt/c/temp/proxmox-vm/audits/runs/falcon/20261003-0018-fix-backup-abort-markers-20b5e57/remediation/PATCH-4/verify.log
cd "$WT" || exit 1
{
echo "# PATCH-4 verification"
echo "date_utc=$(date -u +%FT%TZ)"
echo "worktree=$WT (clean git worktree, LF line endings)"
echo "commit=$(git rev-parse HEAD)"
echo
echo "## 1. bash -n on changed scripts"
for f in automation/validation/heartbeat.sh bootstrap/90-alerting.sh automation/validation/tests/heartbeat_independence_test.sh; do
  bash -n "$f"; echo "bash -n $f exit=$?"
done
echo
echo "## 2. heartbeat independence regression test"
bash automation/validation/tests/heartbeat_independence_test.sh; echo "heartbeat_independence_test exit=$?"
echo
echo "## 3. ci/validate.py (parsers, shell-syntax, shell-tests)"
FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only parsers,shell-syntax,shell-tests; echo "ci_validate_targeted exit=$?"
echo
echo "## 4. full ci/validate.py (evidence optional)"
FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py; echo "ci_validate_full exit=$?"
echo
echo "## 5. gitleaks"
GL="$(command -v gitleaks || true)"
[ -z "$GL" ] && [ -x /root/bin/gitleaks ] && GL=/root/bin/gitleaks
if [ -n "$GL" ]; then
  "$GL" detect --no-git --source . --redact --config .gitleaks.toml; echo "gitleaks exit=$?"
else
  echo "gitleaks NOT INSTALLED in this runner -> not run"
fi
} > "$LOG" 2>&1
tail -5 "$LOG"
