#!/usr/bin/env bash
# PS-006 verification (ARCH-P2-001 single-source execution-order lint,
# ARCH-P2-002 strict check_run gate). Read-only except the throwaway
# negative-test copy under /tmp. Writes real output + exit codes to
# remediation/PS-006/verify.log via the caller's redirection.
set -u
REPO=/mnt/c/temp/repo-deep-dive-rem
RUN_REL=runs/repo-deep-dive-20261003-0018-main-7bac320
cd "$REPO" || exit 99

hdr() { printf '\n===== %s =====\n' "$1"; }

hdr "1. bash tools/self_test.sh"
bash tools/self_test.sh
echo "EXIT=$?"

hdr "2. bash tools/lint_pack.sh"
bash tools/lint_pack.sh
echo "EXIT=$?"

hdr "3. ARCH-P2-002: run_toolchain.py without bash (expect exit 2, FAILED)"
env PATH=/nonexistent /usr/bin/python3 tools/run_toolchain.py "$RUN_REL"
echo "EXIT=$?"

hdr "4. ARCH-P2-002: run_toolchain.py without bash + --no-check (expect exit 0, TOOLCHAIN: PASS)"
env PATH=/nonexistent /usr/bin/python3 tools/run_toolchain.py "$RUN_REL" --no-check
echo "EXIT=$?"

hdr "5. ARCH-P2-002: run_toolchain.py with bash available (expect exit 0)"
python3 tools/run_toolchain.py "$RUN_REL"
echo "EXIT=$?"

hdr "6. ARCH-P2-001 negative test: perturbed executionOrder must FAIL the lint"
rm -rf /tmp/ps006-neg
cp -a "$REPO" /tmp/ps006-neg
python3 - <<'PY'
import json
p = "/tmp/ps006-neg/examples/audit_manifest.example.json"
d = json.load(open(p, encoding="utf-8-sig"))
d["executionOrder"] = [x for x in d["executionOrder"]
                       if not x.startswith("21_")]  # drop one prompt
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
PY
( cd /tmp/ps006-neg && bash tools/pack_digest.sh >/dev/null && bash tools/lint_pack.sh )
echo "EXIT=$?"
rm -rf /tmp/ps006-neg
