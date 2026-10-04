#!/usr/bin/env bash
# Mirrors the "Ensure generated license/SBOM artifacts stay untracked" step in
# .github/workflows/test.yml so it can be exercised in the lab.
set -u
tracked="$(git ls-files -- licenses.json sbom.cdx.json sbom.spdx.json)"
if [ -n "$tracked" ]; then
  echo "GUARD_FAIL: generated artifact(s) are tracked: $tracked"
  exit 1
fi
echo "GUARD_PASS: generated artifacts are untracked"
