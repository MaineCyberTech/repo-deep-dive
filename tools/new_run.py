#!/usr/bin/env python3
"""Scaffold a new repo-deep-dive run folder (Wave 0).

Creates <root>/<name>/<run>/ with an INDEX.md skeleton and an
audit_manifest.json seeded from the pack's example manifest, so a new repo
(or a new audit of a known repo) starts from a valid, checkable skeleton.

Usage:
  python3 tools/new_run.py --run YYYYMMDD-HHMM-branch-sha [--name repo-deep-dive]
                           [--root docs/audits] [--profile base|falcon-lab]
                           [--repo PATH] [--branch B] [--sha S]

Refuses to touch a non-empty directory. Writes only the new run folder.
Run from anywhere; the pack root is resolved from this script's location.
"""

import argparse
import datetime
import json
import os
import sys

sys.dont_write_bytecode = True

PACK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

EXAMPLES = {
    "base": "examples/audit_manifest.example.json",
    "falcon-lab": "examples/audit_manifest.falcon-lab.example.json",
}

RUNNERS = {
    "base": "prompts/MASTER_RUNNER_FULL_HARDENING.md",
    "falcon-lab": "prompts/MASTER_RUNNER_FALCON_LAB.md",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True,
                    help="run name, e.g. YYYYMMDD-HHMM-branch-sha (fallback YYYYMMDD-HHMM-manual)")
    ap.add_argument("--name", default="repo-deep-dive", help="audit name")
    ap.add_argument("--root", default="docs/audits",
                    help="audit root (run folder is <root>/<name>/<run>/)")
    ap.add_argument("--profile", default="base", choices=sorted(EXAMPLES),
                    help="seed manifest from this profile example")
    ap.add_argument("--repo", default="", help="target repo path (recorded in INDEX)")
    ap.add_argument("--branch", default="", help="target branch (recorded in INDEX)")
    ap.add_argument("--sha", default="", help="target commit SHA (recorded in INDEX)")
    args = ap.parse_args()

    if "/" in args.run or "\\" in args.run or args.run in (".", ".."):
        print("error: --run must be a plain directory name", file=sys.stderr)
        raise SystemExit(2)

    run_dir = os.path.join(args.root, args.name, args.run)
    if os.path.exists(run_dir) and os.listdir(run_dir):
        print("error: refusing to touch non-empty directory: %s" % run_dir,
              file=sys.stderr)
        raise SystemExit(2)
    os.makedirs(run_dir, exist_ok=True)

    with open(os.path.join(PACK_ROOT, EXAMPLES[args.profile]),
              encoding="utf-8") as fh:
        manifest = json.load(fh)
    manifest["run"] = args.run
    manifest["scaffolded_at"] = datetime.datetime.now(
        datetime.timezone.utc).isoformat()
    manifest["scaffolded_by"] = "tools/new_run.py"
    with open(os.path.join(run_dir, "audit_manifest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    order = manifest.get("executionOrder", [])
    rows = "\n".join(
        "| %d | %s | pending |" % (n, f) for n, f in enumerate(order, 1))
    index = """# Audit Run Index

## Metadata

- Name: %s
- Run: %s
- Profile: %s
- Target repo: %s
- Branch: %s
- Commit: %s
- Generated: %s

## Reports

| Order | Report | Status |
|---:|---|---|
%s

## Key Outputs

- Executive summary: pending
- Risk register: pending
- Roadmap: pending
- Patch plan: pending
- Release gate: pending

## Top Risks

pending (prompt 22)

## Next Actions

1. Take a repo inventory: `python3 tools/repo_inventory.py <repo> -o /tmp/inventory.json`
2. Paste `%s` into the audit agent.
3. Validate when done: `python3 tools/run_toolchain.py %s --write --dashboard`
""" % (args.name, args.run, args.profile, args.repo or "tbd",
       args.branch or "tbd", args.sha or "tbd",
       datetime.datetime.now(datetime.timezone.utc).isoformat(),
       rows or "| - | (no execution order in seed manifest) | pending |",
       RUNNERS[args.profile], run_dir)
    with open(os.path.join(run_dir, "INDEX.md"), "w",
              encoding="utf-8") as fh:
        fh.write(index)

    print("created %s" % run_dir)
    print("manifest: audit_manifest.json (seed: %s)" % EXAMPLES[args.profile])
    print("next: paste %s into the audit agent" % RUNNERS[args.profile])


if __name__ == "__main__":
    main()
