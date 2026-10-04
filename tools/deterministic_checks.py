#!/usr/bin/env python3
"""Deterministic, LLM-free checks for repo-deep-dive (Wave: machine findings).

Runs portable, reproducible checks against any repository and emits findings in
the repo-deep-dive vocabulary (AREA-Px-NNN), so a deep dive produces real
findings even before the prompt-driven audit runs.

Checks:
  PORT  CRLF line endings in tracked text files; non-executable tracked *.sh;
        missing/loose .gitattributes LF policy.
  SEC   gitleaks results (if installed); tracked private-key / .env files.
  CI    actionlint errors (if installed); missing CI workflows.
  DEP   package.json without a lockfile; missing Dependabot config.
  GIT   no LICENSE; large tracked files.
  DOC   no README.

  --deep (opt-in) additionally runs, when the tools are installed:
  DOCKER hadolint on Dockerfiles.
  DEP    trivy filesystem vulnerability scan (lockfiles / dependencies).

Usage:
  tools/deterministic_checks.py <repo-root> [-o OUTDIR] [--run NAME] [--deep]
  tools/deterministic_checks.py <repo-root> --run-folder <run-dir>

Writes OUTDIR/deterministic-findings.json and OUTDIR/lens_deterministic.md.
Deterministic findings use the distinct `DET` area (with the check subcode kept
in the title), so their IDs can never collide with the domain reports' areas
such as SEC/CI (API-P2-001). With `--run-folder`, the lens + JSON are written
into the run folder and merged into its findings.json via collect_findings.py
(API-P2-002).
Read-only against the target repo (gitleaks is run with --no-git --redact).
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

SKIP_DIRS = {".git", "node_modules", ".pnpm", ".next", "dist", "build", "out",
             "vendor", "venv", ".venv", "__pycache__", "coverage"}
TEXT_EXT = {".sh", ".bash", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
            ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini", ".conf", ".md",
            ".txt", ".sql", ".php", ".html", ".css", ".rb", ".go", ".rs", ".java"}
LOCKFILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "npm-shrinkwrap.json")
SECRET_NAME_RE = re.compile(
    r"(^\.env$|^\.env\.[^.]+$|\.pem$|\.p12$|\.pfx$|^id_rsa$|^id_ed25519$|\.asc$)", re.I)
LARGE_FILE_BYTES = 5 * 1024 * 1024


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True,
                           text=True, timeout=60)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def have(cmd):
    return shutil.which(cmd) is not None


# ---------------------------------------------------------------- checks ----

def check_portability(root, add):
    eol = git(root, "ls-files", "--eol")
    crlf = []
    for line in eol.splitlines():
        if "\t" in line:
            left, path = line.split("\t", 1)
        else:
            toks = line.split()
            if not toks:
                continue
            left, path = " ".join(toks[:2]), (toks[-1] if toks else "")
        toks = left.split()
        # Only the INDEX eol matters: a CRLF working tree on Windows is expected.
        if toks and toks[0] in ("i/crlf", "i/mixed"):
            crlf.append(path)
    if crlf:
        add("PORT", "P2", "CRLF committed for %d file(s) (index has CRLF)" % len(crlf),
            "Committed line endings are CRLF, which breaks Linux CI (shell scripts, "
            "hash checks). Add `.gitattributes` with `* text=auto eol=lf`, then "
            "renormalize (`git add --renormalize .`).",
            crlf[:15])

    attrs = os.path.join(root, ".gitattributes")
    if not os.path.exists(attrs):
        add("PORT", "P3", ".gitattributes missing (no line-ending policy)",
            "Without a policy, checkouts differ between Windows and Linux. "
            "Add `* text=auto eol=lf`.", [])
    else:
        txt = open(attrs, encoding="utf-8", errors="replace").read()
        if "text=auto" not in txt and "eol=lf" not in txt:
            add("PORT", "P3", ".gitattributes has no LF policy",
                "Add `* text=auto eol=lf` so Linux checkouts are LF.", [".gitattributes"])

    noexec = []
    for line in git(root, "ls-files", "-s").splitlines():
        m = re.match(r"^(\d{6})\s+\w+\s+\d+\t(.*)$", line)
        if not m:
            continue
        mode, path = m.group(1), m.group(2)
        if path.endswith(".sh") and mode == "100644":
            noexec.append(path)
    if noexec:
        add("PORT", "P2", "%d tracked shell script(s) without the exec bit" % len(noexec),
            "`./script.sh` fails on Linux; set `git update-index --chmod=+x`. "
            "Transfers from Windows drop the bit.", noexec[:15])


def check_secrets(root, add):
    tracked = [p for p in git(root, "ls-files").splitlines()]
    named = [p for p in tracked if SECRET_NAME_RE.search(os.path.basename(p))
             and not p.lower().endswith(".example")]
    if named:
        add("SEC", "P1", "%d tracked secret-adjacent file(s)" % len(named),
            "Tracked `.env`/private keys should be removed and rotated.", named[:15])

    if have("gitleaks"):
        with tempfile.TemporaryDirectory() as td:
            rep = os.path.join(td, "gl.json")
            cmd = ["gitleaks", "detect", "--source", root, "--no-git",
                   "--redact", "--report-format", "json",
                   "--report-path", rep, "--exit-code", "0"]
            repo_cfg = os.path.join(root, ".gitleaks.toml")
            if os.path.exists(repo_cfg):
                # Honor the repo's reviewed allowlist (its own gate already uses it);
                # otherwise reviewed false positives re-report as raw findings.
                cmd += ["--config", repo_cfg]
            subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            leaks = []
            if os.path.exists(rep):
                try:
                    leaks = json.load(open(rep, encoding="utf-8")) or []
                except Exception:
                    leaks = []
            by_rule = {}
            for l in leaks[:200]:
                f = l.get("File", "?")
                try:
                    f = os.path.relpath(f, root)
                except Exception:
                    pass
                by_rule.setdefault(l.get("RuleID", "rule"), []).append(
                    "%s:%s" % (f, l.get("StartLine", "?")))
            high = ("aws", "private-key", "private_key", "github", "gitlab", "slack",
                    "stripe", "sendgrid", "telegram", "twilio", "rsa", "openssh",
                    "pkcs", "azure", "digitalocean", "shopify", "discord", "pypi")
            for rule, hits in sorted(by_rule.items()):
                sev = "P1" if any(k in rule.lower() for k in high) else "P2"
                add("SEC", sev, "gitleaks: %s (%d hit(s))" % (rule, len(hits)),
                    "Potential secret detected by gitleaks (unverified; may be a fixture, "
                    "placeholder, or example file). Confirm and remediate, or allowlist in "
                    "`.gitleaks.toml`.", hits[:10])
    else:
        add("SEC", "P3", "gitleaks not installed (secret scan skipped)",
            "Install gitleaks in CI to enable the secret scan.", [])


def check_ci(root, add):
    wf_dir = os.path.join(root, ".github", "workflows")
    wfs = []
    if os.path.isdir(wf_dir):
        wfs = [f for f in os.listdir(wf_dir) if f.endswith((".yml", ".yaml"))]
    if not wfs:
        add("CI", "P3", "No GitHub Actions workflows", "Add CI for lint/test/build.",
            [])
        return
    if have("actionlint"):
        r = subprocess.run(["actionlint", "-no-color"],
                           cwd=root, capture_output=True, text=True, timeout=300)
        out = (r.stdout + r.stderr).strip()
        if r.returncode != 0 and out:
            add("CI", "P2", "actionlint reported workflow problems",
                "Fix workflow lint errors.", out.splitlines()[:15])


def check_dependencies(root, add):
    pkg = os.path.join(root, "package.json")
    if os.path.exists(pkg):
        if not any(os.path.exists(os.path.join(root, l)) for l in LOCKFILES):
            add("DEP", "P2", "package.json with no lockfile",
                "Unpinned dependencies break reproducibility; commit a lockfile.", [])
    dep = os.path.join(root, ".github", "dependabot.yml")
    if not os.path.exists(dep) and os.path.isdir(os.path.join(root, ".github")):
        add("DEP", "P3", "No Dependabot configuration",
            "Add `.github/dependabot.yml` for dependency updates.", [])


def check_hygiene(root, add):
    names = os.listdir(root)
    if not any(n.upper().startswith("LICENSE") for n in names):
        add("GIT", "P3", "No LICENSE file", "Add a license.", [])
    large = []
    # Tracked files only: an ignored 45 MB generated ruleset must not read as a
    # "large tracked file" (fix 2026-10-04; the prior os.walk flagged gitignored files).
    for rel in git(root, "ls-files").splitlines():
        fp = os.path.join(root, rel)
        try:
            if os.path.getsize(fp) > LARGE_FILE_BYTES:
                large.append(rel)
        except OSError:
            pass
    if large:
        add("GIT", "P3", "%d large tracked file(s) (>5 MB)" % len(large),
            "Large blobs bloat clones; consider Git LFS or removal.", sorted(large)[:10])


def check_docs(root, add):
    names = os.listdir(root)
    if not any(n.lower().startswith("readme") for n in names):
        add("DOC", "P3", "No README", "Add a README.", [])


SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
USE_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")


def check_supply_chain(root, add):
    """Unpinned GitHub Action refs and container images (falcon-style supply-chain checks)."""
    wf_dir = os.path.join(root, ".github", "workflows")
    unpinned = []
    if os.path.isdir(wf_dir):
        for f in os.listdir(wf_dir):
            if not f.endswith((".yml", ".yaml")):
                continue
            p = os.path.join(wf_dir, f)
            for n, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                m = USE_RE.match(line)
                if not m:
                    continue
                ref = m.group(1)
                if ref.startswith("./") or ref.startswith("docker://") or "@" not in ref:
                    continue
                if not SHA40.match(ref.split("@", 1)[1]):
                    unpinned.append("%s:%d %s" % (f, n, ref))
    if unpinned:
        add("SUPPLY", "P2", "%d GitHub Action ref(s) not pinned to a commit SHA" % len(unpinned),
            "Pin `uses:` to a full 40-hex commit SHA (supply-chain hardening).", unpinned[:15])

    imgs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if not ((f.startswith("docker-compose") and f.endswith((".yml", ".yaml")))
                    or f in ("compose.yml", "compose.yaml")):
                continue
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            for n, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                s = line.strip()
                if s.startswith("image:"):
                    val = s.split(":", 1)[1].strip().strip('"').strip("'")
                    if "@sha256:" not in val:
                        imgs.append("%s:%d %s" % (rel, n, val))
    if imgs:
        add("SUPPLY", "P3", "%d container image(s) without a digest pin" % len(imgs),
            "Pin images by digest (`image@sha256:...`) for reproducible, tamper-evident deploys.",
            imgs[:15])


def check_deep(root, add):
    """Opt-in heavier checks: Dockerfile lint (hadolint) and dependency vulns (trivy)."""
    dockerfiles = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f == "Dockerfile" or f.startswith("Dockerfile.") or f.endswith(".Dockerfile"):
                dockerfiles.append(os.path.join(dirpath, f))

    if dockerfiles:
        if have("hadolint"):
            problems = []
            for df in dockerfiles:
                rel = os.path.relpath(df, root).replace(os.sep, "/")
                try:
                    r = subprocess.run(["hadolint", "-f", "json", df],
                                       capture_output=True, text=True, timeout=120)
                    for item in json.loads(r.stdout or "[]"):
                        if item.get("level") in ("error", "warning"):
                            problems.append("%s:%s %s %s" % (rel, item.get("line"),
                                                             item.get("code", ""),
                                                             (item.get("message") or "")[:80]))
                except Exception:
                    pass
            if problems:
                add("SUPPLY", "P3", "Dockerfile lint (hadolint): %d issue(s)" % len(problems),
                    "Harden container builds; load into a registry as non-root with pinned bases.",
                    problems[:15])
        else:
            add("SUPPLY", "P3", "hadolint not installed (Dockerfile lint skipped)",
                "Install hadolint to lint Dockerfiles in --deep mode.", [])

    if have("trivy"):
        with tempfile.TemporaryDirectory() as td:
            rep = os.path.join(td, "trivy.json")
            subprocess.run(["trivy", "fs", "--scanners", "vuln", "--format", "json",
                            "--quiet", "--skip-dirs", "node_modules", "--skip-dirs", ".git",
                            "-o", rep, root], capture_output=True, text=True, timeout=900)
            vulns = []
            if os.path.exists(rep):
                try:
                    data = json.load(open(rep, encoding="utf-8"))
                except Exception:
                    data = {}
                for result in data.get("Results", []):
                    target = result.get("Target", "?")
                    try:
                        target = os.path.relpath(target, root).replace(os.sep, "/")
                    except Exception:
                        pass
                    for v in result.get("Vulnerabilities", []) or []:
                        vulns.append((v.get("Severity", "UNKNOWN"), target,
                                      v.get("VulnerabilityID", "?"), v.get("PkgName", "?")))
            buckets = {}
            for sev, target, vid, pkg in vulns:
                key = {"CRITICAL": "P1", "HIGH": "P1", "MEDIUM": "P2", "LOW": "P3"}.get(sev, "P3")
                buckets.setdefault(key, []).append("%s %s %s" % (target, vid, pkg))
            for key in ("P1", "P2", "P3"):
                hits = buckets.get(key)
                if hits:
                    add("DEP", key, "trivy: %d %s vulnerabilit%s" % (
                        len(hits), key, "y" if len(hits) == 1 else "ies"),
                        "Known CVEs in dependencies; upgrade the affected package. "
                        "Verify and remediate or record a risk acceptance.", sorted(hits)[:15])
    else:
        add("DEP", "P3", "trivy not installed (dependency vuln scan skipped)",
            "Install trivy to enable the --deep dependency vulnerability scan.", [])


# ---------------------------------------------------------------- driver ----

def run_checks(root, deep=False):
    raw = []

    # `subcode` is the check family (SEC/CI/PORT/...); it is rendered into the
    # title only. Every deterministic ID uses the single `DET` area so it can
    # never collide with a domain report's own area counter (API-P2-001).
    def add(subcode, sev, title, detail, evidence):
        raw.append({"subcode": subcode, "severity": sev, "title": title,
                    "detail": detail, "evidence": list(evidence)})

    check_portability(root, add)
    check_secrets(root, add)
    check_ci(root, add)
    check_dependencies(root, add)
    check_supply_chain(root, add)
    check_hygiene(root, add)
    check_docs(root, add)
    if deep:
        check_deep(root, add)

    # assign stable IDs: one namespaced DET area, ordered by subcode/severity/title
    raw.sort(key=lambda f: (f["subcode"], f["severity"], f["title"]))
    counters = {}
    findings = []
    for f in raw:
        area = "DET"
        counters[area] = counters.get(area, 0) + 1
        fid = "%s-%s-%03d" % (area, f["severity"], counters[area])
        findings.append({"id": fid, "severity": f["severity"],
                         "title": "[%s] %s" % (f["subcode"], f["title"]),
                         "report": "lens_deterministic.md", "line": 1,
                         "detail": f["detail"], "evidence": f["evidence"]})
    return findings


def counts(findings):
    by_sev, by_area = {}, {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        a = f["id"].split("-")[0]
        by_area[a] = by_area.get(a, 0) + 1
    return {"bySeverity": dict(sorted(by_sev.items())),
            "byArea": dict(sorted(by_area.items())), "total": len(findings)}


def render_markdown(name, findings):
    """Render the deterministic lens and set each finding's real heading line.

    Each finding records the 1-based line of its `### Finding ID:` heading
    (DATA-P3-003) and the heading uses the shared ASCII ` - ` separator so the
    same parser that reads the domain reports reads this lens.
    """
    # The summary table deliberately puts Title before Severity: the shared
    # table parser (lib_findings.ROW) expects `| ID | Px | ...`, so this keeps
    # the lens from being counted twice (table row + detail heading).
    lines = ["# Deterministic checks - %s" % name, "",
             "Machine checks (no LLM). Findings use the repo-deep-dive `DET` area.",
             "", "## Findings", "", "| ID | Title | Severity |", "|---|---|---|"]
    for f in findings:
        lines.append("| %s | %s | %s |" % (f["id"], f["title"], f["severity"]))
    lines += ["", "## Detail", ""]
    for f in findings:
        f["line"] = len(lines) + 1
        lines.append("### Finding ID: %s - %s" % (f["id"], f["title"]))
        lines.append("")
        lines.append(f["detail"])
        if f["evidence"]:
            lines.append("")
            lines.append("Evidence:")
            lines.append("")
            for e in f["evidence"]:
                lines.append("- `%s`" % e)
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", help="repository root (read-only)")
    ap.add_argument("-o", "--outdir", default=None, help="output directory")
    ap.add_argument("--run", default=None, help="run name (default: repo basename)")
    ap.add_argument("--deep", action="store_true",
                    help="also run hadolint/trivy (only when installed)")
    ap.add_argument("--run-folder", default=None,
                    help="import path: write the lens + JSON into an audit run "
                         "folder and merge them into its findings.json")
    args = ap.parse_args()

    if not os.path.isdir(args.repo):
        print("error: not a directory: %s" % args.repo, file=sys.stderr)
        raise SystemExit(2)

    root = os.path.abspath(args.repo)
    name = args.run or os.path.basename(root)
    if args.run_folder:
        outdir = os.path.abspath(args.run_folder)
        if not os.path.isdir(outdir):
            print("error: --run-folder not a directory: %s" % args.run_folder,
                  file=sys.stderr)
            raise SystemExit(2)
    else:
        outdir = args.outdir or os.path.join(root, "deterministic-out")
    os.makedirs(outdir, exist_ok=True)

    findings = run_checks(root, deep=args.deep)
    c = counts(findings)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = {"run": name, "generated": now, "sourceReports": 1,
           "counts": c, "findings": findings}

    # Render first: it assigns each finding the real line of its heading.
    markdown = render_markdown(name, findings)
    jpath = os.path.join(outdir, "deterministic-findings.json")
    open(jpath, "w", encoding="utf-8").write(json.dumps(doc, indent=2) + "\n")
    mpath = os.path.join(outdir, "lens_deterministic.md")
    open(mpath, "w", encoding="utf-8").write(markdown)

    print("repo: %s" % name)
    print("findings: %d %s" % (c["total"], c["bySeverity"]))
    print("areas: %s" % c["byArea"])
    print("wrote %s" % jpath)
    print("wrote %s" % mpath)

    if args.run_folder:
        collect = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "collect_findings.py")
        if os.path.exists(collect):
            r = subprocess.run([sys.executable, collect, outdir, "--write"],
                               capture_output=True, text=True)
            sys.stdout.write(r.stdout)
            if r.returncode != 0:
                sys.stderr.write(r.stderr)
                print("warning: deterministic lens written, but collect_findings.py "
                      "failed; run it manually to merge into findings.json",
                      file=sys.stderr)
            elif not r.stdout.strip():
                print("merged into %s/findings.json" % outdir)


if __name__ == "__main__":
    main()
