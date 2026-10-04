#!/usr/bin/env python3
"""Publish an audit run - the standard post-audit step.

Given a run source (the audit's findings + report), this:
  0. runs a lightweight pre-publish secret scan (fail closed) over every file it
     would write or push; nothing is written or pushed when a likely secret is found.
  1. normalizes everything into a repo-deep-dive run folder that PASSES tools/check_run.sh
     (fixed AREA-Px-NNN finding IDs, registers, finals, manifest, INDEX);
  2. installs it in the pack under runs/<repo>-<run>/ and appends a runs/INDEX.md row
     (the portable copy);
  3. opens/updates a DRAFT PR in the target repo adding the canonical copy at
     docs/audits/repo-deep-dive/<run>/ (never merges, never self-approves).

Run sources accepted:
  --source-dir DIR   a folder with findings.json (required), FINDINGS.md or REPORT.md,
                     and optional lens_deterministic.md / deterministic-findings.json

Usage:
  tools/publish_audit.py --repo chat --branch develop --sha <full-sha> \
      --source-dir C:/temp/deepdive/chat [--run 20261004-0700-develop-0695894] \
      [--no-pack] [--no-pr] [--org MaineCyberTech] [--dry-run]

After a pack install, run: tools/pack_digest.sh && tools/lint_pack.sh, then commit/push.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

ALLOWED_STATUS = {"", "open", "partially-fixed", "verified-fixed", "still-open", "regressed", "owner-accepted"}

# Pre-publish secret scan (repo-deep-dive-SEC-002). Lightweight, dependency-free
# deny-list of high-confidence secret shapes; publication fails closed on a hit
# so a credential pasted into evidence/report is never committed to the pack or
# pushed to a target-repo PR. Values are reported redacted only.
SECRET_RULES = (
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("stripe-key", re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("generic-assigned-secret", re.compile(
        r"(?i)\b(?:password|passwd|pwd|secret|token|api[_-]?key|apikey|"
        r"access[_-]?key|client[_-]?secret|private[_-]?key)\b\s*[:=]\s*"
        r"['\"]?([A-Za-z0-9_\-/+]{16,})")),
)

# Known-safe values (documented placeholders, env references, redactions) and
# explicit false-positive prose. Keep narrow so real keys in a diff still fire.
SECRET_VALUE_ALLOWLIST = re.compile(
    r"(?i)^(?:<[^>]+>|example|placeholder|redacted|changeme|xxx+|abcdef1234567890|"
    r"your[_-]?(?:token|key|secret|password)|not[_-]?a[_-]?secret|"
    r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?)$")
SECRET_LINE_ALLOWLIST = re.compile(
    r"(?i)(?:gitleaks[^\n]*false[ -]?positive|false[ -]?positive|"
    r"not[ -]?a[ -]?secret|redacted|<redacted>)")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _redact(value):
    """Report a matched secret without reproducing it (first 3 chars only)."""
    n = len(value)
    return "***redacted***" if n <= 8 else value[:3] + "***redacted***"


def scan_secrets(files):
    """Return [(name, lineno, rule, redacted), ...] for likely secrets in files.

    `files` maps a filename to its text. Known-safe placeholders and explicit
    false-positive notes are allowed; everything else matches the deny-list.
    """
    hits = []
    for name in sorted(files):
        for lineno, line in enumerate(str(files[name]).splitlines(), 1):
            if SECRET_LINE_ALLOWLIST.search(line):
                continue
            for rule, rx in SECRET_RULES:
                m = rx.search(line)
                if not m:
                    continue
                value = m.group(1) if m.groups() else m.group(0)
                if SECRET_VALUE_ALLOWLIST.match(value):
                    continue
                hits.append((name, lineno, rule, _redact(value)))
                break
    return hits


def area_code(f):
    a = re.sub(r"[^A-Za-z]", "", str(f.get("area", ""))).upper()
    if not a:
        # derive from the finding id prefix if present (e.g. "chat-SEC-001")
        m = re.search(r"-([A-Za-z]{2,})-", str(f.get("id", "")))
        a = m.group(1).upper() if m else "GEN"
    return a


def first_line(f):
    for ev in f.get("evidence") or []:
        m = re.search(r":(\d+)(?:-\d+)?(?:\b|:|\s|$)", str(ev))
        if m:
            try:
                n = int(m.group(1))
                if n >= 1:
                    return n
            except ValueError:
                pass
    return 1


def normalize(items, report_name):
    """Return (findings_for_json, registers) with pack-compatible AREA-Px-NNN IDs."""
    counter = Counter()
    out, regs = [], []
    for f in items:
        sev = str(f.get("severity", "")).upper()
        if sev not in ("P0", "P1", "P2", "P3"):
            sev = "P3"
        area = area_code(f) or "GEN"
        counter[(area, sev)] += 1
        nid = "%s-%s-%03d" % (area, sev, counter[(area, sev)])
        title = str(f.get("title", "")).strip() or "(untitled)"
        rec = {
            "id": nid,
            "severity": sev,
            "title": title,
            "report": report_name,
            "line": first_line(f),
            "area": area,
            "evidence": f.get("evidence") or [],
            "impact": f.get("impact", ""),
            "recommendation": f.get("recommendation", ""),
            "deterministic_ref": f.get("deterministic_ref"),
            "confidence": f.get("confidence", ""),
            "status": "open",
        }
        out.append(rec)
        regs.append(rec)
    return out, regs


def register_md(regs):
    lines = ["# Follow-up register", "",
             "| Finding | Severity | Title | Owner | Target | Status | Note |",
             "|---|---|---|---|---|---|---|"]
    for r in regs:
        lines.append("| %s | %s | %s | @owner | %s | open | %s |" % (
            r["id"], r["severity"], r["title"].replace("|", "\\|"), r["area"],
            (r.get("recommendation", "")[:120].replace("|", "\\|") or "remediation")))
    return "\n".join(lines) + "\n"


def build_files(repo, branch, sha, run, items, source_dir, report_name, report_text):
    short = sha[:7]
    findings, regs = normalize(items, report_name)
    sev = Counter(f["severity"] for f in findings)
    area = Counter(f["area"] for f in findings)
    total = len(findings)

    # Tooling-compatible report: findings must appear as `| ID | Px | title |` rows in a
    # lens_*.md report (tools/lib_findings.py), so prepend the normalized table.
    table = ["## Findings", "", "| ID | Severity | Title | Report |", "|---|---|---|---|"]
    for f in findings:
        table.append("| %s | %s | %s | %s |" % (f["id"], f["severity"], f["title"].replace("|", "\\|"), report_name))
    report_text = ("# Focused security / supply-chain / CI deep-dive - %s\n\n" % repo
                   + "\n".join(table) + "\n\n---\n\n" + report_text)

    idx = ["# Audit run %s - %s" % (run, repo), "",
           "Focused security / supply-chain / CI deep-dive (`%s` @ `%s`)." % (branch, short), "",
           "Counts: " + ", ".join("%s x%s" % (s, sev.get(s, 0)) for s in ("P0", "P1", "P2", "P3")), "",
           "| File | Contents |", "|---|---|",
           "| %s | Full findings write-up |" % report_name,
           "| findings.json | Machine-readable findings |",
           "| EXECUTIVE_SUMMARY.md | Summary |",
           "| risk_register.md / follow_up_register.md | Findings register |",
           "| RELEASE_GATE.md | Gate verdict |",
           "| roadmap.md / patch_plan.md | Remediation plan |",
           "| audit_manifest.json | Run manifest |", ""]
    hi = [f for f in findings if f["severity"] in ("P0", "P1")]
    idx.append("## P0/P1")
    idx += (["- **%s** (%s) %s" % (f["id"], f["severity"], f["title"]) for f in hi] or ["_None._"])
    idx.append("")

    exec_summary = "# Executive summary - %s\n\n%s @ `%s`.\n\n%s\n" % (
        repo, branch, short,
        ", ".join("%s x%s" % (s, sev.get(s, 0)) for s in ("P0", "P1", "P2", "P3")))

    gate = "GO" if sev.get("P0", 0) == 0 and sev.get("P1", 0) == 0 else "GO WITH CONDITIONS"
    release_gate = ("# Release gate - %s\n\nVerdict: **%s**\n\n"
                    "P0 x%d, P1 x%d. See the %s report and registers.\n" % (
                        repo, gate, sev.get("P0", 0), sev.get("P1", 0), report_name))

    roadmap = "# Roadmap\n\n" + "\n".join(
        "- %s (%s) - %s" % (f["id"], f["severity"], f["title"]) for f in findings) + "\n"
    patch_plan = "# Patch plan\n\n" + "\n".join(
        "## %s - %s\n\n%s\n" % (f["id"], f["title"], f.get("recommendation") or "TBD")
        for f in findings) + "\n"

    manifest = {
        "pack": "repo-deep-dive-full-hardening-audit-pack",
        "version": open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VERSION"),
                        encoding="utf-8").read().strip(),
        "profile": "focused-security-supply-chain-ci",
        "outputRoot": "docs/audits/{name}/{run}/",
        "run": run,
        "scaffolded_at": now(),
        "scaffolded_by": "tools/publish_audit.py",
        "promptCount": 4,
        "prompts": ["06_security_authz_tenancy_audit.md", "10_github_actions_cicd_governance.md",
                    "11_supply_chain_dependency_secrets.md", "36_container_runtime_security.md"],
        "scope": {"repo": repo, "repoName": repo, "branch": branch, "commit": sha,
                  "shortCommit": short, "generatedAt": now(),
                  "reports": [report_name]},
        "findings": {"total": total},
    }
    findings_doc = {
        "run": run, "generated": now(), "sourceReports": 1,
        "counts": {"total": total, "bySeverity": dict(sev), "byArea": dict(area)},
        "findings": findings,
    }

    files = {
        "INDEX.md": "\n".join(idx) + "\n",
        report_name: report_text,
        "findings.json": json.dumps(findings_doc, indent=2) + "\n",
        "audit_manifest.json": json.dumps(manifest, indent=2) + "\n",
        "EXECUTIVE_SUMMARY.md": exec_summary,
        "RELEASE_GATE.md": release_gate,
        "risk_register.md": register_md(regs),
        "follow_up_register.md": register_md(regs),
        "roadmap.md": roadmap,
        "patch_plan.md": patch_plan,
    }
    for name in ("lens_deterministic.md", "deterministic-findings.json"):
        src = os.path.join(source_dir, name)
        if os.path.isfile(src):
            files[name] = open(src, encoding="utf-8").read()
    return files


def api(method, path, body=None, token=""):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.github.com" + path, data=data, method=method,
                                 headers={"Authorization": "Bearer " + token,
                                          "Accept": "application/vnd.github+json",
                                          "Content-Type": "application/json",
                                          "User-Agent": "repo-deep-dive-publish-audit"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError("%s %s -> %s %s" % (method, path, e.code, e.read().decode(errors="replace")[:300]))


def publish_pr(repo, branch, run, files, token, org, pr_branch):
    ref = api("GET", "/repos/%s/%s/git/ref/heads/%s" % (org, repo, branch), token=token)
    sha = ref["object"]["sha"]
    try:
        api("POST", "/repos/%s/%s/git/refs" % (org, repo), {"ref": "refs/heads/%s" % pr_branch, "sha": sha}, token)
    except RuntimeError as e:
        if "422" in str(e):
            api("PATCH", "/repos/%s/%s/git/refs/heads/%s" % (org, repo, pr_branch), {"sha": sha, "force": True}, token)
        else:
            raise
    base = "docs/audits/repo-deep-dive/%s" % run
    for name, text in files.items():
        path = "%s/%s" % (base, name)
        body = {"message": "docs(audit): %s/%s" % (run, name),
                "content": base64.b64encode(text.encode("utf-8")).decode("ascii"), "branch": pr_branch}
        # update if the file already exists
        try:
            existing = api("GET", "/repos/%s/%s/contents/%s?ref=%s" % (org, repo, path, pr_branch), token=token)
            body["sha"] = existing.get("sha")
        except RuntimeError:
            pass
        api("PUT", "/repos/%s/%s/contents/%s" % (org, repo, path), body, token)
    # open a draft PR if none exists for this head
    prs = api("GET", "/repos/%s/%s/pulls?head=%s:%s&state=open" % (org, repo, org, pr_branch), token=token)
    if not prs:
        pr = api("POST", "/repos/%s/%s/pulls" % (org, repo), {
            "title": "docs(audit): publish run %s" % run, "head": pr_branch, "base": branch, "draft": True,
            "body": "Canonical audit run `%s` (published by tools/publish_audit.py). Draft for review; never auto-merged." % run,
        }, token)
        return pr.get("html_url")
    return prs[0].get("html_url")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--source-dir", required=True)
    ap.add_argument("--run", default=None)
    ap.add_argument("--org", default="MaineCyberTech")
    ap.add_argument("--pack-dir", default=None, help="pack runs/ dir (default: repo root runs/)")
    ap.add_argument("--no-pack", action="store_true")
    ap.add_argument("--no-pr", action="store_true")
    ap.add_argument("--pr-branch", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() \
        if os.path.isdir(".git") else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pack_runs = a.pack_dir or os.path.join(root, "runs")
    short = a.sha[:7]
    run = a.run or "20261004-0700-%s-%s" % (a.branch, short)
    pr_branch = a.pr_branch or "audit/%s" % run

    items = json.load(open(os.path.join(a.source_dir, "findings.json"), encoding="utf-8"))
    if isinstance(items, dict):
        items = items.get("findings", [])
    report_name = "lens_focused_security_supply_chain_ci.md"
    rpt = os.path.join(a.source_dir, "FINDINGS.md")
    if not os.path.isfile(rpt):
        rpt = os.path.join(a.source_dir, "REPORT.md")
    report_text = open(rpt, encoding="utf-8").read() if os.path.isfile(rpt) else "# %s\n" % run

    files = build_files(a.repo, a.branch, a.sha, run, items, a.source_dir, report_name, report_text)
    print("[publish] %s run=%s files=%d findings=%d" % (a.repo, run, len(files), len(items)))

    # Fail closed: never write to the pack or push a PR if a likely secret is
    # present anywhere in the generated file set (repo-deep-dive-SEC-002).
    hits = scan_secrets(files)
    if hits:
        print("[publish] REFUSING to publish: %d likely secret(s) detected "
              "(redacted):" % len(hits), file=sys.stderr)
        for name, lineno, rule, red in hits:
            print("  %s:%d %s -> %s" % (name, lineno, rule, red), file=sys.stderr)
        print("[publish] redact/remove the value, or add a narrow entry to "
              "publish_audit.SECRET_VALUE_ALLOWLIST.", file=sys.stderr)
        return 2
    try:
        manifest = json.loads(files["audit_manifest.json"])
        manifest["secretScan"] = {"tool": "tools/publish_audit.py scan_secrets",
                                  "result": "pass", "rules": len(SECRET_RULES),
                                  "scannedAt": now()}
        files["audit_manifest.json"] = json.dumps(manifest, indent=2) + "\n"
    except (KeyError, ValueError):
        pass

    if not a.no_pack:
        dest = os.path.join(pack_runs, "%s-%s" % (a.repo, run))
        if a.dry_run:
            print("[publish] would write pack run -> %s" % dest)
        else:
            os.makedirs(dest, exist_ok=True)
            for name, text in files.items():
                with open(os.path.join(dest, name), "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(text)
            print("[publish] wrote pack run -> %s" % dest)
            idx = os.path.join(pack_runs, "INDEX.md")
            if os.path.isfile(idx) and ("%s-%s" % (a.repo, run)) in open(idx, encoding="utf-8").read():
                print("[publish] runs/INDEX.md already lists %s-%s (skipping)" % (a.repo, run))
            elif os.path.isfile(idx):
                row = "| [%s-%s](%s-%s/) | %s | %s @ `%s` | focused (security/supply-chain/CI) | %s | %s | published by tools/publish_audit.py |\n" % (
                    a.repo, run, a.repo, run, now()[:10], a.repo, short,
                    " · ".join("%s ×%s" % (s, Counter(f["severity"] for f in json.loads(files["findings.json"])["findings"]).get(s, 0))
                               for s in ("P0", "P1", "P2", "P3")),
                    "GO" if "P0" not in files["findings.json"] else "REVIEW")
                with open(idx, "a", encoding="utf-8", newline="\n") as fh:
                    fh.write(row)
                print("[publish] appended runs/INDEX.md row")

    if not a.no_pr:
        token = os.environ.get("GH_TOKEN", "")
        if not token:
            print("[publish] GH_TOKEN not set; skipping PR", file=sys.stderr)
        elif a.dry_run:
            print("[publish] would open/update draft PR on %s/%s branch %s" % (a.org, a.repo, pr_branch))
        else:
            url = publish_pr(a.repo, a.branch, run, files, token, a.org, pr_branch)
            print("[publish] draft PR: %s" % url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
