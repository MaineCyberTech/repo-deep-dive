#!/usr/bin/env python3
"""Compare two repo-deep-dive runs: new / missing / severity / title / status changes.

Usage:
  tools/diff_runs.py <old-run> <new-run> [-o output.md]

Read-only. Prints a markdown delta report; -o also writes it to a file.
"""

import argparse
import pathlib
import re
import sys

sys.dont_write_bytecode = True

import lib_findings


def statuses(run_dir):
    """Extract finding -> status from follow_up_register.md (column named Status)."""
    path = pathlib.Path(run_dir) / "follow_up_register.md"
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = None
    for line in lines:
        if line.startswith("|") and "Status" in line:
            header = [c.strip() for c in line.strip("|").split("|")]
            if "Status" in header:
                idx = header.index("Status")
            break
    if idx is None:
        return {}
    out = {}
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) > idx and re.fullmatch(r'[A-Z]+-P[0-3]-\d{3}', cells[0] or ""):
            out[cells[0]] = cells[idx]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("old_run")
    ap.add_argument("new_run")
    ap.add_argument("-o", "--output", help="also write the delta report to this file")
    args = ap.parse_args()

    old_dir, old = lib_findings.collect(args.old_run)
    new_dir, new = lib_findings.collect(args.new_run)
    om = {f["id"]: f for f in old}
    nm = {f["id"]: f for f in new}
    os_, ns = statuses(old_dir), statuses(new_dir)

    added = sorted(set(nm) - set(om))
    missing = sorted(set(om) - set(nm))
    common = sorted(set(om) & set(nm))
    sev_changed = [i for i in common if om[i]["severity"] != nm[i]["severity"]]
    title_changed = [i for i in common if om[i]["title"] != nm[i]["title"]]
    status_changed = [i for i in sorted(set(os_) | set(ns))
                      if os_.get(i) != ns.get(i) and i in set(om) | set(nm)]

    L = []
    L.append(f"# Run Delta: {old_dir.name} -> {new_dir.name}")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append(f"- Findings: {len(om)} -> {len(nm)}")
    L.append(f"- New: {len(added)}")
    L.append(f"- Missing (present in old, not in new - closed, renamed, or dropped): {len(missing)}")
    L.append(f"- Severity changes: {len(sev_changed)}")
    L.append(f"- Title changes: {len(title_changed)}")
    L.append(f"- Status changes: {len(status_changed)}")
    L.append("")

    def table(title, rows, cols, fmt):
        L.append(f"## {title}")
        L.append("")
        if not rows:
            L.append("_None._")
            L.append("")
            return
        L.append("| " + " | ".join(cols) + " |")
        L.append("|" + "---|" * len(cols))
        for r in rows:
            L.append("| " + " | ".join(fmt(r, c) for c in cols) + " |")
        L.append("")

    table("New findings", added, ["ID", "Sev", "Title", "Report"],
          lambda i, c: {"ID": i, "Sev": nm[i]["severity"], "Title": nm[i]["title"], "Report": nm[i]["report"]}[c])
    table("Missing findings", missing, ["ID", "Sev", "Title", "Report"],
          lambda i, c: {"ID": i, "Sev": om[i]["severity"], "Title": om[i]["title"], "Report": om[i]["report"]}[c])
    table("Severity changes", sev_changed, ["ID", "Old", "New"],
          lambda i, c: {"ID": i, "Old": om[i]["severity"], "New": nm[i]["severity"]}[c])
    table("Title changes", title_changed, ["ID", "Old", "New"],
          lambda i, c: {"ID": i, "Old": om[i]["title"], "New": nm[i]["title"]}[c])
    table("Status changes", status_changed, ["ID", "Old", "New"],
          lambda i, c: {"ID": i, "Old": os_.get(i, "-"), "New": ns.get(i, "-")}[c])

    report = "\n".join(L)
    print(report)
    if args.output:
        pathlib.Path(args.output).write_text(report, encoding="utf-8")
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
