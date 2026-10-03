#!/usr/bin/env bash
# lint_pack.sh — self-consistency checks for the repo-deep-dive pack (read-only).
# Usage: tools/lint_pack.sh
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
ok()  { printf '  OK   %s\n' "$1"; }
bad() { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }

echo "Linting pack: $(pwd)"
echo

# --- 1. Version consistency -----------------------------------------------------
V="$(tr -d '[:space:]' < VERSION 2>/dev/null || true)"
if [[ -n "$V" ]]; then ok "VERSION = $V"; else bad "VERSION file missing/empty"; fi
if [[ -n "$V" ]] && grep -q "v$V" README.md; then ok "README references v$V"; else bad "README does not reference v$V"; fi
if [[ -n "$V" ]] && python3 - "$V" <<'PY'
import json, sys
v = sys.argv[1]
pairs = [
    ("examples/audit_manifest.example.json", "version"),
    ("examples/audit_manifest.falcon-lab.example.json", "packVersion"),
    ("profiles/falcon-lab.manifest.json", "basePackVersion"),
]
bad = [f"{p}:{k}={json.load(open(p, encoding='utf-8-sig')).get(k)}" for p, k in pairs if json.load(open(p, encoding='utf-8-sig')).get(k) != v]
if bad:
    print("mismatch: " + ", ".join(bad))
    raise SystemExit(1)
PY
then ok "JSON version fields match VERSION"; else bad "JSON version fields mismatch"; fi

# --- 2. JSON validity -----------------------------------------------------------
n=0; n_bad=0
while IFS= read -r f; do
  n=$((n + 1))
  python3 -c "import json,sys;json.load(open(sys.argv[1], encoding='utf-8-sig'))" "$f" 2>/dev/null || { bad "JSON invalid: $f"; n_bad=$((n_bad + 1)); }
done < <(find . -name '*.json' -not -path './.git/*' | sort)
if [[ $n_bad -eq 0 ]]; then ok "$n JSON files parse"; fi

# --- 3. Area codes unique -------------------------------------------------------
dups="$(grep -h "beginning with" prompts/*.md | sed 's/.*beginning with `\([A-Z]*\)`.*/\1/' | sort | uniq -d || true)"
if [[ -z "$dups" ]]; then ok "area codes unique"; else bad "duplicate area codes: $(echo "$dups" | tr '\n' ' ')"; fi

# --- 4. Prompt structure --------------------------------------------------------
missing=""
for f in prompts/[0-9][0-9]_*.md; do
  case "$f" in *00_SHARED_AUDIT_RULES.md) continue ;; esac
  for s in '@include `00_SHARED_AUDIT_RULES.md`' '## Mission' '## Output path' '## Area code' \
           '## Primary audit questions' '## Scope to analyze' '## Required special checks' \
           '## Required outputs and companion artifacts' '## Step-by-step execution instructions' \
           '## Evidence collection checklist' '## Required report structure' '## Quality bar'; do
    grep -qF "$s" "$f" || missing="$missing; $f: $s"
  done
done
if [[ -z "$missing" ]]; then ok "prompt structure complete"; else bad "prompt structure gaps:${missing}"; fi

# --- 5. Prompt counts -----------------------------------------------------------
actual=$(ls prompts/[0-9][0-9]_*.md | grep -v SHARED | wc -l)
falcon=$(grep -l "Falcon Lab profile" prompts/[0-9][0-9]_*.md | grep -v SHARED | wc -l)
base=$((actual - falcon))
if python3 - "$actual" "$base" <<'PY'
import json, sys
actual, base = int(sys.argv[1]), int(sys.argv[2])
errs = []
pm = json.load(open("profiles/falcon-lab.manifest.json")).get("promptCount")
be = json.load(open("examples/audit_manifest.example.json")).get("promptCount")
if pm != actual: errs.append(f"profile manifest promptCount={pm} != actual {actual}")
if be != base: errs.append(f"base example promptCount={be} != base {base}")
if errs:
    print("; ".join(errs))
    raise SystemExit(1)
PY
then ok "prompt counts (actual $actual = base $base + falcon $falcon)"; else bad "prompt count mismatch"; fi

# --- 5b. Execution order covers every prompt (ARCH-P2-001) ----------------------
# The execution order / prompt status is duplicated across the example manifests
# and the profile manifest; this asserts every prompt file is referenced by
# exactly the right manifest (base vs falcon-lab) so coverage cannot silently drift.
if python3 - <<'PY'
import json, pathlib, re

prompts = sorted(
    p.name for p in pathlib.Path("prompts").glob("[0-9][0-9]_*.md")
    if not p.name.endswith("SHARED_AUDIT_RULES.md")
)
all_nums = {f[:2] for f in prompts}
profile = json.load(open("profiles/falcon-lab.manifest.json", encoding="utf-8-sig"))
falcon_nums = {e["id"] for e in profile.get("addedPrompts", [])}
errs = []


