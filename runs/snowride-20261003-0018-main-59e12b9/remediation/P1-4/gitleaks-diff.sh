#!/usr/bin/env bash
set -u
cd /srv/work
{
  echo "# gitleaks detect --no-git --redact --source p1-4-diff.patch"
  gitleaks detect --no-git --redact --source p1-4-diff.patch
  echo "gitleaks_diff_exit=$?"
  echo
  echo "# gitleaks detect --no-git --redact --source snowride-p1-4/docs/runbooks/INCIDENT.md"
  gitleaks detect --no-git --redact --source snowride-p1-4/docs/runbooks/INCIDENT.md
  echo "gitleaks_file_exit=$?"
} > p1-4-gitleaks.log 2>&1
cat p1-4-gitleaks.log
