#!/usr/bin/env python3
"""Full-domain (all-domain) deep-dive driver for repo-deep-dive (roadmap item 13/20).

A "full-domain pass" walks the master runner's per-domain prompts; each domain is
run by a subagent that writes machine findings, then this tool normalizes them to
the pack's `AREA-Px-NNN` vocabulary, renders the domain reports, and aggregates a
run that passes `tools/check_run.sh` and `tools/lint_pack.sh`.

It is also the supported `--fast` / `--full` budget boundary (roadmap item 20):

  * `--fast` = deterministic checks + security / supply-chain / CI domains only
  * `--full` = every domain prompt in `prompts/MASTER_RUNNER_FULL_HARDENING.md`

Pipeline (one subcommand each):

    init  -> emit (per domain, as subagents finish) -> aggregate -> [publish]

`emit` never assigns an ID it cannot justify: a finding may already carry a
pack-schema ID (item 19); otherwise aggregate assigns the next free
`AREA-Px-NNN` for the domain's area. `aggregate` is the single writer of
`findings.json`, the registers, the finals, and `audit_manifest.json`, so the
run is internally consistent by construction.

Usage:
  python3 tools/full_domain.py domains [--fast|--full] [--json]
  python3 tools/full_domain.py init --repo falcon --branch main --sha <sha> \
      [--run R] [--mode fast|full] [--repo-root PATH] [--out DIR] [--pack]
  python3 tools/full_domain.py emit --run DIR --domain deterministic \
      --input <deterministic-findings.json> [--report <lens_deterministic.md>]
  python3 tools/full_domain.py emit --run DIR --domain 06_security_authz_tenancy_audit.md \
      --input <findings.json> [--report <body.md>]
  python3 tools/full_domain.py aggregate --run DIR [--gate GO|"GO WITH CONDITIONS"|NO-GO] \
      [--check] [--pack]
  python3 tools/full_domain.py status --run DIR [--json]
  python3 tools/full_domain.py run --repo falcon --branch main --sha <sha> \
      --repo-root PATH --fast [--agent-cmd '...{out}...'] [--pack] [--check]

Stdlib only; generated files are written LF-normalized.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from datetime import datetime, timezone

sys.dont_write_bytecode = True

TOOLS = os.path.dirname(os.path.abspath(__file__))
PACK_ROOT = os.path.abspath(os.path.join(TOOLS, ".."))
sys.path.insert(0, TOOLS)
import lib_findings  # noqa: E402

MASTER = "prompts/MASTER_RUNNER_FULL_HARDENING.md"
DEVICES = ("P0", "P1", "P2", "P3")
AREA_RX = re.compile(r"beginning with `([A-Z]+)`")
ID_RX = re.compile(r"^([A-Z]+)-P[0-3]-\d{3}$")
FAST_FILES = (
    "06_security_authz_tenancy_audit.md",
    "10_github_actions_cicd_governance.md",
    "11_supply_chain_dependency_secrets.md",
)
DETERMINISTIC = "deterministic"
ALLOWED_STATUS = {"", "open", "partially-fixed", "verified-fixed",
                  "still-open", "regressed", "owner-accepted"}
GATES = ("GO", "GO WITH CONDITIONS", "NO-GO")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def die(msg):
    print("error: %s" % msg, file=sys.stderr)
    raise SystemExit(2)


def pack_path(*parts):
    return os.path.join(PACK_ROOT, *parts)


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text, newline="\n"):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline=newline) as fh:
        fh.write(text)


def wsl_path(path):
    """Windows path -> /mnt/<drive>/... so the pack's bash tools can read it."""
    path = os.path.abspath(path)
    if os.name != "nt":
        return path
    drive, rest = os.path.splitdrive(path)
    return "/mnt/" + drive[0].lower() + rest.replace("\\", "/")