def nums(paths):
    out = set()
    for p in paths:
        m = re.match(r"^(\d\d)_", p)
        if m:
            out.add(m.group(1))
    return out


base = json.load(open("examples/audit_manifest.example.json", encoding="utf-8-sig"))
base_order = nums(base.get("executionOrder", []))
expected_base = all_nums - falcon_nums
if base_order != expected_base:
    errs.append("base example executionOrder set != base prompt set "
                "(missing=%s extra=%s)" % (sorted(expected_base - base_order),
                                           sorted(base_order - expected_base)))

falcon = json.load(open("examples/audit_manifest.falcon-lab.example.json",
                        encoding="utf-8-sig"))
falcon_covered = nums(falcon.get("executionOrder", [])) | nums(falcon.get("naReports", []))
if falcon_covered != all_nums:
    errs.append("falcon example executionOrder+naReports != prompt set "
                "(missing=%s extra=%s)" % (sorted(all_nums - falcon_covered),
                                           sorted(falcon_covered - all_nums)))

ps = profile.get("promptStatus", {})
profile_covered = set(ps.get("run", [])) | set(ps.get("adapted", {})) | set(ps.get("na", {}))
if profile_covered != all_nums:
    errs.append("profile promptStatus != prompt set "
                "(missing=%s extra=%s)" % (sorted(all_nums - profile_covered),
                                           sorted(profile_covered - all_nums)))

wave_refs = set()
for w in profile.get("waves", []):
    wave_refs |= set(w.get("prompts", [])) | set(w.get("na", []))
if wave_refs != all_nums:
    errs.append("profile waves != prompt set "
                "(missing=%s extra=%s)" % (sorted(all_nums - wave_refs),
                                           sorted(wave_refs - all_nums)))

if errs:
    print("; ".join(errs))
    raise SystemExit(1)
print("%d prompts covered by order/status/waves" % len(all_nums))
PY
then ok "execution order/status/waves cover the prompt set"; else bad "execution order/status drift"; fi

# --- 6. Referenced files exist --------------------------------------------------
if python3 - <<'PY'
import json, pathlib
pm = json.load(open("profiles/falcon-lab.manifest.json"))
missing = []
for e in pm.get("addedPrompts", []):
    if not pathlib.Path(e["file"]).exists():
        missing.append(e["file"])
for e in pm.get("lenses", []):
    if not pathlib.Path(e["file"]).exists():
        missing.append(e["file"])
if missing:
    print("missing: " + ", ".join(missing))
    raise SystemExit(1)
PY
then ok "profile manifest references resolve"; else bad "profile manifest references missing"; fi

# --- 7. Archived runs validate --------------------------------------------------
if compgen -G "runs/*/" > /dev/null; then
  for d in runs/*/; do
    if ./tools/check_run.sh "$d" > /dev/null 2>&1; then ok "run validates: ${d%/}"; else bad "run fails check_run: ${d%/}"; fi
  done
fi

# --- 8. Digest freshness --------------------------------------------------------
if python3 - <<'PY'
import hashlib, pathlib
root = pathlib.Path(".")
skip_names = {"PACK_DIGEST.txt", "opencode.json", ".DS_Store", "Thumbs.db"}
files = sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts and p.name not in skip_names and not p.name.endswith("~"))
current = {p.as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
digest = {}
for line in open("PACK_DIGEST.txt", encoding="utf-8"):
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    h, _, path = line.partition("  ")
    if not path:
        h, _, path = line.partition(" *")
    path = path[2:] if path.startswith("./") else path
    digest[path.replace("\\", "/")] = h
diff = [p for p in current if digest.get(p) != current[p]] + [p for p in digest if p not in current]
if diff:
    print("stale/missing entries: " + ", ".join(sorted(diff)[:10]))
    raise SystemExit(1)
PY
then ok "PACK_DIGEST.txt is current"; else bad "digest stale — run tools/pack_digest.sh"; fi

# --- 9. Runs index consistency --------------------------------------------------
idx_missing=""
for d in runs/*/; do
  [[ -d "$d" ]] || continue
  name="$(basename "$d")"
  grep -q "$name" runs/INDEX.md || idx_missing="$idx_missing $name"
done
if [[ -z "$idx_missing" ]]; then ok "runs/INDEX.md lists all archived runs"; else bad "runs/INDEX.md missing:${idx_missing}"; fi

# --- 10. Verification Performed in report structures ----------------------------
vp_missing=""
for f in prompts/[0-9][0-9]_*.md; do
  case "$f" in *00_SHARED_AUDIT_RULES.md) continue ;; esac
  grep -q "## Verification Performed" "$f" || vp_missing="$vp_missing $f"
done
if [[ -z "$vp_missing" ]]; then ok "report structures include Verification Performed"; else bad "missing Verification Performed:${vp_missing}"; fi

# --- Result ---------------------------------------------------------------------
echo
if [[ $fail -eq 0 ]]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL ($fail check(s))"
  exit 1
fi
