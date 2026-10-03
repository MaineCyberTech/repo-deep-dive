#!/usr/bin/env python3
"""One-command machine chain for a repo-deep-dive run (Wave 4 + verify).

Runs, in order: run validation (check_run.sh when bash exists),
findings normalization (collect_findings.py), advisory scoring
(risk_score.py), dashboard rendering (render_dashboard.py), run-to-run
delta (diff_runs.py), and CSV export (findings_to_csv.py).

Usage:
  python3 tools/run_toolchain.py <run-folder> [--write] [--dashboard]
      [--diff <old-run-folder>] [--no-check] [--strict]

Read-only by default (every step prints a summary; CSV goes to a temp
file). --write lets each step emit its artifacts into the run folder.
--dashboard also renders dashboard.md/html + pr_comment.md (with --write).
--diff compares against an older run. --no-check skips check_run.sh.
--strict turns a skipped check (no bash) into a failure.
Fails fast: the first failing step aborts the chain. ASCII-only output.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

PACK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS = os.path.join(PACK_ROOT, "tools")


def step(label, cmd, strict=True):
    print("== %s ==" % label)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print("FAILED: %s (exit %d)" % (label, r.returncode), file=sys.stderr)
        if strict:
            raise SystemExit(r.returncode)
        print("continuing (--no-check/soft mode)")
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir", help="run folder to process")
    ap.add_argument("--write", action="store_true",
                    help="emit artifacts into the run folder")
    ap.add_argument("--dashboard", action="store_true",
                    help="also render dashboard artifacts (needs --write to save)")
    ap.add_argument("--diff", default=None, metavar="OLD_RUN",
                    help="record the delta against an older run folder")
    ap.add_argument("--no-check", action="store_true",
                    help="skip check_run.sh validation")
    ap.add_argument("--strict", action="store_true",
                    help="fail when the check step must be skipped (no bash)")
    args = ap.parse_args()

    py = sys.executable
    write = ["--write"] if args.write else []
    ok = True

    if not args.no_check:
        bash = shutil.which("bash")
        if bash:
            ok = step("check_run.sh",
                      [bash, os.path.join(TOOLS, "check_run.sh"), args.run_dir]) and ok
        elif args.strict:
            print("FAILED: check requested but no bash found (--strict)",
                  file=sys.stderr)
            raise SystemExit(2)
        else:
            print("== check_run.sh ==")
            print("skipped: no bash on PATH (use --strict to fail, --no-check to silence)")

    ok = step("collect_findings.py",
              [py, os.path.join(TOOLS, "collect_findings.py"), args.run_dir] + write) and ok
    ok = step("risk_score.py",
              [py, os.path.join(TOOLS, "risk_score.py"), args.run_dir] + write) and ok
    if args.dashboard:
        ok = step("render_dashboard.py",
                  [py, os.path.join(TOOLS, "render_dashboard.py"), args.run_dir] + write) and ok
    if args.diff:
        ok = step("diff_runs.py",
                  [py, os.path.join(TOOLS, "diff_runs.py"), args.diff, args.run_dir]) and ok

    tmp_csv = os.path.join(tempfile.gettempdir(), "toolchain_findings.csv")
    ok = step("findings_to_csv.py",
              [py, os.path.join(TOOLS, "findings_to_csv.py"),
               args.run_dir, "-o", tmp_csv]) and ok
    if ok:
        print("csv rows at %s" % tmp_csv)
        print("TOOLCHAIN: PASS")

    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
