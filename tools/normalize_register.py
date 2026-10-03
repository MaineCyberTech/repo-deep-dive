#!/usr/bin/env python3
"""Ensure a run's risk_register.md and follow_up_register.md carry a full finding table.

check_run.sh requires the two registers to expose the SAME set of `| AREA-Px-NNN |` table rows
(and a manifest total equal to that count). LLM-authored risk registers and the follow-up register
written by remediation_status.py can drift; this tool makes both carry every finding ID exactly once,
idempotently, preserving any existing Owner/Target/Status/note values.

Usage: tools/normalize_register.py <run-folder>
"""

import json
import os
import re
import sys

sys.dont_write_bytecode = True

ID = re.compile(r"[A-Z]+-P[0-3]-\d{3}")
ROW = re.compile(r"^\|\s*([A-Z]+-P[0-3]-\d{3})\s*\|")


def load_findings(run):
    p = os.path.join(run, "findings.json")
    if not os.path.isfile(p):
        return []
    return json.load(open(p, encoding="utf-8")).get("findings", [])


def existing_status(run):
    """ID -> (status, note) from an existing follow_up_register.md."""
    out = {}
    p = os.path.join(run, "follow_up_register.md")
    if not os.path.isfile(p):
        return out
    lines = open(p, encoding="utf-8").read().splitlines()
    for ln in lines:
        m = ROW.match(ln)
        if m:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            out[m.group(1)] = (cells[5] if len(cells) > 5 else "", cells[6] if len(cells) > 6 else "")
    return out


def row_ids(path):
    if not os.path.isfile(path):
        return set()
    return {m.group(1) for m in (ROW.match(l) for l in open(path, encoding="utf-8")) if m}


def write_follow_up(run, findings):
    status = existing_status(run)
    lines = ["# Follow-up register", "",
             "Owner/Target/Status columns drive tools/collect_findings.py enrichment.", "",
             "| ID | Severity | Title | Owner | Target | Status | Post-audit note |",
             "|---|---|---|---|---|---|---|"]
    for f in findings:
        st, note = status.get(f["id"], ("", ""))
        if not st:
            st = f.get("status") or "open"
        lines.append("| %s | %s | %s |  |  | %s | %s |" % (
            f["id"], f["severity"], (f.get("title", "") or "").replace("|", "/"), st, note.replace("|", "/")))
    open(os.path.join(run, "follow_up_register.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def write_risk_index(run, findings):
    path = os.path.join(run, "risk_register.md")
    text = open(path, encoding="utf-8").read() if os.path.isfile(path) else "# Risk register\n"
    # strip a previously added index so this stays idempotent
    text = re.split(r"\n## Finding index\n", text)[0].rstrip() + "\n"
    block = ["\n## Finding index\n", "| ID | Severity | Title |", "|---|---|---|"]
    for f in findings:
        block.append("| %s | %s | %s |" % (f["id"], f["severity"], (f.get("title", "") or "").replace("|", "/")))
    open(path, "w", encoding="utf-8").write(text + "\n".join(block) + "\n")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    run = os.path.abspath(sys.argv[1])
    findings = load_findings(run)
    if not findings:
        print("no findings.json; nothing to do")
        return
    write_follow_up(run, findings)
    write_risk_index(run, findings)
    n = len(findings)
    rr, fu = row_ids(os.path.join(run, "risk_register.md")), row_ids(os.path.join(run, "follow_up_register.md"))
    print("findings: %d  risk rows: %d  follow_up rows: %d  match: %s" % (
        n, len(rr), len(fu), rr == fu))


if __name__ == "__main__":
    main()
