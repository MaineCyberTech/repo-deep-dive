#!/usr/bin/env bash
# Verify .gitleaks.toml:
#   1. the tracked pack is clean under the reviewed allowlists, and
#   2. a synthetic generic-api-key is STILL detected (negative fixture), so a
#      rule-scoped allowlist cannot silently grow to swallow a real secret.
#
# gitleaks is an optional external tool; when it is not installed this exits 0
# with a notice, so the check can run in any environment (and is a no-op in CI
# jobs that do not install it).
#
# Usage: tools/verify_gitleaks_config.sh
set -euo pipefail
cd "$(dirname "$0")/.."

fixture="tests/fixtures/gitleaks-negative.env.fixture"
config=".gitleaks.toml"

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "gitleaks not installed; skipping gitleaks config verification"
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "1/2 full-tree scan under .gitleaks.toml must be clean"
if ! gitleaks detect --source "$PWD" --no-git --redact --exit-code 1 \
      --report-format json --report-path "$TMP/repo.json" \
      --config "$config" >/dev/null 2>&1; then
  echo "FAIL: gitleaks reported findings in the tracked pack" >&2
  exit 1
fi
echo "    OK: no findings"

echo "2/2 negative fixture must still be detected"
mkdir -p "$TMP/neg"
# shellcheck disable=SC1090
. "$fixture"
printf 'API_KEY = "%s%s"\n' "$NEG_LEFT" "$NEG_RIGHT" > "$TMP/neg/negative.env"
if gitleaks detect --source "$TMP/neg" --no-git --redact --exit-code 1 \
      --report-format json --report-path "$TMP/negative.json" \
      --config "$config" >/dev/null 2>&1; then
  echo "FAIL: negative fixture was not detected; the allowlist is too broad" >&2
  exit 1
fi
echo "    OK: synthetic key detected"

echo "PASS: gitleaks config verification"