def run_check(run_dir):
    """Run tools/check_run.sh (via WSL on Windows) and return its exit code."""
    check = pack_path("tools", "check_run.sh")
    if os.name == "nt":
        cmd = ["wsl.exe", "-d", "Ubuntu-24.04", "--", "bash",
               wsl_path(check), wsl_path(run_dir)]
    else:
        cmd = ["bash", check, run_dir]
    return subprocess.run(cmd, text=True).returncode


# --- domain registry -------------------------------------------------------------

def master_order():
    """The per-domain prompt files, in master-runner order."""
    out = []
    for m in re.finditer(r"^\d+\.\s+`([^`]+\.md)`", read_text(pack_path(MASTER)), re.M):
        out.append(m.group(1))
    if not out:
        die("could not parse domain order from %s" % MASTER)
    return out


def prompt_area(fname):
    m = AREA_RX.search(read_text(pack_path("prompts", fname)))
    return m.group(1) if m else "GEN"


def prompt_title(fname):
    for line in read_text(pack_path("prompts", fname)).splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fname


def domain_registry():
    out = []
    for fname in master_order():
        out.append({
            "domain": fname[:-3],
            "file": fname,
            "area": prompt_area(fname),
            "title": prompt_title(fname),
            "kind": "prompt",
        })
    return out


def select(mode):
    reg = domain_registry()
    if mode == "full":
        return [DET_DOMAIN()] + reg
    fast = {f: d for d in reg for f in [d["file"]] if d["file"] in FAST_FILES}
    missing = [f for f in FAST_FILES if f not in fast]
    if missing:
        die("fast domains missing from the master runner: %s" % ", ".join(missing))
    return [DET_DOMAIN()] + [fast[f] for f in FAST_FILES]


def DET_DOMAIN():
    return {"domain": DETERMINISTIC, "file": "lens_deterministic.md", "area": "DET",
            "title": "Deterministic checks (machine, LLM-free)", "kind": "deterministic"}


def find_domain(mode_or_domains, key):
    for d in mode_or_domains:
        if key in (d["domain"], d["file"], d["area"]):
            return d
    return None


# --- run scaffold ----------------------------------------------------------------

def pack_version():
    try:
        return read_text(pack_path("VERSION")).strip()
    except OSError:
        return "0"


def default_run(repo, mode, branch, sha):
    return "%s-%s-%s-%s-%s" % (repo, datetime.now(timezone.utc).strftime("%Y%m%d"),
                               mode, branch or "manual", (sha or "manual")[:7])


def run_dir_for(args, run):
    if args.out:
        return os.path.abspath(args.out)
    return pack_path("runs", run)


def manifest_for(repo, branch, sha, run, mode, domains, repo_root):
    return {
        "pack": "repo-deep-dive-full-hardening-audit-pack",
        "profile": "base",
        "version": pack_version(),
        "promptCount": len([d for d in domains if d["kind"] == "prompt"]),
        "recommendedName": "repo-deep-dive",
        "outputRoot": "docs/audits/{name}/{run}/",
        "run": run,
        "scaffolded_at": now(),
        "scaffolded_by": "tools/full_domain.py",
        "mode": mode,
        "scope": {
            "name": repo,
            "targetRepo": repo_root or "",
            "targetUrl": "https://github.com/MaineCyberTech/%s" % repo if repo else "",
            "branch": branch,
            "commit": sha,
            "shortCommit": (sha or "")[:7],
            "profile": "base",
            "readOnly": True,
            "secretsRedacted": True,
            "generatedAt": now(),
            "domains": [d["domain"] for d in domains],
            "lenses": [d["area"] for d in domains],
            "releaseGate": "pending",
        },
        "findings": {"bySeverity": {}, "byArea": {}, "total": 0},
    }


