"""Shared finding extraction for repo-deep-dive tools (read-only)."""

import pathlib
import re

ID = r'([A-Z]+-P[0-3]-\d{3})'
FULL = re.compile(r'^### Finding ID: ' + ID + r'\s*[-\u2013]\s*(.*?)\s*$')
ROW = re.compile(r'^\|\s*' + ID + r'\s*\|\s*(P[0-3])\s*\|\s*([^|]+?)\s*\|')
ID_ONLY = re.compile(r'[A-Z]+-P[0-3]-\d{3}')

# follow_up_register.md columns -> finding field names (others are ignored).
REGISTER_FIELDS = (("owner", "Owner"), ("target", "Target"),
                   ("status", "Status"), ("note", "Post-audit note"))


def scan_report(path):
    """Extract findings from a report: full-format headings and compact table rows."""
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = FULL.match(line)
        if m:
            out.append({
                "id": m.group(1),
                "severity": m.group(1).split("-")[1],
                "title": m.group(2),
                "report": path.name,
                "line": n,
            })
            continue
        m = ROW.match(line)
        if m:
            out.append({
                "id": m.group(1),
                "severity": m.group(2),
                "title": m.group(3).strip(),
                "report": path.name,
                "line": n,
            })
    return out


def run_reports(run_dir):
    """Reports that carry findings: lens_*.md and NN_*.md (domain reports)."""
    run = pathlib.Path(run_dir)
    return sorted(
        p for p in run.glob("*.md")
        if p.name.startswith("lens_") or re.match(r'^\d+_', p.name)
    )


def register_fields(run_dir):
    """Map finding ID -> dict(owner, target, status, note) from follow_up_register.md.

    Returns {} when the register (or a header carrying Owner/Status) is absent.
    Columns are matched by name, so both register layouts work (with or without
    "Owning prompt/lens"); missing columns/rows yield empty strings.
    """
    path = pathlib.Path(run_dir) / "follow_up_register.md"
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = None
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if "Owner" in cells and "Status" in cells:
            idx = {name: i for i, name in enumerate(cells)}
            break
    if idx is None:
        return {}
    out = {}
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or not ID_ONLY.fullmatch(cells[0] or ""):
            continue
        out[cells[0]] = {
            key: (cells[idx[col]] if col in idx and len(cells) > idx[col] else "")
            for key, col in REGISTER_FIELDS
        }
    return out


def merge_register(findings, run_dir):
    """Attach status/owner/target/note from follow_up_register.md to each finding.

    No register -> no extra fields. Findings not listed in the register get
    empty strings, keeping the finding schema uniform within a run.
    """
    fields = register_fields(run_dir)
    if not fields:
        return
    for f in findings:
        reg = fields.get(f["id"], {})
        for key, _ in REGISTER_FIELDS:
            f[key] = reg.get(key, "")


def collect_with_dupes(run_dir):
    """Return (run_path, ordered_findings, duplicates); first occurrence of an ID wins.

    Findings carry register fields (status/owner/target/note) when the run has a
    follow_up_register.md. duplicates maps finding ID -> list of reports where it
    appears (first report included).
    """
    run = pathlib.Path(run_dir)
    findings = {}
    dupes = {}
    for p in run_reports(run):
        for f in scan_report(p):
            if f["id"] in findings:
                dupes.setdefault(f["id"], [findings[f["id"]]["report"]]).append(p.name)
            else:
                findings[f["id"]] = f
    ordered = sorted(findings.values(), key=lambda f: (f["severity"], f["id"]))
    merge_register(ordered, run)
    return run, ordered, dupes


def collect(run_dir):
    """Return (run_path, ordered_findings); first occurrence of an ID wins."""
    run, ordered, _ = collect_with_dupes(run_dir)
    return run, ordered


def counts(findings):
    by_sev, by_area = {}, {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        area = f["id"].split("-")[0]
        by_area[area] = by_area.get(area, 0) + 1
    return {
        "bySeverity": dict(sorted(by_sev.items())),
        "byArea": dict(sorted(by_area.items())),
        "total": len(findings),
    }


GATES = ("GO", "GO WITH CONDITIONS", "NO-GO")

# A finding with one of these statuses no longer blocks a release/changed-run gate.
# `false-positive` is accepted here even though it is not a run-register status, so
# a future vocabulary change does not silently weaken the gate.
RESOLVED_STATUSES = frozenset({"verified-fixed", "owner-accepted", "false-positive"})


def compute_gate(counts, override=None):
    """Single release-gate decision, shared by full_domain.py and publish_audit.py.

    A P0 can never be released: P0 -> NO-GO, P1 -> GO WITH CONDITIONS, else GO.
    An explicit `override` (one of GATES) wins; an unknown value raises ValueError
    so callers fail closed instead of silently publishing a wrong verdict.
    """
    if override:
        if override not in GATES:
            raise ValueError("gate must be one of: %s" % ", ".join(GATES))
        return override
    sev = counts.get("bySeverity", {}) if isinstance(counts, dict) else {}
    if sev.get("P0", 0) > 0:
        return "NO-GO"
    if sev.get("P1", 0) > 0:
        return "GO WITH CONDITIONS"
    return "GO"
