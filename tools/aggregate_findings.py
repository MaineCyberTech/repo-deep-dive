#!/usr/bin/env python3
"""Aggregate per-repo deterministic-findings.json into an org-wide rollup.

Usage:
  tools/aggregate_findings.py <indir> [-o ORG_SUMMARY.md] [--json ORG.json]

<indir> contains one subdirectory per repo, each with deterministic-findings.json.
"""

import argparse
import datetime
import json
import os
import sys

sys.dont_write_bytecode = True

SEV = ("P0", "P1", "P2", "P3")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("indir", help="directory of per-repo output folders")
    ap.add_argument("-o", "--out", default="ORG_SUMMARY.md")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    repos = []
    for d in sorted(os.listdir(args.indir)):
        p = os.path.join(args.indir, d, "deterministic-findings.json")
        if os.path.isfile(p):
            try:
                repos.append(json.load(open(p, encoding="utf-8")))
            except Exception as e:
                print("skip %s: %s" % (d, e), file=sys.stderr)

    sev = {}
    for r in repos:
        for k, v in r.get("counts", {}).get("bySeverity", {}).items():
            sev[k] = sev.get(k, 0) + v
    total = sum(r.get("counts", {}).get("total", 0) for r in repos)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = ["# Deep-dive deterministic checks - org rollup", "",
             "Generated: %s" % now, "",
             "Repos: %d &middot; Findings: %d &middot; %s" % (
                 len(repos), total,
                 ", ".join("%s x%d" % (k, sev[k]) for k in SEV if k in sev) or "none"),
             "",
             "| Repo | P0 | P1 | P2 | P3 | Total |", "|---|---:|---:|---:|---:|---:|"]
    for r in repos:
        s = r.get("counts", {}).get("bySeverity", {})
        lines.append("| %s | %d | %d | %d | %d | %d |" % (
            r.get("run", "?"), s.get("P0", 0), s.get("P1", 0), s.get("P2", 0),
            s.get("P3", 0), r.get("counts", {}).get("total", 0)))
    lines += ["", "## Findings by repo", ""]
    for r in repos:
        lines.append("### %s" % r.get("run", "?"))
        lines.append("")
        fs = r.get("findings", [])
        if not fs:
            lines.append("_No findings._")
        for f in fs:
            lines.append("- **%s** (%s) %s" % (f["id"], f["severity"], f["title"]))
        lines.append("")

    open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    if args.json:
        open(args.json, "w", encoding="utf-8").write(
            json.dumps({"generated": now, "repos": repos}, indent=2) + "\n")

    print("repos=%d findings=%d -> %s" % (len(repos), total, args.out))


if __name__ == "__main__":
    main()
