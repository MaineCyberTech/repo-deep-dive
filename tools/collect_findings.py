#!/usr/bin/env python3
"""Collect findings from a run folder into findings.json (and optionally sync the manifest).

Usage:
  tools/collect_findings.py <run-folder> [--write] [--update-manifest]

Read-only by default (prints a summary). --write emits findings.json into the run
folder; --update-manifest syncs the findings counts in audit_manifest.json.
Findings are enriched with status/owner/target/note from follow_up_register.md
when that register is present.
"""

import argparse
import datetime
import json
import sys

sys.dont_write_bytecode = True

import lib_findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("--write", action="store_true", help="write findings.json into the run folder")
    ap.add_argument("--update-manifest", action="store_true", help="sync findings counts in audit_manifest.json")
    args = ap.parse_args()

    run, findings, dupes = lib_findings.collect_with_dupes(args.run_dir)
    c = lib_findings.counts(findings)
    reports = lib_findings.run_reports(run)
    for fid, reps in sorted(dupes.items()):
        print(f"warning: duplicate finding ID {fid} in: {', '.join(reps)}", file=sys.stderr)

    print(f"run: {run.name}")
    print(f"reports scanned: {len(reports)}")
    print(f"findings: {c['total']} ({', '.join(f'{k} x{v}' for k, v in c['bySeverity'].items())})")
    print(f"areas: {', '.join(f'{k} x{v}' for k, v in c['byArea'].items())}")

    by_status = {}
    for f in findings:
        status = f.get("status")
        if status:
            by_status[status] = by_status.get(status, 0) + 1
    if by_status:
        print(f"status: {', '.join(f'{k} x{v}' for k, v in sorted(by_status.items()))}")

    if args.write or args.update_manifest:
        data = {
            "run": run.name,
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sourceReports": len(reports),
            "counts": c,
            "findings": findings,
        }
        if args.write:
            out = run / "findings.json"
            out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"wrote {out}")

    if args.update_manifest:
        man_path = run / "audit_manifest.json"
        if not man_path.exists():
            print("no audit_manifest.json; skipped manifest sync")
            return
        man = json.loads(man_path.read_text(encoding="utf-8"))
        before = man.get("findings", {})
        after = {"bySeverity": c["bySeverity"], "byArea": c["byArea"], "total": c["total"]}
        if before != after:
            man["findings"] = after
            man_path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"updated {man_path.name}: {before} -> {after}")
        else:
            print("manifest counts already current")


if __name__ == "__main__":
    main()
