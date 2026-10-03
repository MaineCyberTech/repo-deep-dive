#!/usr/bin/env bash
# PATCH-6 verification in a clean LF worktree (/root/falcon-p6).
set -u
WT=/root/falcon-p6
RUN=/mnt/c/temp/proxmox-vm/audits/runs/falcon/20261003-0018-fix-backup-abort-markers-20b5e57/remediation/PATCH-6
LOG="$RUN/verify.log"
cd "$WT" || exit 1
{
echo "# PATCH-6 verification"
echo "date_utc=$(date -u +%FT%TZ)"
echo "worktree=$WT (clean git worktree, LF line endings)"
echo "commit=$(git rev-parse HEAD)"
echo "declared_commit=$(sed -n 's/^repository_commit=//p' PACKAGE_DIGEST.txt)"
echo
echo "## 1. publication equality checker (full git mode)"
python3 automation/validation/check_publication_equality.py --root .; echo "check_publication_equality exit=$?"
echo
echo "## 2. publication equality offline regression"
bash automation/validation/tests/publication_equality_test.sh; echo "publication_equality_test exit=$?"
echo
echo "## 3. existing digest tests"
bash automation/validation/tests/digest_binding_check_test.sh; echo "digest_binding_check_test exit=$?"
bash automation/validation/tests/digest_verdict_consistency_test.sh; echo "digest_verdict_consistency_test exit=$?"
echo
echo "## 4. verify_publication_chain.sh (signed archive guard optional in this runner)"
FALCON_SIGNED_GUARD_OPTIONAL=1 bash automation/validation/verify_publication_chain.sh; echo "verify_publication_chain exit=$?"
echo
echo "## 5. full ci/validate.py (evidence optional)"
FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py; echo "ci_validate_full exit=$?"
echo
echo "## 6. gitleaks"
GL="$(command -v gitleaks || true)"
[ -z "$GL" ] && [ -x /root/bin/gitleaks ] && GL=/root/bin/gitleaks
if [ -n "$GL" ]; then
  "$GL" detect --no-git --source . --redact --config .gitleaks.toml; echo "gitleaks exit=$?"
else
  echo "gitleaks NOT INSTALLED in this runner -> not run"
fi
} > "$LOG" 2>&1
tail -4 "$LOG"
