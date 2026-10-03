#!/usr/bin/env python3
"""Compile a machine-readable remediation plan from a completed audit run.

Reads the run's `patch_plan.md` (patch-set mapping table + validation commands) and
optional `findings.json`, and writes `remediation_plan.json`:

{
  "run", "repo", "generated",
  "patchSets": [
    { "id": "PS-01", "title", "severity", "findings": [...], "files": [...],
      "dependsOn": [...], "effort", "verification": [...],
      "branch": "remediation/PS-01-<run>" }
  ],
  "unassignedFindings": [...]
}

Usage:
  tools/remediation_plan.py <run-folder> [-o remediation_plan.json] [--json]

If the run already contains a valid `remediation_plan.json`, it is validated and echoed.
Read-only against the repo; only the plan output is written.
"""

import argparse
import datetime
import json
import os
import re
import sys

sys.dont_write_bytecode = True

FINDING = re.compile(r"\b([A-Z]+-P[0-3]-\d{3})\b")
SHORT = re.compile(r"([A-Z]+-P[0-3]-)(\d{3})((?:/\d{3})+)")
PS_ID = re.compile(r"\bPS-?\d{1,3}\b", re.I)
BACKTICK = re.compile(r"`([^`]+)`")


def expand_findings(text):
    """Expand finding IDs including shorthand like `SEC-P1-003/004/005` -> 3 IDs."""
    ids = FINDING.findall(text)
    for m in SHORT.finditer(text):
        prefix, first, rest = m.group(1), m.group(2), m.group(3)
        for n in [first] + re.findall(r"\d{3}", rest):
            ids.append(prefix + n)
    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_patch_table(md):
    """Return list of dicts from the patch-set mapping table."""
    out = []
    lines = md.splitlines()
    for i, ln in enumerate(lines):
        if "|" not in ln or "Findings" not in ln or "Files" not in ln:
            continue
        header = [c.lower() for c in cells(ln)]
        # find header indices
        def idx(*names):
            for n in names:
                for j, h in enumerate(header):
                    if n in h:
                        return j
            return None
        i_set, i_title, i_find, i_files = idx("set"), idx("title"), idx("finding"), idx("file")
        i_dep, i_eff, i_ver = idx("depend"), idx("effort"), idx("verif")
        if i_find is None or i_set is None:
            continue
        for row in lines[i + 1:]:
            if "|" not in row:
                break
            c = cells(row)
            if len(c) <= i_set or not PS_ID.search(c[i_set]):
                continue
            ps = {
                "id": c[i_set].upper().replace("PS", "PS-").replace("PS--", "PS-"),
                "title": c[i_title] if i_title is not None and len(c) > i_title else "",
                "findings": expand_findings(c[i_find]) if len(c) > i_find else [],
                "files": BACKTICK.findall(c[i_files]) if i_files is not None and len(c) > i_files else [],
                "dependsOn": [] if i_dep is None or len(c) <= i_dep else
                             [x.upper() for x in FINDING.findall(c[i_dep])] or
                             [x.upper() for x in re.findall(r"PS-?\d{1,3}", c[i_dep], re.I)],
                "effort": c[i_eff] if i_eff is not None and len(c) > i_eff else "",
                "verificationText": c[i_ver] if i_ver is not None and len(c) > i_ver else "",
            }
            if "—" in ps["dependsOn"] or "–" in ps["dependsOn"]:
                ps["dependsOn"] = []
            out.append(ps)
        break
    return out


def parse_validation_table(md):
    """Return {set_id: [commands]} from a 'Validation commands' table."""
    out = {}
    lines = md.splitlines()
    for i, ln in enumerate(lines):
        if "|" not in ln:
            continue
        low = ln.lower()
        if "command" in low and ("set" in low or "ps-" in low):
            for row in lines[i + 1:]:
                if "|" not in row:
                    break
                c = cells(row)
                if len(c) < 2:
                    continue
                m = PS_ID.search(c[0])
                if not m:
                    continue
                raw = c[1].strip().strip("`")
                cmds = [x.strip().strip("`").strip() for x in re.split(r";|&&", raw)]
                out[m.group(0).upper()] = [x for x in cmds if x]
            break
    return out


HEADING_RE = re.compile(
    r"^#{2,4}\s+((?:PATCH|PS)[-\s]?\d{1,3}|P\d[-\s]\d{1,2})\b[\s:.\-\u2013\u2014]*(.*)$", re.I)
BULLET = re.compile(r"^\s*[-*]\s*([A-Za-z][A-Za-z /]*?)\s*:\s*(.*)$")
ID_TOKEN = re.compile(r"PATCH-\d{1,3}|PS-?\d{1,3}|P\d-\d{1,2}", re.I)


