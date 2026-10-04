#!/usr/bin/env bash
# P1-2 verification on the ci-runner lab. Runs the profile's snowride gate plus
# the new branch-protection self-test and actionlint. Real output + exit codes.
set -u
cd /srv/work/snowride-p1-2

echo "# P1-2 verification - branch protection (CI-P1-001)"
echo "commit: $(git rev-parse HEAD)"
echo "node:   $(node --version)"
echo "npm:    $(npm --version)"
echo

echo "## npm ci"
npm ci
echo "npm_ci_exit=$?"
echo

echo "## npm run lint"
npm run lint
echo "lint_exit=$?"
echo

echo "## npm test"
npm test
echo "test_exit=$?"
echo

echo "## npx prettier --check .github/branch-protection.json scripts/verify-branch-protection.mjs tests/branch-protection.test.ts"
npx prettier --check .github/branch-protection.json scripts/verify-branch-protection.mjs tests/branch-protection.test.ts
echo "prettier_exit=$?"
echo

echo "## node scripts/verify-branch-protection.mjs --self-test"
node scripts/verify-branch-protection.mjs --self-test
echo "bp_self_test_exit=$?"
echo

echo "## actionlint .github/workflows/ci-foundation.yml"
actionlint .github/workflows/ci-foundation.yml
echo "actionlint_exit=$?"
