#!/usr/bin/env bash
# PS-U03 pre-push gitleaks gate.
# 1) changed files, no allowlist config (proves the patch adds no secrets);
# 2) full worktree with the committed .gitleaks.toml allowlist (the gate);
# 3) full worktree with the allowlist moved aside to document the audited
#    pre-existing fixture hits that the allowlist covers.
set -u
cd /srv/work/snowride-ps-u03

echo "# PS-U03 pre-push gitleaks gate"
echo
echo "## changed files (no allowlist config)"
for f in .github/workflows/ci-foundation.yml .gitleaks.toml scripts/repo-secret-scan.sh; do
  echo "-- gitleaks --no-git --redact --source $f"
  gitleaks detect --no-git --redact --no-banner --source "$f"
  echo "gitleaks_exit=$?"
done
echo
echo "## full worktree with committed .gitleaks.toml allowlist"
gitleaks detect --no-git --redact --no-banner --source . --config .gitleaks.toml
echo "full_with_allowlist_exit=$?"
echo
echo "## full worktree with allowlist moved aside (audited pre-existing fixtures)"
mv .gitleaks.toml /tmp/ps-u03-gitleaks.toml.off
gitleaks detect --no-git --redact --no-banner --source . \
  --report-format json --report-path /tmp/ps-u03-full-nocfg.json \
  > /tmp/ps-u03-full-nocfg.txt 2>&1
echo "full_without_allowlist_exit=$?"
mv /tmp/ps-u03-gitleaks.toml.off .gitleaks.toml
echo "findings=$(grep -o '"RuleID"' /tmp/ps-u03-full-nocfg.json | wc -l)"
echo "hit files:"
grep -oE '"File":"[^"]+"' /tmp/ps-u03-full-nocfg.json | sort | uniq -c
