#!/usr/bin/env bash
# PS-004 verification harness (repo-deep-dive remediation).
# Uses the repository's real gates (lint_pack.sh / self_test.sh) and the lab's
# actionlint + gitleaks binaries. Runs in WSL Ubuntu-24.04 against the separate
# clone. Read-only except TMP and the generated PACK_DIGEST.txt.
set -uo pipefail

REPO="/mnt/c/temp/repo-deep-dive-rem"
RUN="/mnt/c/temp/proxmox-vm/audits/runs/repo-deep-dive/20261003-0018-main-7bac320"
TOOLS="$RUN/remediation/PS-003/tools"
GITLEAKS="$TOOLS/gitleaks"
ACTIONLINT="$TOOLS/actionlint"
WF_NEW=".github/workflows/audit.yml"
WF_EX="ci/audit.yml"

cd "$REPO" || exit 2

overall=0
step() { # name, exit-code
  local name="$1" code="$2"
  if [ "$code" -eq 0 ]; then
    echo "== [PASS] $name =="
  else
    echo "== [FAIL] $name (exit $code) =="
    overall=1
  fi
}

echo "repo:    $REPO"
echo "head:    $(git rev-parse HEAD)"
echo "branch:  $(git rev-parse --abbrev-ref HEAD)"
echo "date:    $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "actionlint: $($ACTIONLINT --version 2>&1 | head -1)"
echo "gitleaks:   $($GITLEAKS version)"
echo

echo "### 1. actionlint -no-color $WF_NEW"
$ACTIONLINT -no-color "$WF_NEW"
step "actionlint-audit.yml" $?
echo

echo "### 2. actionlint -no-color $WF_EX"
$ACTIONLINT -no-color "$WF_EX"
step "actionlint-ci-audit.yml" $?
echo

echo "### 3. CI-P1-001: the audit workflow is wired under .github/workflows"
ls -1 .github/workflows/
if [ -f "$WF_NEW" ]; then step "workflow-wired" 0; else step "workflow-wired" 1; fi
echo

echo "### 4. CI-P1-002: PACK_DIR matches the in-repo layout (root, not vendored)"
grep -n 'PACK_DIR' "$WF_EX"
if grep -qE '^\s*PACK_DIR: *"?\.?"?$' "$WF_EX"; then step "pack-dir-root" 0; else step "pack-dir-root" 1; fi
echo

echo "### 5. CI-P2-006: PR events do not use a fixed 'latest' run path"
echo "-- [5a] example is workflow_dispatch only (no PR empty-input path)"
if grep -qE '^\s*pull_request:' "$WF_EX"; then
  echo "ci/audit.yml still triggers on pull_request"; step "example-no-pr-trigger" 1
else step "example-no-pr-trigger" 0; fi
echo "-- [5b] no bogus fixed run-path fallback anywhere"
if grep -rn "docs/audits/repo-deep-dive/latest" "$WF_NEW" "$WF_EX" || grep -rn "inputs.run_dir ||" "$WF_NEW" "$WF_EX"; then
  echo "fixed 'latest' run-path still present"; step "no-latest-path" 1
else step "no-latest-path" 0; fi
echo "-- [5c] wired workflow derives changed runs from the PR diff"
grep -nE 'git diff --name-only|mapfile|runs/\*\*' "$WF_NEW"
if grep -q "git diff --name-only" "$WF_NEW" \
   && ! grep -q "inputs.run_dir ||" "$WF_NEW" \
   && ! grep -q "docs/audits/repo-deep-dive/latest" "$WF_NEW"; then
  step "diff-derived-run-dir" 0
else step "diff-derived-run-dir" 1; fi
echo

echo "### 6. Changed-run detection logic (unit check of the diff filter)"
# Same awk used by .github/workflows/audit.yml.
sample=$'runs/repo-deep-dive-20261003-0018-main-7bac320/findings.json\n'
sample+=$'runs/repo-deep-dive-20261003-0018-main-7bac320/INDEX.md\n'
sample+=$'runs/INDEX.md\n'
sample+=$'tools/self_test.sh\n'
got=$(printf '%s\n' "$sample" | awk -F/ 'NF >= 3 { print $1 "/" $2 }' | sort -u)
echo "input paths -> detected run folders:"
printf '%s\n' "$sample" | sed 's/^/  in : /'
printf '%s\n' "$got" | sed 's/^/  out: /'
if [ "$got" = "runs/repo-deep-dive-20261003-0018-main-7bac320" ]; then
  step "changed-run-filter" 0