def parse_heading_sets(md):
    """Parse heading-based patch sets (PATCH-01 / PS-01 / P1-1 with Files:/Closes:/Validate: bullets)."""
    out, cur = [], None
    for ln in md.splitlines():
        m = HEADING_RE.match(ln)
        if m:
            if cur:
                out.append(cur)
            cur = {"id": m.group(1).upper().replace(" ", "-"), "title": m.group(2).strip(),
                   "findings": expand_findings(ln), "files": [], "dependsOn": [],
                   "effort": "", "verificationText": "", "_block": []}
            continue
        if cur is not None:
            cur["_block"].append(ln)
            b = BULLET.match(ln)
            if b:
                key, val = b.group(1).strip().lower(), b.group(2)
                if key.startswith("file"):
                    cur["files"] += BACKTICK.findall(val)
                elif key.startswith(("closes", "fixes", "finding")):
                    cur["findings"] += expand_findings(val)
                elif key.startswith(("validation", "validate", "verify")):
                    cur["verificationText"] = val
                elif key.startswith("effort"):
                    cur["effort"] = val.strip()
                elif key.startswith(("depends", "prereq")):
                    cur["dependsOn"] = [x.upper() for x in ID_TOKEN.findall(val)]
    if cur:
        out.append(cur)
    for ps in out:
        seen, f = set(), []
        for x in ps["findings"]:
            if x not in seen:
                seen.add(x)
                f.append(x)
        ps["findings"] = f
        if not ps["files"]:
            block = "\n".join(ps["_block"])
            ps["files"] = [p for p in BACKTICK.findall(block) if "/" in p or "." in p][:20]
        ps.pop("_block", None)
    return out


def parse_patch_sets(md):
    """Prefer the table form; fall back to heading-based patch sets."""
    sets = parse_patch_table(md)
    if sets:
        return sets
    return parse_heading_sets(md)


def sev_rank(s):
    return {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(s, 9)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--json", action="store_true", help="print the plan JSON to stdout")
    args = ap.parse_args()

    run = os.path.abspath(args.run_dir)
    if not os.path.isdir(run):
        print("error: not a directory: %s" % run, file=sys.stderr)
        raise SystemExit(2)

    out_path = args.output or os.path.join(run, "remediation_plan.json")
    if os.path.exists(out_path):
        try:
            doc = json.load(open(out_path, encoding="utf-8"))
            if doc.get("patchSets"):
                print("existing remediation_plan.json is valid (%d patch sets); echoing"
                      % len(doc["patchSets"]))
                if args.json:
                    print(json.dumps(doc, indent=2))
                return
        except Exception:
            pass

    plan_md = os.path.join(run, "patch_plan.md")
    if not os.path.isfile(plan_md):
        print("error: no patch_plan.md in %s" % run, file=sys.stderr)
        raise SystemExit(2)
    md = open(plan_md, encoding="utf-8", errors="replace").read()

    findings = {}
    fj = os.path.join(run, "findings.json")
    if os.path.isfile(fj):
        try:
            for f in json.load(open(fj, encoding="utf-8")).get("findings", []):
                findings[f["id"]] = f
        except Exception:
            pass

    patch_sets = parse_patch_sets(md)
    commands = parse_validation_table(md)

    assigned = set()
    for ps in patch_sets:
        assigned.update(ps["findings"])
        if ps["id"] in commands:
            ps["verification"] = commands[ps["id"]]
        else:
            ps["verification"] = [ps["verificationText"]] if ps["verificationText"] else []
        sevs = [findings.get(fid, {}).get("severity") or fid.split("-")[1]
                for fid in ps["findings"]]
        ps["severity"] = min(sevs, key=sev_rank) if sevs else ""
        ps["branch"] = "remediation/%s-%s" % (ps["id"], os.path.basename(run))

    unassigned = sorted(set(findings) - assigned)
    repo = ""
    m = re.search(r"Repository:\s*`([^`]+)`", md) or re.search(r"Repo:\s*`([^`]+)`", md)
    if m:
        repo = m.group(1)

    doc = {
        "run": os.path.basename(run),
        "repo": repo,
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "patchSets": patch_sets,
        "unassignedFindings": unassigned,
    }
    open(out_path, "w", encoding="utf-8").write(json.dumps(doc, indent=2) + "\n")

    print("run: %s" % doc["run"])
    print("patch sets: %d" % len(patch_sets))
    for ps in patch_sets:
        print("  %s [%s] %s — %d finding(s), %d file(s), verify: %s" % (
            ps["id"], ps["severity"] or "?", ps["title"], len(ps["findings"]),
            len(ps["files"]), "; ".join(ps["verification"]) or "—"))
    if unassigned:
        print("unassigned findings: %s" % ", ".join(unassigned))
    print("wrote %s" % out_path)
    if args.json:
        print(json.dumps(doc, indent=2))


if __name__ == "__main__":
    main()
