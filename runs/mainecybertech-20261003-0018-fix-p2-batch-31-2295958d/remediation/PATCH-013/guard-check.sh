#!/usr/bin/env bash
# SUPPLY-P3-002: mirrors the "Reject tracked local secret files" CI step in
# .github/workflows/test.yml. Case A proves the repo is clean; Case B proves the
# guard fails closed when a secret-like path is tracked.
set -u

PATTERN='(^|/)\.env($|\.)|(^|/)supabase/\.temp/'
ALLOW_EXAMPLE='\.env\.example$'
ALLOW_BASELINE='.github/restore-test-baseline.env'

echo "--- Case A: real tree must be clean ---"
BAD="$(git ls-files | grep -E "$PATTERN" | grep -vE "$ALLOW_EXAMPLE" | grep -vx "$ALLOW_BASELINE" || true)"
if [ -n "$BAD" ]; then
  echo "GUARD_FAIL: tracked secret-like files:"
  printf '%s\n' "$BAD"
  exit 1
fi
echo "GUARD_PASS: no tracked local secret files"

echo "--- Case B: synthetic secret path must be detected (fail-closed proof) ---"
SYNTH="$(printf '%s\n' \
  'supabase/.temp/start-secrets/supabase_edge_runtime_mainecybertech-dev/env/docker.env' \
  '.env.local' \
  '.env.example' \
  '.github/restore-test-baseline.env' \
  | grep -E "$PATTERN" | grep -vE "$ALLOW_EXAMPLE" | grep -vx "$ALLOW_BASELINE" || true)"
if [ -z "$SYNTH" ]; then
  echo "GUARD_FAIL: guard did not detect the synthetic secret paths"
  exit 1
fi
echo "GUARD_DETECTED:"
printf '%s\n' "$SYNTH"
EXPECTED="$(printf '%s\n' 'supabase/.temp/start-secrets/supabase_edge_runtime_mainecybertech-dev/env/docker.env' '.env.local')"
if [ "$SYNTH" != "$EXPECTED" ]; then
  echo "GUARD_FAIL: detection set did not match expectation"
  exit 1
fi
echo "GUARD_PASS: guard fails closed on supabase/.temp and .env (excludes examples/baseline)"
