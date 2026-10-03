#!/usr/bin/env bash
set -uo pipefail
REPO=/mnt/c/temp/repo-deep-dive-rem
cd "$REPO"
RUN=runs/repo-deep-dive-20261003-0018-main-7bac320

echo
echo "===== FINDING-SPECIFIC BINDING CHECKS ====="
echo
echo "--- INV-P1-001: inventory and manifest bind to the audited commit ---"
python3 - "$RUN" <<'PY'
import json, sys
run = sys.argv[1]
inv = json.load(open(run + "/inventory.json"))
man = json.load(open(run + "/audit_manifest.json"))
repo = man["scope"]["repos"][0]
assert inv["git"]["sha"] == "6cada03", inv["git"]["sha"]
assert inv["git"]["branch"] == "main", inv["git"]["branch"]
assert repo["sha"] == "6cada03", repo["sha"]
assert repo["recordedSha"] == "7bac320", repo["recordedSha"]
print("inventory.git.sha=%s manifest.sha=%s manifest.recordedSha=%s -> OK"
      % (inv["git"]["sha"], repo["sha"], repo["recordedSha"]))
PY
echo "[exit=$?]"
echo
echo "--- INV-P2-002: inventory now sees the org workflow ---"
python3 - "$RUN" <<'PY'
import json, sys
inv = json.load(open(sys.argv[1] + "/inventory.json"))
assert inv["workflows"] == [".github/workflows/deep-dive-deterministic.yml"], inv["workflows"]
assert inv["ci"] == ["github-actions"], inv["ci"]
assert inv["stacks"] == ["github-actions"], inv["stacks"]
assert inv["totals"]["by_ext"][".py"] == 11, inv["totals"]["by_ext"]
print("workflows=%s ci=%s py=%d -> OK"
      % (inv["workflows"], inv["ci"], inv["totals"]["by_ext"][".py"]))
PY
echo "[exit=$?]"
echo
echo "--- INV-P3-003: environment-local pin is no longer tracked ---"
if git ls-files --error-unmatch opencode.json >/dev/null 2>&1; then
  echo "FAIL: opencode.json is still tracked"
  echo "[exit=1]"
else
  echo "PASS: opencode.json is not in git ls-files"
  echo "[exit=0]"
fi
echo
echo "--- digest completeness vs tracked tree ---"
python3 - <<'PY'
import hashlib, pathlib, subprocess
tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                             check=True).stdout.split())
digest = {}
for line in open("PACK_DIGEST.txt", encoding="utf-8"):
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    h, _, p = line.partition("  ")
    digest[p[2:] if p.startswith("./") else p] = h
skip = {"PACK_DIGEST.txt"}
missing = sorted(t for t in tracked if t not in digest and t not in skip)
extra = sorted(d for d in digest if d not in tracked)
print("tracked=%d digest=%d missing_from_digest=%s extra_in_digest=%s"
      % (len(tracked), len(digest), missing, extra))
assert not missing and not extra, (missing, extra)
print("digest is a complete manifest of tracked files (excluding PACK_DIGEST.txt) -> OK")
PY
echo "[exit=$?]"
