#!/usr/bin/env bash
# PS-014 verification on edge-builder: git-archive tree of the committed fix.
set -u
WORK=/srv/work/falcon-edge-ps014
rm -rf "$WORK"
mkdir -p "$WORK"
cd "$WORK" || exit 1
tar xzf /tmp/falcon-edge-ps014.tar.gz
# git-initialise so ci/validate.sh's `git ls-files` json/yaml parse loop runs.
git init -q 2>/dev/null || true
git add -A 2>/dev/null || true

echo "REMEDIATION PS-014 verify.log"
echo "REPO: falcon-edge   BASE: origin/main   BRANCH: remediation/ps-014-20261003-0018-fix-trust-root-87532ec"
echo "COMMIT: efe174a9af2d995ca2e4749b062a8b2bb8245aec (source tree; git archive HEAD preserves modes/LF)"
echo "FINDINGS: API-P3-001, API-P3-002, FEAT-P3-001 (already fixed upstream), FEAT-P3-002"
echo "METHOD: local 'git archive --format=tar.gz HEAD' -> scp -> remote extract; git-initialised for validate.sh"
echo "HOST: $(hostname)  $(uname -srm)"
echo "DATE: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "PYTHON: $(python3 --version 2>&1)"
echo "PYTEST: $(python3 -m pytest --version 2>&1)"
echo "GITLEAKS: $(gitleaks version 2>&1)"
echo "tracked files: $(git ls-files | wc -l)"
echo

run() {
  echo "===== COMMAND: $* ====="
  "$@" 2>&1
  local rc=$?
  echo "[exit=$rc]"
  echo
  return $rc
}

rc_all=0
# Declared patch-set gate.
run python3 -m pytest -q tests/phase2 tests/phase3 || rc_all=1
# API-P3-001 / API-P3-002 focused regressions.
run python3 -m pytest -q tests/phase2/test_api_polish.py -v || rc_all=1
# FEAT-P3-002 CLI regressions.
run python3 -m pytest -q tests/phase4/test_cli.py -k create_token || rc_all=1
# Existing Vector ingest suite must still pass.
run python3 -m pytest -q tests/phase6/test_ingest_endpoint.py || rc_all=1
# Repo gate.
run bash ci/validate.sh || rc_all=1
# Secret gate.
run gitleaks detect --no-git --redact --source . -v || rc_all=1

echo "===== PS-014 VERIFY DONE (rc_all=$rc_all) ====="
exit $rc_all