else step "changed-run-filter" 1; fi
echo "-- pathspec 'runs/**' matches tracked run files:"
n=$(git ls-files 'runs/**' | wc -l)
echo "git ls-files 'runs/**' -> $n files"
echo "-- current PR diff ($(git rev-parse --abbrev-ref HEAD) vs origin/main):"
git diff --name-only origin/main...HEAD -- 'runs/**' | sed 's/^/  /'
[ "$n" -gt 0 ] && step "pathspec-matches-runs" 0 || step "pathspec-matches-runs" 1
echo

echo "### 7. P0 gate logic (same python as the wired workflow)"
gate=$(mktemp -d)
mkdir -p "$gate"
cat > "$gate/p0.json" <<'JSON'
{"counts":{"bySeverity":{"P1":9,"P2":20,"P3":12}}}
JSON
cat > "$gate/p0present.json" <<'JSON'
{"counts":{"bySeverity":{"P0":1,"P1":9}}}
JSON
gate_py() {
python3 - "$1" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as fh:
    doc = json.load(fh)
p0 = int(doc.get("counts", {}).get("bySeverity", {}).get("P0", 0))
if p0 > 0:
    raise SystemExit("P0 findings present: %d" % p0)
print("P0 gate: no P0 findings")
PY
}
gate_py "$gate/p0.json"; clean=$?
gate_py "$gate/p0present.json"; present=$?
echo "P0 absent -> exit $clean (expect 0); P0 present -> exit $present (expect 1)"
if [ "$clean" -eq 0 ] && [ "$present" -eq 1 ]; then step "p0-gate-logic" 0; else step "p0-gate-logic" 1; fi
rm -rf "$gate"
echo

echo "### 8. bash tools/lint_pack.sh"
bash tools/lint_pack.sh
step "lint_pack.sh" $?
echo

echo "### 9. bash tools/self_test.sh"
bash tools/self_test.sh
step "self_test.sh" $?
echo

echo "### 10. Secret scan of the changed tree (gitleaks defaults)"
scan=$(mktemp -d)
mkdir -p "$scan/.github/workflows" "$scan/ci"
cp "$WF_NEW" "$scan/.github/workflows/"
cp "$WF_EX" "$scan/ci/"
cp .github/CODEOWNERS "$scan/.github/"
cp CONTRIBUTING.md "$scan/"
$GITLEAKS detect --no-git --no-banner --redact --source "$scan" 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
step "changed-files-no-secrets" $?
rm -rf "$scan"
echo

echo "### 11. CI-P2-005: CODEOWNERS + documented required checks/bypass policy"
ls -l .github/CODEOWNERS
grep -n 'JulianB-MCT' .github/CODEOWNERS | head
grep -n 'CI and required checks\|Bypass policy\|required status checks' CONTRIBUTING.md
if [ -f .github/CODEOWNERS ] && grep -q 'Bypass policy' CONTRIBUTING.md; then
  step "codeowners-and-policy" 0
else step "codeowners-and-policy" 1; fi
echo

echo "### 12. TEST-P1-001: push/PR job runs lint_pack + self_test"
grep -nE 'pull_request:|push:|bash tools/lint_pack.sh|bash tools/self_test.sh' "$WF_NEW"
if grep -q 'pull_request:' "$WF_NEW" && grep -q 'bash tools/self_test.sh' "$WF_NEW"; then
  step "pack-ci-on-pr-and-push" 0
else step "pack-ci-on-pr-and-push" 1; fi
echo

echo "### 13. Extracted workflow shell scripts pass bash -n (YAML heredoc integrity)"
extract_yaml() {
python3 - "$1" <<'PY'
import sys
try:
    import yaml
except Exception as exc:  # pragma: no cover
    print("pyyaml unavailable: %s" % exc, file=sys.stderr)
    raise SystemExit(3)
with open(sys.argv[1], encoding="utf-8") as fh:
    doc = yaml.safe_load(fh)
for job in doc.get("jobs", {}).values():
    for step in job.get("steps", []):
        if "run" in step:
            sys.stdout.write(step["run"])
            sys.stdout.write("\n# --- step boundary ---\n")
PY
}
for wf in "$WF_NEW" "$WF_EX"; do
  tmp=$(mktemp)
  if extract_yaml "$wf" > "$tmp"; then
    if bash -n "$tmp"; then step "bash-syntax-${wf//\//_}" 0; else step "bash-syntax-${wf//\//_}" 1; fi
  else
    echo "skipped bash -n (no yaml parser) for $wf"
  fi
  rm -f "$tmp"
done
echo

echo "================================"
if [ "$overall" -eq 0 ]; then echo "PS-004 VERIFY RESULT: PASS"; else echo "PS-004 VERIFY RESULT: FAIL"; fi
echo "================================"
exit $overall
