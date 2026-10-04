#!/usr/bin/env bash
# PS-011 verification — Ownership and gate (EXEC-P2-001, EXEC-P3-002)
# Runs against the patched clone. Read-only w.r.t. the repo.
set -uo pipefail

REPO=${REPO:-/mnt/c/temp/repo-deep-dive-rem}
PS004_REF=${PS004_REF:-origin/remediation/ps-004-20261003-0018-main-7bac320}
RUN_DIR=runs/repo-deep-dive-20261003-0018-main-7bac320
GITLEAKS=${GITLEAKS:-/mnt/c/temp/proxmox-vm/audits/runs/repo-deep-dive/20261003-0018-main-7bac320/remediation/PS-003/tools/gitleaks}

cd "$REPO"
echo "repo:    $REPO"
echo "head:    $(git rev-parse HEAD)"
echo "branch:  $(git rev-parse --abbrev-ref HEAD)"
echo "base:    $(git rev-parse origin/main)"
date -u +"date:    %Y-%m-%dT%H:%M:%SZ"
echo "gitleaks: $($GITLEAKS version 2>&1 | head -1)"
echo

fail=0
pass() { echo "== [PASS] $1"; }
bad()  { echo "== [FAIL] $1"; fail=$((fail+1)); }

echo "### 1. EXEC-P2-001: .github/CODEOWNERS exists and routes review"
if [[ -f .github/CODEOWNERS ]]; then
  echo "-- file: $(wc -c < .github/CODEOWNERS) bytes, UTF-8: $(file -b .github/CODEOWNERS)"
  echo "-- routing lines:"
  grep -nE '^[*/@]' .github/CODEOWNERS
  if grep -qE '^\*\s+@' .github/CODEOWNERS && grep -qE '^/\.github/\s+@' .github/CODEOWNERS; then
    pass "codeowners-routing"
  else
    bad "codeowners-routing"
  fi
else
  bad "codeowners-missing"
fi

echo "### 2. Overlap coordination: PS-011 CODEOWNERS == PS-004 CODEOWNERS"
if git show "$PS004_REF:.github/CODEOWNERS" > /tmp/ps011-codeowners-ps004 2>/dev/null; then
  if diff -q /tmp/ps011-codeowners-ps004 .github/CODEOWNERS >/dev/null; then
    pass "codeowners-identical-to-PS004 (merge-safe; overlap noted)"
    echo "-- both add the same file; merging either order is conflict-free"
  else
    bad "codeowners-differs-from-PS004 (conflict risk)"
    diff /tmp/ps011-codeowners-ps004 .github/CODEOWNERS || true
  fi
else
  echo "-- PS-004 ref not fetched; skipping cross-check"
  bad "ps004-ref-missing"
fi

echo "### 3. EXEC-P2-001: gate owner resolved and patch sets mapped"
if grep -q 'Gate owner: `@JulianB-MCT`' "$RUN_DIR/RELEASE_GATE.md"; then
  pass "gate-owner-resolved"
else
  bad "gate-owner-unresolved"
fi
if grep -q 'Patch set' "$RUN_DIR/RELEASE_GATE.md" && grep -q 'PS-001 … PS-011' "$RUN_DIR/RELEASE_GATE.md"; then
  pass "patch-set-owner-mapping"
else
  bad "patch-set-owner-mapping"
fi
if grep -q 'Unknown' "$RUN_DIR/RELEASE_GATE.md"; then
  bad "gate-still-says-unknown"
else
  pass "no-unknown-owner"
fi

echo "### 4. EXEC-P3-002: reproduce the base-profile scaffold defect (dependency PS-002)"
rm -rf /tmp/ps011-scaffold && mkdir -p /tmp/ps011-scaffold
python3 tools/new_run.py --run test-ps011 --name repo-deep-dive \
  --root /tmp/ps011-scaffold --profile base >/tmp/ps011-newrun.out 2>&1
echo "-- new_run.py exit=$?"
cat /tmp/ps011-newrun.out
echo "-- seed manifest keys:"
python3 -c "import json;print(sorted(json.load(open('/tmp/ps011-scaffold/repo-deep-dive/test-ps011/audit_manifest.json')).keys()))"
set +e
out=$(bash tools/check_run.sh /tmp/ps011-scaffold/repo-deep-dive/test-ps011 2>&1); rc=$?
set -e
echo "$out"
if [[ $rc -ne 0 ]] && echo "$out" | grep -q 'RESULT: FAIL'; then
  pass "scaffold-defect-reproduced (check_run exit=$rc) -> condition 1 PASS capture blocked by PS-002"
else
  bad "scaffold-defect-not-reproduced"
fi
rm -rf /tmp/ps011-scaffold

echo "### 5. tools/self_test.sh"
set +e
bash tools/self_test.sh; rc=$?
set -e
if [[ $rc -eq 0 ]]; then pass "self_test.sh (exit=$rc)"; else bad "self_test.sh (exit=$rc)"; fi

echo "### 6. tools/lint_pack.sh"
set +e
bash tools/lint_pack.sh; rc=$?
set -e
if [[ $rc -eq 0 ]]; then pass "lint_pack.sh (exit=$rc)"; else bad "lint_pack.sh (exit=$rc)"; fi

echo "### 7. PACK_DIGEST.txt is current (lint gate + stable inventory)"
# lint_pack.sh check 8 already verified digest freshness (see section 6).
# Confirm regeneration is stable apart from the generated timestamp header.
body() { grep -v '^# generated:' PACK_DIGEST.txt | sha256sum | cut -d' ' -f1; }
h1=$(body)
bash tools/pack_digest.sh >/dev/null
h2=$(body)
echo "-- inventory sha256 before=$h1 after=$h2"
if [[ "$h1" == "$h2" ]]; then pass "pack-digest-current"; else bad "pack-digest-stale"; fi

echo "### 8. Secret scan of changed files (gitleaks defaults)"
rm -rf /tmp/ps011-scan && mkdir -p /tmp/ps011-scan/.github /tmp/ps011-scan/$RUN_DIR
cp .github/CODEOWNERS /tmp/ps011-scan/.github/CODEOWNERS
cp "$RUN_DIR/RELEASE_GATE.md" "/tmp/ps011-scan/$RUN_DIR/RELEASE_GATE.md"
set +e
$GITLEAKS detect --no-git --redact --source /tmp/ps011-scan --verbose 2>&1 | tail -6
rc=${PIPESTATUS[0]}
set -e
if [[ $rc -eq 0 ]]; then pass "changed-files-no-secrets"; else bad "gitleaks-findings (exit=$rc)"; fi
rm -rf /tmp/ps011-scan

echo
echo "================================"
if [[ $fail -eq 0 ]]; then
  echo "PS-011 VERIFY RESULT: PASS"
else
  echo "PS-011 VERIFY RESULT: FAIL ($fail)"
fi
echo "================================"
exit $fail
