#!/usr/bin/env python3
"""Reconcile remediation PR outcomes into a run's follow-up register.

Updates `<run>/follow_up_register.md` (Owner/Target/Status/Post-audit note columns) and
appends `<run>/verification_log.md`, without rewriting any original finding report.

Usage:
  tools/remediation_status.py <run-folder> --patch-set PS-01 --state merged \
      --commit <sha> [--pr <url>] [--note "..."]
  tools/remediation_status.py <run-folder> --status-file status.json

status.json: [{ "patchSet": "PS-01", "state": "merged|open|closed", "commit": "...", "pr": "...", "note": "..." }, ...]

States map to findings: merged -> verified-fixed; open/ready -> partially-fixed;
closed (unmerged) -> still-open. A finding only becomes verified-fixed with a commit.
"""

import argparse
import datetime
import json
import os
import re
import sys

sys.dont_write_bytecode = True

STATE_TO_STATUS = {
    "merged": "verified-fixed",
    "open": "partially-fixed",
    "draft": "partially-fixed",
    "ready": "partially-fixed",
    "closed": "still-open",
    "regressed": "regressed",
}
HEADER = "| ID | Severity | Title | Owner | Target | Status | Post-audit note |\n"
SEP = "|---|---|---|---|---|---|---|\n"


def load_json(path, default):
    if os.path.isfile(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return default
    return default


def ensure_register(run):
    path = os.path.join(run, "follow_up_register.md")
    if os.path.isfile(path):
        return path
    findings = load_json(os.path.join(run, "findings.json"), {}).get("findings", [])
    lines = ["# Follow-up register", "",
             "Auto-created by tools/remediation_status.py. Owner/Target/Status columns drive "
             "tools/collect_findings.py enrichment.", "",
             HEADER.rstrip("\n"), SEP.rstrip("\n")]
    for f in findings:
        lines.append("| %s | %s | %s |  |  | %s |  |" % (
            f["id"], f["severity"], f.get("title", "").replace("|", "/"), f.get("status") or "open"))
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return path


def update_register(path, statuses, note):
    rows = open(path, encoding="utf-8").read().splitlines(keepends=True)
    out, col = [], None
    for ln in rows:
        if ln.startswith("|") and "Status" in ln and "Owner" in ln:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            col = {c: i for i, c in enumerate(cells)}
            out.append(ln)
            continue
        if ln.startswith("|") and col:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            fid = cells[0] if cells else ""
            if fid in statuses:
                st, extra = statuses[fid]
                while len(cells) < len(col):
                    cells.append("")
                cells[col["Status"]] = st
                if col.get("Post-audit note") is not None:
                    cells[col["Post-audit note"]] = (extra or note or cells[col["Post-audit note"]]).replace("|", "/")
                out.append("| " + " | ".join(cells) + " |\n")
                continue
        out.append(ln)
    open(path, "w", encoding="utf-8").write("".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("--patch-set", default=None)
    ap.add_argument("--state", default=None)
    ap.add_argument("--commit", default="")
    ap.add_argument("--pr", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--status-file", default=None)
    args = ap.parse_args()

    run = os.path.abspath(args.run_dir)
    if not os.path.isdir(run):
        print("error: not a directory: %s" % run, file=sys.stderr)
        raise SystemExit(2)

    updates = []
    if args.status_file:
        updates = json.load(open(args.status_file, encoding="utf-8"))
    elif args.patch_set and args.state:
        updates = [{"patchSet": args.patch_set, "state": args.state,
                    "commit": args.commit, "pr": args.pr, "note": args.note}]
    else:
        ap.error("provide --status-file or --patch-set with --state")
        return

    plan = load_json(os.path.join(run, "remediation_plan.json"), {})
    ps_map = {p["id"]: p for p in plan.get("patchSets", [])}

    register = ensure_register(run)
    statuses = {}
    log = []
    for u in updates:
        ps = u.get("patchSet", "")
        st = STATE_TO_STATUS.get((u.get("state") or "").lower(), "partially-fixed")
        findings = ps_map.get(ps, {}).get("findings", [])
        ev = " ".join(x for x in (u.get("commit") or "", u.get("pr") or "") if x)
        for fid in findings:
            statuses[fid] = (st, ("remediation %s %s %s" % (ps, u.get("state"), ev)).strip())
        log.append("| %s | %s | %s | %s | %s | %s |" % (
            datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ps, u.get("state"), st, ev, (u.get("note") or "").replace("|", "/")))

    if statuses:
        update_register(register, statuses, args.note)
    vlog = os.path.join(run, "verification_log.md")
    new = not os.path.isfile(vlog)
    with open(vlog, "a", encoding="utf-8") as fh:
        if new:
            fh.write("# Verification log\n\n| When | Patch set | State | Finding status | Evidence | Note |\n")
            fh.write("|---|---|---|---|---|---|\n")
        fh.write("\n".join(log) + ("\n" if log else ""))

    print("run: %s" % os.path.basename(run))
    print("updated %d finding(s) across %d patch set(s)" % (len(statuses), len(updates)))
    for fid, (st, ev) in sorted(statuses.items()):
        print("  %s -> %s (%s)" % (fid, st, ev or "-"))
    print("register: %s" % register)
    print("log: %s" % vlog)


if __name__ == "__main__":
    main()
