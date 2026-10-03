#!/usr/bin/env bash
# PS-003 verification harness (repo-deep-dive remediation) - RETRY.
# Uses the repository's real gates (lint_pack.sh / self_test.sh / actionlint).
# Runs in WSL Ubuntu-24.04 against the separate clone. Read-only except TMP.
set -uo pipefail

REPO="/mnt/c/temp/repo-deep-dive-rem"
RUN="/mnt/c/temp/proxmox-vm/audits/runs/repo-deep-dive/20261003-0018-main-7bac320"
TOOLS="$RUN/remediation/PS-003/tools"
GITLEAKS="$TOOLS/gitleaks"
ACTIONLINT="$TOOLS/actionlint"
WF=".github/workflows/deep-dive-deterministic.yml"

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
echo "gitleaks: $($GITLEAKS version)"
echo "actionlint: $($ACTIONLINT --version 2>&1 | head -1)"
echo

echo "### 1. actionlint -no-color $WF"
$ACTIONLINT -no-color "$WF"
step "actionlint" $?
echo

echo "### 2. Every uses: ref in the changed workflow is pinned to a 40-hex SHA"
grep -n 'uses:' "$WF"
unpinned=$(grep -nE 'uses:' "$WF" | grep -vE '@[0-9a-f]{40}\b' || true)
if [ -z "$unpinned" ]; then step "uses-sha-pinned" 0; else echo "UNPINNED:"; echo "$unpinned"; step "uses-sha-pinned" 1; fi
echo

echo "### 3. Tool downloads are versioned + sha256-verified (>= 4 of each)"
dl=$(grep -cE 'releases/download/' "$WF")
ver=$(grep -cE '^ {10}[A-Z_]+_VERSION: "[0-9][0-9.]*"' "$WF")
sha=$(grep -cE 'sha256sum -c -' "$WF")
echo "pinned-version env vars: $ver ; download URLs: $dl ; sha256 checks: $sha"
grep -nE 'releases/download/' "$WF"
if [ "$ver" -ge 4 ] && [ "$dl" -ge 4 ] && [ "$sha" -ge 4 ]; then step "downloads-pinned-checksummed" 0; else step "downloads-pinned-checksummed" 1; fi
echo

echo "### 4. Token is not embedded in the clone URL (SEC-P1-002)"
if grep -qE 'x-access-token:.*GH_TOKEN|https://[^"]*GH_TOKEN@' "$WF"; then
  echo "token still in URL:"; grep -nE 'x-access-token|GH_TOKEN@' "$WF"; step "no-token-in-url" 1
else
  grep -n 'http.extraheader\|add-mask\|credential.helper' "$WF"
  step "no-token-in-url" 0
fi
echo

echo "### 5. bash tools/lint_pack.sh"
bash tools/lint_pack.sh
step "lint_pack.sh" $?
echo

echo "### 6. bash tools/self_test.sh"
bash tools/self_test.sh
step "self_test.sh" $?
echo

echo "### 7. .gitleaks.toml proof: real-format GitHub PAT (ghp_ + 36 [A-Za-z0-9])"
# gitleaks built-in rule github-pat: regex ghp_[0-9a-zA-Z]{36}, entropy >= 3.
# A high-entropy random value avoids the built-in stopword allowlist.
GLT=$(mktemp -d)
mkdir -p "$GLT/examples" "$GLT/src"
cp .gitleaks.toml "$GLT/.gitleaks.toml"
PAT="ghp_$(head -c 96 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 36)"
printf '{"fixture": "%s"}\n' "$PAT" > "$GLT/src/leak.txt"
printf '{"fixture": "%s"}\n' "$PAT" > "$GLT/examples/manifest.example.json"
echo "[7a] non-allowlisted path src/leak.txt must be DETECTED (expect exit 1)"
GITLEAKS_CONFIG="$GLT/.gitleaks.toml" "$GITLEAKS" detect --no-git --no-banner --redact \
  --report-format json --report-path "$GLT/only-a.json" --source "$GLT/src" 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
onlya=$?
python3 -c "import json;d=json.load(open('$GLT/only-a.json'));print('   rules detected:',sorted({x['RuleID'] for x in d}))"
if [ "$onlya" -eq 1 ]; then step "gitleaks-detects-real-pat" 0; else echo "   src/leak.txt not detected (exit $onlya)"; step "gitleaks-detects-real-pat" 1; fi
echo "[7b] allowlisted examples/*.example.json must be SUPPRESSED (expect exit 0)"
GITLEAKS_CONFIG="$GLT/.gitleaks.toml" "$GITLEAKS" detect --no-git --no-banner --redact \
  --report-format json --report-path "$GLT/only-ex.json" --source "$GLT/examples" 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
ex=$?
if [ "$ex" -eq 0 ]; then step "gitleaks-allowlist-suppresses" 0; else echo "   examples fixture flagged (exit $ex)"; step "gitleaks-allowlist-suppresses" 1; fi
rm -rf "$GLT"
echo

echo "### 8. Changed-file secret scan with the new config (CI gate parity)"
scan=$(mktemp -d)
mkdir -p "$scan/.github/workflows"
cp .gitleaks.toml "$scan/"
cp .github/dependabot.yml "$scan/.github/"
cp "$WF" "$scan/.github/workflows/"
GITLEAKS_CONFIG="$scan/.gitleaks.toml" "$GITLEAKS" detect --no-git --no-banner --redact \
  --source "$scan" 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
step "changed-files-no-secrets" $?
rm -rf "$scan"
echo

echo "### 9. Gate logic: P1 SEC finding fails, clean passes (SEC-P2-003 / OBS-P2-002)"
gate=$(mktemp -d)
mkdir -p "$gate/out/orgrepo"
gate_py() {
python3 - <<'PY'
import glob, json, sys
hits = []
for p in sorted(glob.glob("out/*/deterministic-findings.json")):
    try:
        doc = json.load(open(p, encoding="utf-8"))
    except Exception as exc:
        print("::error::could not read %s: %s" % (p, exc), file=sys.stderr)
        sys.exit(2)
    for f in doc.get("findings", []):
        fid = str(f.get("id", ""))
        if f.get("severity") == "P1" and fid.startswith("SEC-"):
            hits.append("%s: %s - %s" % (p, fid, f.get("title", "")))
if hits:
    print("::error::P1 secret finding(s) detected; failing closed:")
    for h in hits:
        print("  " + h)
    sys.exit(1)
print("no P1 secret findings")
PY
}
cat > "$gate/out/orgrepo/deterministic-findings.json" <<'JSON'
{"counts":{"total":1},"findings":[{"id":"SEC-P1-001","severity":"P1","title":"gitleaks: github-pat (1 hit(s))"}]}
JSON
( cd "$gate" && gate_py ); gneg=$?
cat > "$gate/out/orgrepo/deterministic-findings.json" <<'JSON'
{"counts":{"total":0},"findings":[]}
JSON
( cd "$gate" && gate_py ); gpos=$?
echo "P1 finding -> gate exit $gneg (expect 1); clean -> gate exit $gpos (expect 0)"
if [ "$gneg" -eq 1 ] && [ "$gpos" -eq 0 ]; then step "gate-p1-secret" 0; else step "gate-p1-secret" 1; fi
rm -rf "$gate"
echo

echo "================================"
if [ "$overall" -eq 0 ]; then echo "PS-003 VERIFY RESULT: PASS"; else echo "PS-003 VERIFY RESULT: FAIL"; fi
echo "================================"
exit $overall
