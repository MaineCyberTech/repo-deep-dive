#!/usr/bin/env python3
"""Changed-run severity gate for repo-deep-dive CI (CI-003).

Reads a run's `findings.json` and fails (exit 1) when any finding whose severity is
in GATE_SEVERITIES is still **unresolved**. A finding is resolved when its status is
one of `lib_findings.RESOLVED_STATUSES` (verified-fixed / owner-accepted /
false-positive); every other status (open, still-open, partially-fixed, regressed,
or unset) blocks. This lets a run with historical, now-verified-fixed P0/P1 pass on
future changes without weakening the gate for live findings.

Fail-closed: a missing or unreadable findings.json exits 2 (never silently passes).

Usage:
  python3 tools/run_gate.py <run-folder> [--severities P0,P1] [--json]

Exit: 0 = no unresolved gated findings; 1 = unresolved gated findings; 2 = usage/read error.
"""

import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_findings  # noqa: E402


def parse_severities(value):
    return [s.strip().upper() for s in (value or "").split(",") if s.strip()]


def gate_blockers(findings, severities):
    """Return the findings in `severities` whose status is not resolved."""
    wanted = {s.upper() for s in severities}
    blockers = []
    for f in findings or []:
        if str(f.get("severity", "")).upper() not in wanted:
            continue
        status = str(f.get("status", "") or "").strip().lower()
        if status in lib_findings.RESOLVED_STATUSES:
            continue
        blockers.append(f)
    return blockers


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--severities", default=os.environ.get("GATE_SEVERITIES", "P0,P1"),
                    help="comma-separated severities that block (default: $GATE_SEVERITIES or P0,P1)")
    ap.add_argument("--json", action="store_true", help="emit a JSON report")
    args = ap.parse_args(argv)

    severities = parse_severities(args.severities)
    findings_path = os.path.join(args.run_dir, "findings.json")
    if not os.path.isfile(findings_path):
        print("gate: %s not found; failing closed" % findings_path, file=sys.stderr)
        return 2
    try:
        with open(findings_path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as exc:
        print("gate: cannot read %s: %s; failing closed" % (findings_path, exc), file=sys.stderr)
        return 2

    findings = doc.get("findings")
    if not isinstance(findings, list):
        # Legacy run with only aggregate counts: treat every counted gated finding
        # as unresolved (fail closed) rather than passing on missing detail.
        counts = doc.get("counts", {}).get("bySeverity", {})
        findings = [{"id": "(count)", "severity": s, "status": "open"}
                    for s in severities for _ in range(int(counts.get(s, 0) or 0))]

    blockers = gate_blockers(findings, severities)
    if args.json:
        print(json.dumps({
            "run": doc.get("run") or os.path.basename(os.path.abspath(args.run_dir)),
            "severities": severities,
            "resolved": sorted(lib_findings.RESOLVED_STATUSES),
            "blocking": [{"id": f.get("id"), "severity": f.get("severity"),
                          "status": f.get("status", "")} for f in blockers],
        }, indent=2))

    if blockers:
        detail = ", ".join("%s(%s)=%s" % (f.get("id"), f.get("severity"),
                                          f.get("status") or "unset") for f in blockers)
        print("blocking unresolved findings (%s): %s" % (",".join(severities), detail))
        return 1
    print("severity gate (%s): no unresolved findings" % ",".join(severities))
    return 0


if __name__ == "__main__":
    sys.exit(main())