def render_index(m, domains, coverage, counts):
    gate = m.get("scope", {}).get("releaseGate", "pending")
    sev = counts.get("bySeverity", {})
    lines = [
        "# Audit Run Index", "",
        "## Metadata", "",
        "- Name: %s" % m["scope"]["name"],
        "- Run: `%s`" % m["run"],
        "- Mode: %s" % m.get("mode", "full"),
        "- Profile: base",
        "- Target repo: `%s`" % m["scope"].get("targetRepo", ""),
        "- Branch: `%s`" % m["scope"].get("branch", ""),
        "- Commit: `%s`" % m["scope"].get("shortCommit", ""),
        "- Release gate: **%s**" % gate,
        "- Findings: %d total — %s" % (
            counts.get("total", 0),
            ", ".join("%s %d" % (s, sev.get(s, 0)) for s in DEVICES)), "",
        "## Domains", "",
        "| Domain | Area | Findings | Status |", "|---|---|---:|---|",
    ]
    for d in domains:
        c = coverage.get(d["domain"], {})
        lines.append("| %s | %s | %d | %s |" % (
            d["domain"], d["area"], c.get("total", 0),
            "done" if c.get("total", 0) or c.get("emitted") else "not run"))
    lines += ["", "## Key Outputs", "",
              "- Executive summary: `EXECUTIVE_SUMMARY.md`",
              "- Risk register: `risk_register.md`",
              "- Follow-up register: `follow_up_register.md`",
              "- Coverage: `coverage.md`",
              "- Roadmap: `roadmap.md`",
              "- Patch plan: `patch_plan.md`",
              "- Release gate: `RELEASE_GATE.md` — **%s**" % gate, "",
              "## Next Actions", "",
              "1. Validate: `tools/check_run.sh %s`." % m["run"],
              "2. Publish: `tools/publish_audit.py --repo %s ...` (see runbook)." % m["scope"]["name"],
              "3. Remediate unresolved P0/P1/P2 per `patch_plan.md`.", ""]
    return "\n".join(lines) + "\n"


def render_coverage(domains, coverage, mode):
    lines = ["# Coverage — %s pass" % mode, "",
             "| Domain | Prompt / lens | Area | Findings |",
             "|---|---|---|---:|"]
    for d in domains:
        c = coverage.get(d["domain"], {})
        lines.append("| %s | `%s` | %s | %d |" % (
            d["domain"], d["file"], d["area"], c.get("total", 0)))
    lines += ["", "Domains not listed were not part of this %s pass." % mode, ""]
    return "\n".join(lines)


# --- emit ------------------------------------------------------------------------

def load_emitted(run_dir):
    ddir = os.path.join(run_dir, "_domains")
    out = OrderedDict()
    if not os.path.isdir(ddir):
        return out
    for name in sorted(os.listdir(ddir)):
        if name.endswith(".json"):
            with open(os.path.join(ddir, name), encoding="utf-8") as fh:
                out[name[:-5]] = json.load(fh)
    return out


def save_emitted(run_dir, domain, findings, report):
    ddir = os.path.join(run_dir, "_domains")
    os.makedirs(ddir, exist_ok=True)
    write_text(os.path.join(ddir, "%s.json" % domain["domain"]),
               json.dumps({"domain": domain["domain"], "file": domain["file"],
                           "area": domain["area"], "agent": "subagent",
                           "emitted_at": now(), "findings": findings,
                           "report": report or ""}, indent=2) + "\n")


