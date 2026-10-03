#!/usr/bin/env python3
"""Export a run's findings (plus follow-up fields when present) to CSV for external trackers.

Usage:
  tools/findings_to_csv.py <run-folder> [-o findings.csv]

Read-only. Columns: id,severity,area,title,report,line,owner,target,status,post_audit_note
"""

import argparse
import csv
import pathlib
import re
import sys

sys.dont_write_bytecode = True

import lib_findings

COLUMNS = ["id", "severity", "area", "title", "report", "line",
           "owner", "target", "status", "post_audit_note"]


def followup_fields(run_dir):
    """id -> dict(owner, target, status, post_audit_note) from follow_up_register.md."""
    path = pathlib.Path(run_dir) / "follow_up_register.md"
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    header, idx = None, {}
    for line in lines:
        if line.startswith("|") and "Status" in line:
            header = [c.strip() for c in line.strip("|").split("|")]
            idx = {name: header.index(name) for name in header if name}
            break
    if not header:
        return {}
    out = {}
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or not re.fullmatch(r'[A-Z]+-P[0-3]-\d{3}', cells[0] or ""):
            continue
        out[cells[0]] = {
            "owner": cells[idx["Owner"]] if "Owner" in idx and len(cells) > idx["Owner"] else "",
            "target": cells[idx["Target"]] if "Target" in idx and len(cells) > idx["Target"] else "",
            "status": cells[idx["Status"]] if "Status" in idx and len(cells) > idx["Status"] else "",
            "post_audit_note": cells[idx["Post-audit note"]] if "Post-audit note" in idx and len(cells) > idx["Post-audit note"] else "",
        }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("-o", "--output", help="write CSV to this file instead of stdout")
    args = ap.parse_args()

    run, findings = lib_findings.collect(args.run_dir)
    fu = followup_fields(run)

    rows = []
    for f in findings:
        row = {
            "id": f["id"],
            "severity": f["severity"],
            "area": f["id"].split("-")[0],
            "title": f["title"],
            "report": f["report"],
            "line": f["line"],
            "owner": fu.get(f["id"], {}).get("owner", ""),
            "target": fu.get(f["id"], {}).get("target", ""),
            "status": fu.get(f["id"], {}).get("status", ""),
            "post_audit_note": fu.get(f["id"], {}).get("post_audit_note", ""),
        }
        rows.append(row)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {args.output} ({len(rows)} rows)")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
