#!/usr/bin/env python3
"""Consolidated remediation review index across repo-deep-dive runs (read-only).

Joins each run's remediation_plan.json (patch sets -> findings/severity) with the
follow-up register (status + PR evidence) and the verification log, then emits a
Markdown index a human reviewer can work through: repo -> patch set -> draft PR ->
findings -> severity -> status -> verification.

Usage:
  tools/review_index.py --runs-dir <dir> [--out REVIEW_INDEX.md] [--json out.json]

A run is any directory containing audit_manifest.json (or findings.json).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_findings  # noqa: E402

PR_RE = re.compile(r"https://github\.com/[^\s)|>`]+/pull/\d+")
FINDING_RE = re.compile(r"\b[A-Z]+-P[0-3]-\d{3}\b")
SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "": 9}
SEV_CLS = {"P0": "**P0**", "P1": "**P1**", "P2": "P2", "P3": "P3"}


def load_pr_map(path):
    """{repo: [(url, title)]} from a JSON list of {repo,url,title}."""
    data = load_json(path, [])
    out = {}
    for pr in data:
        out.setdefault(pr.get("repo", ""), []).append(
            (pr.get("url", ""), pr.get("title", "")))
    return out


def prs_for(repo, findings, prmap, pid=""):
    """PRs whose title names any finding, or the patch-set id (fallback)."""
    urls = []
    pidre = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(pid) + r"(?![0-9])") if pid else None
    for url, title in prmap.get(repo, []):
        if any(f in title for f in findings) or (pidre and pidre.search(title)):
            urls.append(url)
    return sorted(set(urls))


def load_json(path, default):
    if os.path.isfile(path):
        try:
            return json.load(open(path, encoding="utf-8-sig"))
        except Exception:
            return default
    return default


def is_run(path):
    return os.path.isfile(os.path.join(path, "audit_manifest.json")) or \
        os.path.isfile(os.path.join(path, "findings.json"))


def repo_label(run, manifest):
    cand = manifest.get("repo") or manifest.get("repository") or ""
    if cand:
        base = os.path.basename(str(cand).rstrip("/\\"))
        if base:
            return base
    parent = run.parent.name
    if parent and parent not in ("runs", "audits") and not re.match(r"^\d{8}-\d{4}-", parent):
        return parent
    m = re.match(r"^(.*?)-\d{8}-\d{4}-", run.name)
    return m.group(1) if m else run.name


def parse_verification_log(run):
    """{patch_set: [evidence strings]} from verification_log.md."""
    out = {}
    p = run / "verification_log.md"
    if not p.exists():
        return out
    idx = None
    for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if "Patch set" in cells:
            idx = {c: i for i, c in enumerate(cells)}
            continue
        if idx and len(cells) > idx.get("Evidence", -1):
            ps = cells[idx["Patch set"]] if "Patch set" in idx else ""
            ev = cells[idx["Evidence"]] if "Evidence" in idx else ""
            if ps:
                out.setdefault(ps, []).append(ev)
    return out


def collect_run(run, prmap=None):
    prmap = prmap or {}
    manifest = load_json(str(run / "audit_manifest.json"), {})
    repo = repo_label(run, manifest)
    plan = load_json(str(run / "remediation_plan.json"), {})
    reg = lib_findings.register_fields(str(run))
    vlog = parse_verification_log(run)

    patch_sets = []
    for ps in plan.get("patchSets", []):
        fs = ps.get("findings", [])
        statuses = {f: (reg.get(f, {}).get("status") or "open") for f in fs}
        prs = []
        notes = []
        for f in fs:
            note = reg.get(f, {}).get("note", "")
            if note:
                notes.append(note)
            prs += PR_RE.findall(note)
        for ev in vlog.get(ps.get("id"), []):
            prs += PR_RE.findall(ev)
        prs = sorted(set(prs))
        if not prs:
            prs = prs_for(repo, fs, prmap, ps.get("id", ""))
        sev = ps.get("severity") or ""
        if not sev and fs:
            sev = min((f.split("-")[1] for f in fs), key=lambda s: SEV_ORDER.get(s, 9))
        patch_sets.append({
            "id": ps.get("id"),
            "title": ps.get("title", ""),
            "severity": sev,
            "findings": fs,
            "statuses": statuses,
            "files": ps.get("files", []),
            "prs": prs,
            "evidence": vlog.get(ps.get("id"), []),
        })
    patch_sets.sort(key=lambda p: (SEV_ORDER.get(p["severity"], 9), p["id"] or ""))

    return {
        "run": manifest.get("run") or run.name,
        "repo": repo,
        "patchSets": patch_sets,
    }


def build_markdown(rows):
    lines = ["# Remediation review index", "",
             "Draft PRs only - a human reviewer must review and merge; none are auto-merged or "
             "self-approved. Findings move to `verified-fixed` only after a merge with a commit.",
             ""]
    # global P0/P1 first
    hot = []
    for r in rows:
        for p in r["patchSets"]:
            if p["severity"] in ("P0", "P1"):
                for f in p["findings"]:
                    sev = f.split("-")[1]
                    if sev in ("P0", "P1"):
                        hot.append((SEV_ORDER[sev], r["repo"], f, p["id"], p["prs"], p["statuses"].get(f)))
    hot.sort()
    lines += ["## Review P0/P1 first", ""]
    if hot:
        lines += ["| Sev | Repo | Finding | Patch set | PR | Status |", "|---|---|---|---|---|---|"]
        for _o, repo, f, pid, prs, st in hot:
            sev = f.split("-")[1]
            pr = prs[0] if prs else "-"
            lines.append("| %s | %s | %s | %s | %s | %s |" % (
                SEV_CLS.get(sev, sev), repo, f, pid, pr, st or "open"))
    else:
        lines.append("_No P0/P1 patch sets._")

    lines += ["", "## By repository", ""]
    for r in sorted(rows, key=lambda x: x["repo"]):
        allf = set()
        counts = {}
        for p in r["patchSets"]:
            for f in p["findings"]:
                allf.add(f)
                s = f.split("-")[1]
                counts[s] = counts.get(s, 0) + 1
        lines.append("### %s" % r["repo"])
        lines.append("")
        lines.append("Findings: %d (P0 %d | P1 %d | P2 %d | P3 %d)" % (
            len(allf), counts.get("P0", 0), counts.get("P1", 0),
            counts.get("P2", 0), counts.get("P3", 0)))
        lines.append("")
        lines.append("| PR | Patch set | Sev | Findings | Status |")
        lines.append("|---|---|---|---|---|")
        for p in r["patchSets"]:
            pr = ", ".join(p["prs"]) if p["prs"] else "-"
            stset = sorted(set(p["statuses"].values()))
            st = ", ".join(stset) if stset else "open"
            findings = ", ".join(p["findings"]) if p["findings"] else p["title"]
            if len(findings) > 90:
                findings = findings[:87] + "…"
            lines.append("| %s | %s | %s | %s | %s |" % (
                pr, p["id"], SEV_CLS.get(p["severity"], p["severity"] or "—"),
                findings, st))
        lines.append("")
    lines += ["---", "*Generated by repo-deep-dive tools/review_index.py*"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", dest="json_path", default=None)
    ap.add_argument("--prs-json", dest="prs_json", default=None,
                    help="JSON list of {repo,url,title} used to fill PR links missing from the registers")
    args = ap.parse_args()

    prmap = load_pr_map(args.prs_json) if args.prs_json else {}
    run_dirs = []
    for root, dirs, _ in os.walk(args.runs_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        if is_run(root) and os.path.isfile(os.path.join(root, "remediation_plan.json")):
            run_dirs.append(Path(root))
            dirs[:] = []
    if not run_dirs:
        print("error: no runs under %s" % args.runs_dir, file=sys.stderr)
        return 2

    rows = [collect_run(d, prmap) for d in run_dirs]
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