def cmd_emit(a):
    run_dir = os.path.abspath(a.run)
    if not os.path.isdir(run_dir):
        die("run folder not found: %s (run `init` first)" % run_dir)
    mode = "full"
    man = os.path.join(run_dir, "audit_manifest.json")
    if os.path.isfile(man):
        mode = json.load(open(man, encoding="utf-8")).get("mode", "full")
    domain = find_domain(select(mode), a.domain)
    if not domain:
        die("unknown domain %r (see `full_domain.py domains`)" % a.domain)
    raw = json.load(open(a.input, encoding="utf-8"))
    findings = raw.get("findings", raw) if isinstance(raw, dict) else raw
    if not isinstance(findings, list):
        die("input must be a findings array or {\"findings\": [...]}")
    clean = []
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            die("finding %d is not an object" % i)
        sev = str(f.get("severity", "")).upper()
        if sev not in DEVICES:
            die("finding %d has bad severity %r" % (i, f.get("severity")))
        if not str(f.get("title", "")).strip():
            die("finding %d has no title" % i)
        rec = dict(f)
        rec["severity"] = sev
        rec.setdefault("area", domain["area"])
        rec["status"] = rec.get("status", "open")
        if rec["status"] not in ALLOWED_STATUS:
            die("finding %d has bad status %r" % (i, rec["status"]))
        rec.setdefault("owner", "@owner")
        rec.setdefault("target", domain["area"])
        clean.append(rec)
    report = a.report and read_text(a.report) or raw.get("report", "") if isinstance(raw, dict) else ""
    save_emitted(run_dir, domain, clean, report)
    print("[emit] %s -> %s (%d findings)" % (a.domain, domain["domain"], len(clean)))
    return 0


# --- aggregate -------------------------------------------------------------------

def assign_ids(domains, emitted):
    """Global, deterministic AREA-Px-NNN assignment across every domain."""
    used = set()
    counters = Counter()
    result = OrderedDict()
    for d in domains:
        raw = emitted.get(d["domain"])
        if not raw:
            continue
        rows = []
        for f in raw.get("findings", []):
            sev = str(f["severity"]).upper()
            fid = str(f.get("id", "")).strip()
            area = str(f.get("area") or d["area"]).upper()
            ok = bool(ID_RX.match(fid)) and fid.split("-")[0] == area and fid not in used
            if not ok:
                counters[(area, sev)] += 1
                n = counters[(area, sev)]
                fid = "%s-%s-%03d" % (area, sev, n)
                while fid in used:
                    counters[(area, sev)] += 1
                    n = counters[(area, sev)]
                    fid = "%s-%s-%03d" % (area, sev, n)
            used.add(fid)
            rec = dict(f)
            rec["id"] = fid
            rec["area"] = area
            rows.append(rec)
        result[d["domain"]] = rows
    return result


def render_domain_report(m, d, rows, body):
    head = ["# %s — %s" % (d["domain"], d["title"]), "",
            "- Run: `%s`" % m["run"],
            "- Target: `%s` @ `%s` (branch `%s`)" % (
                m["scope"]["name"], m["scope"].get("shortCommit", ""),
                m["scope"].get("branch", "")),
            "- Domain: `%s` (area %s, %s)" % (d["file"], d["area"], d["kind"]), "",
            "## Verification Performed", "",
            body.strip() or ("Domain subagent produced %d finding(s) at the bound commit; "
                             "machine IDs assigned by tools/full_domain.py." % len(rows)), "",
            "## Findings", ""]
    if rows:
        head += ["| ID | Severity | Title |", "|---|---|---|"]
        for f in rows:
            head.append("| %s | %s | %s |" % (f["id"], f["severity"],
                                              str(f["title"]).replace("|", "\\|")))
    else:
        head.append("_No findings in this domain._")
    head.append("")
    return "\n".join(head)


def render_deterministic_report(d, rows):
    lines = ["# Deterministic checks — %s" % d["domain"], "",
             "Machine checks (no LLM). Findings use the `DET` area.", "",
             "## Findings", "",
             "| ID | Title | Severity |", "|---|---|---|"]
    for f in rows:
        lines.append("| %s | %s | %s |" % (f["id"], f["title"], f["severity"]))
    lines += ["", "## Detail", ""]
    for f in rows:
        lines += ["### Finding ID: %s - %s" % (f["id"], f["title"]), "",
                  f.get("detail", ""), ""]
        for ev in f.get("evidence") or []:
            lines.append("- `%s`" % ev)
        lines.append("")
    return "\n".join(lines)


