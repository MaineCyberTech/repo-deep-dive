#!/usr/bin/env bash
# binding_ps005.sh - finding-specific assertions for PS-005 (FEAT-P2-001, FEAT-P3-002).
set -uo pipefail
REPO=/mnt/c/temp/repo-deep-dive-rem
cd "$REPO"

echo
echo "===== FINDING-SPECIFIC BINDING CHECKS ====="
echo
echo "--- FEAT-P2-001: VERSION bumped and version fields in sync ---"
python3 - <<'PY'
import json
v = open("VERSION").read().strip()
assert v == "1.5.0", v
readme = open("README.md", encoding="utf-8").read()
assert "v" + v in readme, "README does not reference v" + v
pairs = [
    ("examples/audit_manifest.example.json", "version"),
    ("examples/audit_manifest.falcon-lab.example.json", "packVersion"),
    ("profiles/falcon-lab.manifest.json", "basePackVersion"),
]
for p, k in pairs:
    got = json.load(open(p, encoding="utf-8-sig")).get(k)
    assert got == v, "%s:%s=%s" % (p, k, got)
print("VERSION=%s; README=v%s; 3 JSON version fields=%s -> OK" % (v, v, v))
PY
echo "[exit=$?]"
echo
echo "--- FEAT-P2-001: CHANGELOG names the shipped capabilities at the bumped version ---"
python3 - <<'PY'
lines = open("CHANGELOG.md", encoding="utf-8").read().splitlines()
assert lines[2].startswith("## 2026-10-03") and "(v1.5.0)" in lines[2], lines[2]
entry = "\n".join(lines[2:30])
for needle in ("deterministic_checks.py", "aggregate_findings.py",
               "deep-dive-deterministic.yml", "remediation_plan.py"):
    assert needle in entry, needle
assert "1.4.1" not in lines[2], lines[2]
print("top entry: %s" % lines[2])
print("capabilities named: deterministic_checks.py, aggregate_findings.py, deep-dive-deterministic.yml, remediation_plan.py -> OK")
PY
echo "[exit=$?]"
echo
echo "--- FEAT-P3-002: README tools row lists every tools/* basename ---"
missing=""
for f in tools/*; do
  base="$(basename "$f")"
  grep -qF "$base" README.md || missing="$missing $base"
done
if [[ -z "$missing" ]]; then
  echo "all $(ls tools | wc -l) tool basenames appear in README.md -> OK"
  echo "[exit=0]"
else
  echo "FAIL: missing from README.md:$missing"
  echo "[exit=1]"
fi

