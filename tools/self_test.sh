#!/usr/bin/env bash
# self_test.sh — exercise the pack's tools end-to-end against the archived runs (read-only).
# Usage: tools/self_test.sh
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
ok()  { printf '  OK   %s\n' "$1"; }
bad() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Self-test: $(pwd)"
echo

# --- 1. Pack lint ---------------------------------------------------------------
if ./tools/lint_pack.sh > "$TMP/lint.out" 2>&1; then
  ok "lint_pack.sh"
else
  bad "lint_pack.sh"
  sed 's/^/    /' "$TMP/lint.out"
fi

# --- 1b. Gitleaks allowlists + negative fixture ---------------------------------
if ./tools/verify_gitleaks_config.sh > "$TMP/gitleaks.out" 2>&1; then
  ok "verify_gitleaks_config.sh"
else
  bad "verify_gitleaks_config.sh"
  sed 's/^/    /' "$TMP/gitleaks.out"
fi

# --- 2. Per-run tool checks -----------------------------------------------------
found_runs=0
for d in runs/*/; do
  [[ -f "${d}audit_manifest.json" ]] || continue
  found_runs=$((found_runs + 1))

  if ./tools/check_run.sh "$d" > "$TMP/run.out" 2>&1; then
    ok "check_run.sh ${d%/}"
  else
    bad "check_run.sh ${d%/}"
    sed 's/^/    /' "$TMP/run.out"
  fi

  total=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['findings']['total'])" "${d}audit_manifest.json")
  got=$(./tools/collect_findings.py "$d" | sed -n 's/^findings: \([0-9][0-9]*\).*/\1/p')
  if [[ "$got" == "$total" ]]; then
    ok "collect_findings.py ${d%/} ($got findings)"
  else
    bad "collect_findings.py ${d%/}: got '$got', manifest says '$total'"
  fi

  ./tools/diff_runs.py "$d" "$d" > "$TMP/diff.out" 2>&1 || true
  if grep -qE '^- .*: [1-9][0-9]*$' "$TMP/diff.out"; then
    bad "diff_runs.py self-compare not all-zero"
    sed 's/^/    /' "$TMP/diff.out"
  else
    ok "diff_runs.py self-compare (all zero)"
  fi

  ./tools/findings_to_csv.py "$d" -o "$TMP/findings.csv" > /dev/null
  rows=$(( $(wc -l < "$TMP/findings.csv") - 1 ))
  if [[ "$rows" == "$total" ]]; then
    ok "findings_to_csv.py ($rows rows)"
  else
    bad "findings_to_csv.py: $rows rows vs $total findings"
  fi

  if ./tools/risk_score.py "$d" > "$TMP/score.out" 2>&1 && grep -q "^score: [0-9][0-9]*/100$" "$TMP/score.out"; then
    ok "risk_score.py ${d%/} ($(sed -n 's/^score: //p' "$TMP/score.out"))"
  else
    bad "risk_score.py ${d%/}"
    sed 's/^/    /' "$TMP/score.out"
  fi

  if ./tools/render_dashboard.py "$d" > "$TMP/dash.out" 2>&1 && grep -q "^findings: " "$TMP/dash.out"; then
    ok "render_dashboard.py ${d%/} (read-only render)"
  else
    bad "render_dashboard.py ${d%/}"
    sed 's/^/    /' "$TMP/dash.out"
  fi

  # Schema contract: regenerate findings.json from the run's reports in a TMP
  # copy (archived findings.json predate the integer `sourceReports` contract)
  # and validate the whole document, types included, against the schema.
  rm -rf "$TMP/schema-run"
  cp -R "$d" "$TMP/schema-run"
  if ./tools/collect_findings.py "$TMP/schema-run" --write > /dev/null 2>&1 \
    && python3 - "$TMP/schema-run/findings.json" <<'PY' > /dev/null 2>&1
import json, re, sys

schema = json.load(open("schemas/findings.schema.json"))
doc = json.load(open(sys.argv[1]))


def check(val, spec, path):
    if "enum" in spec:
        assert val in spec["enum"], path
    t = spec.get("type")
    if t == "object":
        assert isinstance(val, dict), path
        for k in spec.get("required", []):
            assert k in val, "%s: missing %s" % (path, k)
        props = spec.get("properties", {})
        for k, sub in props.items():
            if k in val:
                check(val[k], sub, "%s.%s" % (path, k))
        extra = spec.get("additionalProperties")
        if isinstance(extra, dict):
            for k, v in val.items():
                if k not in props:
                    check(v, extra, "%s.%s" % (path, k))
    elif t == "array":
        assert isinstance(val, list), path
        if "items" in spec:
            for i, v in enumerate(val):
                check(v, spec["items"], "%s[%d]" % (path, i))
    elif t == "integer":
        assert isinstance(val, int) and not isinstance(val, bool), path
        if "minimum" in spec:
            assert val >= spec["minimum"], path
    elif t == "string":
        assert isinstance(val, str), path
        if "minLength" in spec:
            assert len(val) >= spec["minLength"], path
        if "pattern" in spec:
            assert re.match(spec["pattern"], val), path


try:
    import jsonschema
except ImportError:
    check(doc, schema, "$")
else:
    jsonschema.validate(doc, schema)
PY
  then
    ok "findings.schema.json type conformance ${d%/} (regenerated)"
  else
    bad "findings.schema.json type conformance ${d%/} (regenerated)"
  fi
done
[[ $found_runs -gt 0 ]] || bad "no archived runs found under runs/"

# --- 2b. Repo inventory (read-only scan of the pack itself) ----------------------
if ./tools/repo_inventory.py . -o "$TMP/inventory.json" > /dev/null 2>&1 \
  && python3 -c "import json,sys;d=json.load(open(sys.argv[1]));assert d['totals']['files']>0 and 'prompts' in str(d['largest_dirs'])" "$TMP/inventory.json"; then
  ok "repo_inventory.py (self-scan)"
else
  bad "repo_inventory.py (self-scan)"
fi

# --- 2c. Toolchain + scaffolder (read-only; TMP only) ---------------------------
first_run=""
for d in runs/*/; do
  [[ -f "${d}audit_manifest.json" ]] && { first_run="$d"; break; }
done
if [[ -n "$first_run" ]] && ./tools/run_toolchain.py "$first_run" > "$TMP/chain.out" 2>&1 \
  && grep -q "TOOLCHAIN: PASS" "$TMP/chain.out"; then
  ok "run_toolchain.py (read-only chain)"
else
  bad "run_toolchain.py (read-only chain)"
  sed 's/^/    /' "$TMP/chain.out" 2>/dev/null || true
fi

if ./tools/new_run.py --run selftest-manual --root "$TMP/audits" --profile falcon-lab \
  --repo /tmp/fake --branch main --sha abc1234 > /dev/null 2>&1 \
  && [[ -f "$TMP/audits/repo-deep-dive/selftest-manual/audit_manifest.json" ]] \
  && [[ -f "$TMP/audits/repo-deep-dive/selftest-manual/INDEX.md" ]]; then
  ok "new_run.py (TMP scaffold)"
else
  bad "new_run.py (TMP scaffold)"
fi

# --- 3. Live snapshot (read-only; safe on any Linux host) ------------------------
if ./tools/live_snapshot.sh "$TMP/snap.txt" > /dev/null 2>&1 && grep -q "# Live snapshot" "$TMP/snap.txt"; then
  ok "live_snapshot.sh (read-only capture)"
else
  bad "live_snapshot.sh"
fi

# --- Result ----------------------------------------------------------------------
echo
if [[ $fail -eq 0 ]]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL ($fail check(s))"
  exit 1
fi