def register_md(run, m, findings):
    lines = ["# Follow-up register", "",
             "Run: `%s` · Target: `%s` @ `%s` · Profile: base" % (
                 run, m["scope"]["name"], m["scope"].get("shortCommit", "")), "",
             "Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.", "",
             "| Finding | Severity | Title | Owner | Target | Status | Note |",
             "|---|---|---|---|---|---|---|"]
    for f in findings:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            f["id"], f["severity"], str(f["title"]).replace("|", "\\|"),
            f.get("owner") or "@owner",
            f.get("target") or f.get("area") or f["id"].split("-")[0],
            f.get("status") or "open",
            str(f.get("note", "")).replace("|", "\\|")))
    return "\n".join(lines) + "\n"


def compute_gate(counts, override):
    if override:
        if override not in GATES:
            die("--gate must be one of: %s" % ", ".join(GATES))
        return override
    sev = counts.get("bySeverity", {})
    if sev.get("P0", 0) > 0:
        return "NO-GO"
    if sev.get("P1", 0) > 0:
        return "GO WITH CONDITIONS"
    return "GO"


def write_exec_summary(m, counts, findings):
    sev = counts.get("bySeverity", {})
    hi = [f for f in findings if f["severity"] in ("P0", "P1")]
    lines = ["# Executive Summary", "",
             "- Target: `%s` @ `%s` (branch `%s`)" % (
                 m["scope"]["name"], m["scope"].get("shortCommit", ""), m["scope"].get("branch", "")),
             "- Run: `%s` (%s mode, full-domain)" % (m["run"], m.get("mode", "full")),
             "- Verdict: **%s**" % m["scope"].get("releaseGate", "pending"), "",
             "## Findings", "",
             "- %d total: %s." % (counts.get("total", 0),
                                  ", ".join("%s %d" % (s, sev.get(s, 0)) for s in DEVICES)),
             "- Domains covered: %s." % ", ".join(m["scope"].get("domains", [])), ""]
    if hi:
        lines += ["Top risks:", ""]
        for f in hi:
            lines.append("- `%s` — %s" % (f["id"], f["title"]))
        lines.append("")
    return "\n".join(lines) + "\n"


def write_release_gate(m, counts, findings):
    lines = ["# Release Gate", "",
             "- Target: `%s` @ `%s` (`%s`)" % (
                 m["scope"]["name"], m["scope"].get("shortCommit", ""), m["scope"].get("branch", "")),
             "- Run: `%s`" % m["run"],
             "- Decision: **%s**" % m["scope"].get("releaseGate", "pending"), "",
             "## Basis", "",
             "- %s." % ", ".join("%s x%d" % (s, counts.get("bySeverity", {}).get(s, 0))
                                 for s in DEVICES), ""]
    blockers = [f for f in findings if f["severity"] in ("P0", "P1")]
    if blockers:
        lines += ["## Blocking findings", "", "| ID | Sev | Title |", "|---|---|---|"]
        for f in blockers:
            lines.append("| %s | %s | %s |" % (f["id"], f["severity"], f["title"]))
        lines.append("")
    lines += ["## Verification required to change the verdict", "",
              "Re-run the owning domains at the remediated commit and capture artifacts; "
              "confirm zero P0/P1 remains. This run records a delta only.", ""]
    return "\n".join(lines) + "\n"


