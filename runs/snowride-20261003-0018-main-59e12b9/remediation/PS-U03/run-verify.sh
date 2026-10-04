#!/usr/bin/env bash
# PS-U03 verification on the ci-runner lab (clean LF bundle clone).
# Covers the snowride profile gate plus the two new CI steps and actionlint.
# Raw output + exit codes; no fabrication.
set -u
cd /srv/work/snowride-ps-u03

echo "# PS-U03 verification - unassigned CI findings (CI-P2-001, CI-P2-002)"
echo "commit: $(git rev-parse HEAD)"
echo "branch: $(git rev-parse --abbrev-ref HEAD)"
echo "node:   $(node --version)"
echo "npm:    $(npm --version)"
echo "gitleaks: $(gitleaks version 2>/dev/null || echo unavailable)"
echo "actionlint: $(actionlint --version 2>/dev/null || echo unavailable)"
echo

echo "## actionlint .github/workflows/ci-foundation.yml"
actionlint .github/workflows/ci-foundation.yml
echo "actionlint_exit=$?"
echo

echo "## bash scripts/repo-secret-scan.sh (repository-tree secret scan)"
bash scripts/repo-secret-scan.sh
echo "secret_scan_exit=$?"
echo

echo "## npm ci"
npm ci
echo "npm_ci_exit=$?"
echo

echo "## npm audit --omit=dev --audit-level=high"
npm audit --omit=dev --audit-level=high
echo "audit_exit=$?"
echo

echo "## npm run lint"
npm run lint
echo "lint_exit=$?"
echo

echo "## npm test"
npm test
echo "test_exit=$?"
echo

echo "## git status --short (generated files are not committed)"
git status --short
echo "git_status_exit=$?"
