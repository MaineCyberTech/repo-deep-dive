#!/usr/bin/env bash
# P1-3 verification on the ci-runner lab (clean worktree /srv/work/snowride).
# Runs the snowride profile gate plus SBOM generation/validation and actionlint.
# Real output + exit codes.
set -u
# Run in the clean LF git worktree (the lab-sync tar copy carries Windows CRLF,
# which breaks vitest's .ts transform for tests/ledger-format.test.ts).
cd /srv/work/snowride-p1-3

echo "# P1-3 verification - SBOM in CI (SUPPLY-P1-001, CI-P3-001)"
echo "commit: $(git rev-parse HEAD)"
echo "branch: $(git rev-parse --abbrev-ref HEAD)"
echo "node:   $(node --version)"
echo "npm:    $(npm --version)"
echo

echo "## npm ci"
npm ci
echo "npm_ci_exit=$?"
echo

echo "## npx --no-install @cyclonedx/cyclonedx-npm --output-file sbom.json"
npx --no-install @cyclonedx/cyclonedx-npm --output-file sbom.json
echo "sbom_gen_exit=$?"
echo

echo "## validate sbom.json (bomFormat/specVersion/components)"
node -e 'const fs=require("fs");const b=JSON.parse(fs.readFileSync("sbom.json","utf8"));if(b.bomFormat!=="CycloneDX"){console.error("bad bomFormat "+b.bomFormat);process.exit(1)}if(b.specVersion==null||!Array.isArray(b.components)||b.components.length===0){console.error("missing specVersion/components");process.exit(1)}console.log("SBOM OK bomFormat="+b.bomFormat+" specVersion="+b.specVersion+" components="+b.components.length)'
echo "sbom_validate_exit=$?"
echo

echo "## npm run lint"
npm run lint
echo "lint_exit=$?"
echo

echo "## npm test"
npm test
echo "test_exit=$?"
echo

echo "## actionlint .github/workflows/ci-foundation.yml"
actionlint .github/workflows/ci-foundation.yml
echo "actionlint_exit=$?"
echo

echo "## git status --short (sbom.json is generated, not committed)"
git status --short
echo "git_status_exit=$?"