def cmd_aggregate(a):
    run_dir = os.path.abspath(a.run)
    man_path = os.path.join(run_dir, "audit_manifest.json")
    if not os.path.isfile(man_path):
        die("no audit_manifest.json in %s (run `init` first)" % run_dir)
    m = json.load(open(man_path, encoding="utf-8"))
    mode = m.get("mode", "full")
    domains = select(mode)
    emitted = load_emitted(run_dir)
    assigned = assign_ids(domains, emitted)

    coverage = {}
    for d in domains:
        rows = assigned.get(d["domain"], [])
        coverage[d["domain"]] = {"total": len(rows),
                                 "emitted": d["domain"] in emitted}
        if d["kind"] == "deterministic":
            write_text(os.path.join(run_dir, "deterministic-findings.json"),
                       json.dumps({"run": m["run"], "generated": now(),
                                   "sourceReports": 1,
                                   "counts": {"total": len(rows)},
                                   "findings": rows}, indent=2) + "\n")
            write_text(os.path.join(run_dir, "lens_deterministic.md"),
                       render_deterministic_report(d, rows))
            continue
        body = (emitted.get(d["domain"], {}) or {}).get("report", "")
        write_text(os.path.join(run_dir, d["file"]), render_domain_report(m, d, rows, body))

    # Final finding list is the single source of truth: scan the reports we just
    # wrote, then merge deterministic findings (same rule as collect_findings.py).
    # Register fields (owner/target/status/note/recommendation) are carried from
    # the subagent payloads via the assigned rows, not re-read from a register.
    _, findings, dupes = lib_findings.collect_with_dupes(run_dir)
    meta = {}
    for rows in assigned.values():
        for r in rows:
            meta[r["id"]] = r
    known = {f["id"] for f in findings}
    det_path = os.path.join(run_dir, "deterministic-findings.json")
    if os.path.isfile(det_path):
        for f in json.load(open(det_path, encoding="utf-8")).get("findings", []):
            if f.get("id") and f["id"] not in known:
                findings.append(f)
                known.add(f["id"])
    for f in findings:
        r = meta.get(f["id"], {})
        f["area"] = r.get("area") or f["id"].split("-")[0]
        f["owner"] = r.get("owner") or "@owner"
        f["target"] = r.get("target") or f["area"]
        f["status"] = r.get("status") or "open"
        f["note"] = r.get("note", "")
        for extra in ("recommendation", "detail"):
            if r.get(extra):
                f[extra] = r[extra]
    findings.sort(key=lambda f: (f["severity"], f["id"]))
    counts = lib_findings.counts(findings)
    if dupes:
        print("warning: duplicate finding IDs: %s" % ", ".join(sorted(dupes)), file=sys.stderr)

    gate = compute_gate(counts, a.gate)
    m["scope"]["releaseGate"] = gate
    m["scope"]["generatedAt"] = now()
    m["findings"] = {"bySeverity": counts["bySeverity"], "byArea": counts["byArea"],
                     "total": counts["total"]}
    m["scaffolded_by"] = "tools/full_domain.py aggregate"

    write_text(os.path.join(run_dir, "findings.json"),
               json.dumps({"run": m["run"], "generated": now(),
                           "sourceReports": len([d for d in domains if d["kind"] == "prompt"]),
                           "counts": counts, "findings": findings}, indent=2) + "\n")
    reg = register_md(m["run"], m, findings)
    write_text(os.path.join(run_dir, "risk_register.md"), reg)
    write_text(os.path.join(run_dir, "follow_up_register.md"), reg)
    write_text(os.path.join(run_dir, "EXECUTIVE_SUMMARY.md"), write_exec_summary(m, counts, findings))
    write_text(os.path.join(run_dir, "RELEASE_GATE.md"), write_release_gate(m, counts, findings))
    write_text(os.path.join(run_dir, "roadmap.md"),
               "# Roadmap\n\n" + "\n".join(
                   "- %s (%s) — %s" % (f["id"], f["severity"], f["title"]) for f in findings) + "\n")
    write_text(os.path.join(run_dir, "patch_plan.md"),
               "# Patch plan\n\n" + "\n".join(
                   "## %s — %s\n\n%s\n" % (f["id"], f["title"],
                                           f.get("recommendation") or f.get("detail") or "TBD")
                   for f in findings) + "\n")
    write_text(os.path.join(run_dir, "coverage.md"), render_coverage(domains, coverage, mode))
    write_text(os.path.join(run_dir, "audit_manifest.json"),
               json.dumps(m, indent=2) + "\n")
    write_text(os.path.join(run_dir, "INDEX.md"), render_index(m, domains, coverage, counts))

    if a.pack and os.path.dirname(run_dir) == pack_path("runs"):
        index = pack_path("runs", "INDEX.md")
        row_name = os.path.basename(run_dir)
        if os.path.isfile(index) and row_name not in read_text(index):
            sev = counts["bySeverity"]
            row = "| [%s](%s/) | %s | %s @ `%s` | %s-domain %s | %s | %s | generated by tools/full_domain.py |\n" % (
                row_name, row_name, now()[:10], m["scope"]["name"],
                m["scope"].get("shortCommit", ""), mode,
                ", ".join(m["scope"].get("domains", [])),
                " · ".join("%s ×%s" % (s, sev.get(s, 0)) for s in DEVICES), gate)
            with open(index, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(row)
            print("[aggregate] appended runs/INDEX.md row")

    print("[aggregate] %s: %d findings (%s) gate=%s" % (
        m["run"], counts["total"],
        ", ".join("%s x%d" % (s, counts["bySeverity"].get(s, 0)) for s in DEVICES), gate))
    if a.check:
        if run_check(run_dir) != 0:
            return 1
    return 0


# --- init / status / run ---------------------------------------------------------

def cmd_init(a):
    mode = a.mode
    domains = select(mode)
    run = a.run or default_run(a.repo, mode, a.branch, a.sha)
    run_dir = run_dir_for(a, run)
    if os.path.isdir(run_dir) and os.listdir(run_dir):
        die("refusing to touch non-empty directory: %s" % run_dir)
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(os.path.join(run_dir, "_domains"), exist_ok=True)
    m = manifest_for(a.repo, a.branch, a.sha, run, mode, domains, a.repo_root)
    write_text(os.path.join(run_dir, "audit_manifest.json"), json.dumps(m, indent=2) + "\n")
    write_text(os.path.join(run_dir, "INDEX.md"),
               render_index(m, domains, {}, {"total": 0, "bySeverity": {}}))
    write_text(os.path.join(run_dir, "coverage.md"), render_coverage(domains, {}, mode))
    print("created %s" % run_dir)
    print("mode=%s domains=%d" % (mode, len(domains)))
    print("next: emit per-domain findings, then `full_domain.py aggregate --run %s`" % run_dir)
    return 0


def cmd_domains(a):
    domains = select(a.mode)
    if a.json:
        print(json.dumps(domains, indent=2))
    else:
        for d in domains:
            print("%-32s %-10s %s" % (d["domain"], d["area"], d["file"]))
    return 0


def cmd_status(a):
    run_dir = os.path.abspath(a.run)
    m = json.load(open(os.path.join(run_dir, "audit_manifest.json"), encoding="utf-8"))
    domains = select(m.get("mode", "full"))
    emitted = load_emitted(run_dir)
    rows = []
    for d in domains:
        e = emitted.get(d["domain"])
        rows.append({"domain": d["domain"], "area": d["area"],
                     "emitted": e is not None,
                     "findings": len(e.get("findings", [])) if e else 0})
    if a.json:
        print(json.dumps({"run": m["run"], "mode": m.get("mode"),
                          "domains": rows}, indent=2))
        return 0
    print("run %s (%s)" % (m["run"], m.get("mode")))
    for r in rows:
        print("  %-32s %-8s %s (%d)" % (r["domain"], r["area"],
              "emitted" if r["emitted"] else "pending", r["findings"]))
    return 0


def cmd_run(a):
    domains = select(a.mode)
    run = a.run or default_run(a.repo, a.mode, a.branch, a.sha)
    run_dir = run_dir_for(a, run)
    if not os.path.isdir(run_dir):
        args = argparse.Namespace(**vars(a))
        args.mode = a.mode
        cmd_init(args)
    print("[run] %s mode=%s domains=%d" % (run, a.mode, len(domains)))
    pending = []
    for d in domains:
        out = os.path.join(run_dir, "_domains", "%s.json" % d["domain"])
        if os.path.isfile(out):
            print("  [skip] %s already emitted" % d["domain"])
            continue
        if not a.agent_cmd:
            pending.append(d)
            continue
        prompt_file = d["file"] if d["kind"] == "prompt" else "automation deterministic lens"
        cmd = a.agent_cmd.format(prompt_file=prompt_file, domain=d["domain"],
                                 area=d["area"], out=out, repo=a.repo, run=run,
                                 repo_root=a.repo_root or "", branch=a.branch or "",
                                 sha=a.sha or "")
        print("  [agent] %s -> %s" % (d["domain"], out))
        r = subprocess.run(cmd, shell=True, cwd=PACK_ROOT)
        if r.returncode != 0:
            print("  [warn] agent for %s exited %d" % (d["domain"], r.returncode),
                  file=sys.stderr)
        if os.path.isfile(out):
            subprocess.run([sys.executable, os.path.join(TOOLS, "full_domain.py"),
                            "emit", "--run", run_dir, "--domain", d["domain"],
                            "--input", out], check=False)
    if pending:
        print("[run] no --agent-cmd; %d domain(s) awaiting subagent output:" % len(pending))
        for d in pending:
            print("    %s (area %s) -> %s" % (d["domain"], d["area"],
                  os.path.join(run_dir, "_domains", "%s.json" % d["domain"])))
        print("[run] aggregate with: full_domain.py aggregate --run %s" % run_dir)
        if not a.agent_cmd:
            return 0
    return cmd_aggregate(argparse.Namespace(run=run_dir, gate=a.gate, check=a.check,
                                            pack=a.pack))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("domains")
    p.add_argument("--mode", choices=("fast", "full"), default="fast")
    p.add_argument("--fast", dest="mode", action="store_const", const="fast")
    p.add_argument("--full", dest="mode", action="store_const", const="full")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_domains)

    p = sub.add_parser("init")
    p.add_argument("--repo", required=True)
    p.add_argument("--branch", default="")
    p.add_argument("--sha", default="")
    p.add_argument("--run", default=None)
    p.add_argument("--repo-root", dest="repo_root", default="")
    p.add_argument("--out", default=None)
    p.add_argument("--pack", action="store_true", help="install under the pack's runs/")
    p.add_argument("--mode", choices=("fast", "full"), default="fast")
    p.add_argument("--fast", dest="mode", action="store_const", const="fast")
    p.add_argument("--full", dest="mode", action="store_const", const="full")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("emit")
    p.add_argument("--run", required=True)
    p.add_argument("--domain", required=True, help="domain name, prompt file, or area")
    p.add_argument("--input", required=True, help="subagent findings JSON")
    p.add_argument("--report", default=None, help="optional report body markdown")
    p.set_defaults(fn=cmd_emit)

    p = sub.add_parser("aggregate")
    p.add_argument("--run", required=True)
    p.add_argument("--gate", default=None, choices=GATES)
    p.add_argument("--check", action="store_true", help="run tools/check_run.sh after writing")
    p.add_argument("--pack", action="store_true", help="append the runs/INDEX.md row")
    p.set_defaults(fn=cmd_aggregate)

    p = sub.add_parser("status")
    p.add_argument("--run", required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("run")
    p.add_argument("--repo", required=True)
    p.add_argument("--branch", default="")
    p.add_argument("--sha", default="")
    p.add_argument("--repo-root", dest="repo_root", default="")
    p.add_argument("--run", default=None)
    p.add_argument("--out", default=None)
    p.add_argument("--pack", action="store_true")
    p.add_argument("--mode", choices=("fast", "full"), default="fast")
    p.add_argument("--fast", dest="mode", action="store_const", const="fast")
    p.add_argument("--full", dest="mode", action="store_const", const="full")
    p.add_argument("--agent-cmd", dest="agent_cmd", default=None,
                   help="shell template with {prompt_file},{domain},{out},{repo},"
                        "{run},{repo_root},{branch},{sha}; omit to plan only")
    p.add_argument("--gate", default=None, choices=GATES)
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_run)

    a = ap.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
