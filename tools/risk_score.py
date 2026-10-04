#!/usr/bin/env python3
"""Advisory risk score for a repo-deep-dive run (read-only by default).

Computes a 0-100 readiness score from findings.json (via lib_findings) using
the shared penalty formula, and maps it to an advisory gate suggestion that
uses the same vocabulary as prompt 23 (GO / GO WITH CONDITIONS / NO-GO).

Formula (advisory, portable across repos):
  score = max(0, 100 - (P0*40 + P1*10 + P2*3))   # P3 findings are unpenalized

Mapping (advisory only):
  P0 > 0        -> NO-GO
  score >= 85   -> GO
  otherwise     -> GO WITH CONDITIONS

The score NEVER replaces RELEASE_GATE.md. It is a fast comparator for
dashboards, CI gates, and run-to-run trends.

Usage:
  python3 tools/risk_score.py <run-folder> [--write]

Read-only by default (prints a summary). --write emits risk_score.json into
the run folder. Stdout is ASCII-only (Windows-console safe).
"""

import argparse
import datetime
import json
import sys

sys.dont_write_bytecode = True

import lib_findings

FORMULA = "max(0, 100 - (P0*40 + P1*10 + P2*3)); P3 unpenalized"


def score_counts(by_sev):
    return max(0, 100 - (
        by_sev.get("P0", 0) * 40
        + by_sev.get("P1", 0) * 10
        + by_sev.get("P2", 0) * 3
    ))


def advisory(by_sev, score):
    if by_sev.get("P0", 0) > 0:
        return "NO-GO"
    if score >= 85:
        return "GO"
    return "GO WITH CONDITIONS"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("--write", action="store_true",
                    help="write risk_score.json into the run folder")
    args = ap.parse_args()

    run, findings, dupes = lib_findings.collect_with_dupes(args.run_dir)
    for fid, reps in sorted(dupes.items()):
        print("warning: duplicate finding ID %s in: %s" % (fid, ", ".join(reps)),
              file=sys.stderr)

    c = lib_findings.counts(findings)
    by_sev = c["bySeverity"]
    full = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    full.update(by_sev)
    score = score_counts(full)
    adv = advisory(full, score)

    print("run: %s" % run.name)
    print("findings: %d (P0 x%d, P1 x%d, P2 x%d, P3 x%d)" % (
        c["total"], full["P0"], full["P1"], full["P2"], full["P3"]))
    print("score: %d/100" % score)
    print("advisory: %s (advisory only; see RELEASE_GATE.md)" % adv)

    if args.write:
        payload = {
            "run": run.name,
            "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "formula": FORMULA,
            "counts": {"total": c["total"], "bySeverity": full, "byArea": c["byArea"]},
            "score": score,
            "advisoryDecision": adv,
            "note": "Advisory only. The audit gate in RELEASE_GATE.md is authoritative.",
        }
        out = run / "risk_score.json"
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print("wrote %s" % out)


if __name__ == "__main__":
    main()
