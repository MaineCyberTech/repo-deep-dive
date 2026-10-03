#!/usr/bin/env bash
# check_run.sh — validate a repo-deep-dive run folder (falcon-lab aware).
# Read-only. Usage: tools/check_run.sh <run-folder>
set -euo pipefail

RUN="${1:-}"
if [[ -z "$RUN" || ! -d "$RUN" ]]; then
  echo "usage: $0 <run-folder>" >&2
  exit 2
fi
RUN="${RUN%/}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fail=0
ok()  { printf '  OK   %s\n' "$1"; }
bad() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

echo "Checking run: $RUN"

# --- 1. Common required finals -------------------------------------------------
for f in INDEX.md EXECUTIVE_SUMMARY.md RELEASE_GATE.md risk_register.md roadmap.md patch_plan.md audit_manifest.json; do
  if [[ -f "$RUN/$f" ]]; then ok "$f"; else bad "$f missing"; fi
done

# --- 2. Manifest JSON + required keys ------------------------------------------
MAN="$RUN/audit_manifest.json"
profile=""
if [[ -f "$MAN" ]]; then
  if man_out=$(python3 - "$MAN" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
req = ["pack", "profile", "run", "scope", "findings"]
missing = [k for k in req if k not in d]
if missing:
    raise SystemExit("missing keys: " + ",".join(missing))
total = d.get("findings", {}).get("total", "?")
print(f"run={d['run']} profile={d.get('profile')} findings={total}")
PY
  ); then
    ok "manifest parses ($man_out)"
    profile=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('profile',''))" "$MAN" 2>/dev/null || true)
  else
    bad "manifest invalid or missing keys"
  fi
fi

# --- 3. Falcon-lab extras ------------------------------------------------------
if [[ "$profile" == "falcon-lab" ]]; then
  for f in lens_new_developer.md lens_independent_reviewer.md lens_integration.md lens_live_operations.md follow_up_register.md; do
    if [[ -f "$RUN/$f" ]]; then ok "$f"; else bad "$f missing (falcon-lab)"; fi
  done
fi

# --- 4. Finding-ID consistency (register vs follow-up vs manifest) -------------
if [[ -f "$RUN/risk_register.md" && -f "$RUN/follow_up_register.md" ]]; then
  if id_out=$(python3 - "$RUN/risk_register.md" "$RUN/follow_up_register.md" "$MAN" <<'PY'
import json, re, sys

ID = r'([A-Z]+-P[0-3]-\d{3})'

def ids_from_table(path):
    out = set()
    for line in open(path, encoding="utf-8"):
        m = re.match(r'^\| ' + ID + r' \|', line)
        if m:
            out.add(m.group(1))
    return out

rr = ids_from_table(sys.argv[1])
fu = ids_from_table(sys.argv[2])
if rr != fu:
    print(f"ID mismatch: risk={len(rr)} follow_up={len(fu)} "
          f"only_risk={sorted(rr - fu)[:5]} only_follow_up={sorted(fu - rr)[:5]}")
    raise SystemExit(1)

total = None
try:
    total = json.load(open(sys.argv[3])).get("findings", {}).get("total")
except Exception:
    pass
if isinstance(total, int) and total != len(rr):
    print(f"manifest findings.total={total} != register rows={len(rr)}")
    raise SystemExit(1)

sev = {}
for i in rr:
    sev[i.split("-")[1]] = sev.get(i.split("-")[1], 0) + 1
print(f"{len(rr)} findings ({', '.join(f'{k} x{v}' for k, v in sorted(sev.items()))})")
PY
  ); then
    ok "finding-ID consistency ($id_out)"
  else
    bad "finding-ID consistency"
  fi
fi

# --- 4b. Duplicate finding IDs (load-bearing for registers/CSVs/diffs) --------
if dupe_out=$(python3 - "$RUN" "$SCRIPT_DIR" <<'PY'
import sys
sys.path.insert(0, sys.argv[2])
sys.dont_write_bytecode = True
import lib_findings
run, findings, dupes = lib_findings.collect_with_dupes(sys.argv[1])
if dupes:
    print("; ".join("%s in %s" % (k, ",".join(v)) for k, v in sorted(dupes.items())))
    raise SystemExit(1)
print("%d unique IDs" % len(findings))
PY
); then
  ok "finding IDs unique ($dupe_out)"
else
  bad "duplicate finding IDs ($dupe_out)"
fi

# --- 4c. Status vocabulary (load-bearing for diffs/CSVs/verification) ------------
if status_out=$(python3 - "$RUN" "$SCRIPT_DIR" <<'PY'
import sys
sys.path.insert(0, sys.argv[2])
sys.dont_write_bytecode = True
import lib_findings
allowed = {"", "open", "partially-fixed", "verified-fixed", "still-open", "regressed", "owner-accepted"}
fields = lib_findings.register_fields(sys.argv[1])
bad = sorted("%s=%s" % (fid, v["status"]) for fid, v in fields.items() if v["status"] not in allowed)
if bad:
    print("; ".join(bad))
    raise SystemExit(1)
print("%d statuses ok" % len(fields))
PY
); then
  ok "finding statuses use the shared vocabulary ($status_out)"
else
  bad "unknown finding status values ($status_out)"
fi

# --- 5. Source reports (informational) -----------------------------------------
if [[ -d "$RUN/source_reports" ]]; then
  ok "source_reports present ($(find "$RUN/source_reports" -name '*.md' | wc -l) md files)"
fi

# --- Result ---------------------------------------------------------------------
echo
if [[ $fail -eq 0 ]]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL ($fail check(s))"
  exit 1
fi
