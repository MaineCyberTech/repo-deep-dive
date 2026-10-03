#!/usr/bin/env python3
"""Org-wide remediation status board across repo-deep-dive runs (read-only).

Scans run folders, joins the audit findings, the follow-up register (status), the
remediation plan (patch sets), and any PR/commit evidence, then prints a Markdown
board (and optional JSON).

Usage:
  tools/remediation_report.py <run-dir> [<run-dir> ...]
  tools/remediation_report.py --runs-dir runs/            # all runs under a directory
  tools/remediation_report.py --runs-dir runs/ --out REMEDIATION_REPORT.md --json report.json

A "run" is any directory containing audit_manifest.json (or findings.json).
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_findings  # noqa: E402

PR_RE = re.compile(r"https://github\.com/[^\s)|>`]+/pull/\d+")
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
SEVS = ("P0", "P1", "P2", "P3")
STATUS_ORDER = ("open", "partially-fixed", "verified-fixed", "still-open",
                "regressed", "owner-accepted")


def repo_from_name(name):
    m = re.match(r"^(.*?)-\d{8}-\d{4}-", name)
    return m.group(1) if m else name


def repo_label(run, manifest):
    """Best-effort repo name: manifest field (basename'd), parent dir, then run name."""
    cand = manifest.get("repo") or manifest.get("repository") or ""
    if cand:
        base = os.path.basename(str(cand).rstrip("/\\"))
        if base:
            return base
    parent = run.parent.name
    if parent and parent not in ("runs", "audits") and not re.match(r"^\d{8}-\d{4}-", parent):
        return parent
    return repo_from_name(run.name)


def load_json(path, default):
    if os.path.isfile(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return default
    return default


def is_run(path):
    return os.path.isfile(os.path.join(path, "audit_manifest.json")) or \
        os.path.isfile(os.path.join(path, "findings.json"))


def collect_run(run_dir):
    run = Path(run_dir)
    manifest = load_json(str(run / "audit_manifest.json"), {})
    _rp, findings, _dupes = lib_findings.collect_with_dupes(str(run))
    sev = {s: 0 for s in SEVS}
    status = {}
    for f in findings:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
        st = (f.get("status") or "open").strip().lower() or "open"
        status[st] = status.get(st, 0) + 1

    plan = load_json(str(run / "remediation_plan.json"), {})
    patch_sets = plan.get("patchSets", []) if isinstance(plan, dict) else []

    text = ""
    for p in ("follow_up_register.md", "verification_log.md"):
        fp = run / p
        if fp.exists():
            text += fp.read_text(encoding="utf-8", errors="replace")
    prs = sorted(set(PR_RE.findall(text)))

    return {
        "run": manifest.get("run") or run.name,
        "name": run.name,
        "repo": repo_label(run, manifest),
        "findings": {"total": len(findings), "bySeverity": sev},
        "status": status,
        "patchSets": [{"id": p.get("id"), "severity": p.get("severity"),
                       "findings": p.get("findings", [])} for p in patch_sets],
        "prs": prs,
    }


def build_markdown(rows):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["# Org remediation board", "",
             "Generated: %s" % now, "",
             "| Repo | Run | Findings | P0 | P1 | P2 | P3 | Patch sets | partially-fixed | verified-fixed | PRs |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    tot = {"total": 0, "P0": 0, "P1": 0, "P2": 0, "P3": 0}
    tpart = tver = 0
    for r in sorted(rows, key=lambda x: (x["repo"], x["run"])):
        sev = r["findings"]["bySeverity"]
        part = r["status"].get("partially-fixed", 0)
        ver = r["status"].get("verified-fixed", 0)
        tpart += part
        tver += ver
        tot["total"] += r["findings"]["total"]
        for s in SEVS:
            tot[s] += sev.get(s, 0)
        lines.append("| %s | %s | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            r["repo"], r["run"], r["findings"]["total"],
            sev.get("P0", 0), sev.get("P1", 0), sev.get("P2", 0), sev.get("P3", 0),
            len(r["patchSets"]), part, ver, len(r["prs"])))
    lines.append("| **TOTAL** | | **%d** | **%d** | **%d** | **%d** | **%d** | | **%d** | **%d** | |" % (
        tot["total"], tot["P0"], tot["P1"], tot["P2"], tot["P3"], tpart, tver))
    lines += ["", "## Open remediation PRs", ""]
    any_pr = False
    for r in sorted(rows, key=lambda x: x["repo"]):
        if r["prs"]:
            any_pr = True
            lines.append("- **%s** (%s): %s" % (r["repo"], r["run"], ", ".join(r["prs"])))
    if not any_pr:
        lines.append("_none recorded_")
    lines += ["", "## Status legend", "",
              "open = not started; partially-fixed = draft PR open; "
              "verified-fixed = merged with a commit; still-open = closed unmerged.", "",
              "*Generated by repo-deep-dive tools/remediation_report.py*"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="*", help="run folders")
    ap.add_argument("--runs-dir", default=None, help="directory containing run folders")
    ap.add_argument("--out", default=None, help="write the Markdown board here")
    ap.add_argument("--json", dest="json_path", default=None, help="write JSON here")
    args = ap.parse_args()

    run_dirs = list(args.runs)
    if args.runs_dir:
        for root, dirs, _files in os.walk(args.runs_dir):
            dirs[:] = [d for d in dirs if d != ".git"]
            if is_run(root):
                run_dirs.append(root)
                dirs[:] = []  # don't descend into a run
    if not run_dirs:
        print("error: no run folders given (use positional paths or --runs-dir)", file=sys.stderr)
        return 2

    rows = [collect_run(d) for d in run_dirs]
    md = build_markdown(rows)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(md)
        print("wrote %s (%d run(s))" % (args.out, len(rows)))
    else:
        sys.stdout.write(md)
    if args.json_path:
        open(args.json_path, "w", encoding="utf-8").write(json.dumps(rows, indent=2) + "\n")
        print("wrote %s" % args.json_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
