#!/usr/bin/env python3
"""Org pass control plane for repo-deep-dive.

State machine for an org-wide audit pass. One pass covers many repos and walks each
repo through the standard post-audit pipeline (see runbooks/POST_AUDIT_PIPELINE.md):

    sweep -> deepdive -> publish -> remediate -> merge -> reconcile

State lives at docs/audits/_org/<id>/manifest.json (schema: schemas/org_pass.schema.json)
with a human INDEX.md alongside it. Safe by default: `plan`/`status`/`next` only read
state and print commands; `advance` updates state, and only `advance --execute` runs a
stage's documented commands (every command is logged).

Usage:
  python3 tools/pass.py new --org MaineCyberTech --repos chat,buddy \
      --lenses security,supply-chain,ci [--id 20261004-mainecybertech] [--json]
  python3 tools/pass.py status --id <id> [--json]
  python3 tools/pass.py next   --id <id> [--json]
  python3 tools/pass.py plan   --id <id> [--repo <r>] [--json]
  python3 tools/pass.py advance --id <id> --stage <s> [--repo <r>|--all] \
      [--status done|blocked|in_progress|pending] [--execute] \
      [--branch B] [--sha S] [--source-dir D] [--run R] [--pr N] [--commit SHA] \
      [--patch-set PS-01] [--state merged] [--confirm-merge] [--json]

`advance` without --execute only records state (safe). `advance --execute` runs the
runnable subset of the stage's commands and logs them to
docs/audits/_org/<id>/commands.log; it fails closed and marks the stage `blocked`.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True

PACK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PASSES_ROOT = os.path.join(PACK_ROOT, "docs", "audits", "_org")
RUNS_ROOT = "docs/audits/repo-deep-dive"
SCHEMA_ID = "org_pass/1"
STAGE_ORDER = ["sweep", "deepdive", "publish", "remediate", "merge", "reconcile"]
STATUSES = ["pending", "in_progress", "done", "blocked"]
MANUAL_STAGES = {"deepdive"}  # no shell command to run; driven by the audit agent


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def die(msg):
    print("error: %s" % msg, file=sys.stderr)
    raise SystemExit(2)


def safe_id(pid):
    if not re.match(r"^[A-Za-z0-9._-]+$", pid or ""):
        die("bad pass id %r (allowed: letters, digits, . _ -)" % pid)
    return pid


def pass_dir(pid):
    return os.path.join(PASSES_ROOT, safe_id(pid))


def load(pid):
    path = os.path.join(pass_dir(pid), "manifest.json")
    if not os.path.isfile(path):
        die("pass not found: %s (run `pass.py new` first)" % path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), path


def save(manifest, path):
    manifest["updated_at"] = now()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")


def new_stage():
    return {"status": "pending", "updated_at": now(),
            "evidence": {"run_url": None, "pr_numbers": [], "commit_shas": [], "note": ""}}


def context(manifest, repo, a):
    """Per-repo execution context; placeholders when an input is unknown."""
    pid = manifest["id"]
    return {
        "run": getattr(a, "run", None) or ("%s-%s" % (repo, pid)),
        "branch": getattr(a, "branch", None) or "<default-branch>",
        "sha": getattr(a, "sha", None) or "<sha>",
        "source_dir": getattr(a, "source_dir", None) or "<source-dir>",
        "lenses": manifest.get("lenses", []),
        "patch_set": getattr(a, "patch_set", None),
        "state": getattr(a, "state", None),
    }


def run_name(manifest, repo, ctx=None):
    return (ctx or {}).get("run") or ("%s-%s" % (repo, manifest["id"]))


def stage_commands(manifest, repo, stage, ctx=None):
    """The exact, documented commands for one stage of one repo (strings)."""
    ctx = ctx or context(manifest, repo, argparse.Namespace())
    org = manifest["org"]
    run = run_name(manifest, repo, ctx)
    run_dir = "%s/%s" % (RUNS_ROOT, run)
    branch, sha, source = ctx["branch"], ctx["sha"], ctx["source_dir"]
    ev = manifest["repos"][repo]["stages"][stage]["evidence"]
    prs = [str(p) for p in ev.get("pr_numbers", [])]
    commits = list(ev.get("commit_shas", []))
    lenses = ",".join(ctx["lenses"]) or "security,supply-chain,ci"
    pack = "%s/repo-deep-dive" % org

    if stage == "sweep":
        return [
            "gh workflow run deep-dive-deterministic.yml -R %s -f org=%s -f repos=%s -f deep=true" % (
                pack, org, repo),
            "gh run list -R %s --workflow=deep-dive-deterministic.yml --limit 1 "
            "--json databaseId,url,status" % pack,
        ]
    if stage == "deepdive":
        return [
            "python3 tools/new_run.py --run %s --repo %s --branch %s --sha %s" % (
                run, repo, branch, sha),
            "# agent: run prompts/MASTER_RUNNER_FULL_HARDENING.md for %s (lenses: %s); "
            "write findings.json + FINDINGS.md under %s" % (repo, lenses, run_dir),
        ]
    if stage == "publish":
        return [
            "python3 tools/publish_audit.py --repo %s --branch %s --sha %s "
            "--source-dir %s --run %s --dry-run" % (repo, branch, sha, source, run),
            "python3 tools/publish_audit.py --repo %s --branch %s --sha %s "
            "--source-dir %s --run %s" % (repo, branch, sha, source, run),
            "bash tools/pack_digest.sh",
            "bash tools/lint_pack.sh",
        ]
    if stage == "remediate":
        return [
            "python3 tools/remediation_plan.py %s -o %s/remediation_plan.json "
            "--include-unassigned" % (run_dir, run_dir),
            "# agent: implement each patch set per prompts/REMEDIATION_RUNNER.md; open one "
            "draft PR per patch set (never self-approve)",
        ]
    if stage == "merge":
        audit = prs[0] if prs else "<audit-pr>"
        rem = prs[1] if len(prs) > 1 else "<remediation-pr>"
        return [
            "# requires explicit operator authorization; audit PR first",
            "gh pr ready %s && gh pr merge %s --merge" % (audit, audit),
            "gh pr ready %s && gh pr merge %s --merge" % (rem, rem),
        ]
    if stage == "reconcile":
        commit = commits[0] if commits else "<commit-sha>"
        pr = prs[0] if prs else "<pr-url>"
        ps = ctx.get("patch_set")
        state = ctx.get("state")
        return [
            "python3 tools/remediation_status.py %s --patch-set %s --state %s "
            "--commit %s --pr %s" % (run_dir, ps or "<PS-id>", state or "merged", commit, pr),
            "python3 tools/remediation_status.py %s --status-file <status.json>" % run_dir,
        ]
    die("unknown stage %r" % stage)


def infer_next(manifest):
    """First stage (in order) that is not `done` for every repo."""
    order = manifest.get("stageOrder") or STAGE_ORDER
    for stage in order:
        if any(manifest["repos"][r]["stages"][stage]["status"] != "done"
               for r in manifest["repos"]):
            return stage
    return None


def repo_next(manifest, repo):
    for stage in (manifest.get("stageOrder") or STAGE_ORDER):
        st = manifest["repos"][repo]["stages"][stage]["status"]
        if st != "done":
            return stage if st != "blocked" else "%s (blocked)" % stage
    return None


def runnable(stage, cmd):
    if cmd.strip().startswith("#") or "<" in cmd or ">" in cmd:
        return False
    if stage in MANUAL_STAGES:
        return False
    return True


def execute_stage(manifest, repo, stage, a, log_path):
    ctx = context(manifest, repo, a)
    cmds = stage_commands(manifest, repo, stage, ctx)
    lines = ["# %s %s/%s %s" % (now(), manifest["id"], repo, stage)]
    skipped = False
    for cmd in cmds:
        lines.append("$ %s" % cmd)
        if not runnable(stage, cmd):
            lines.append("# skipped (manual/placeholder): %s" % cmd)
            skipped = True
            continue
        if stage == "merge" and not getattr(a, "confirm_merge", False):
            lines.append("# skipped (merge needs --confirm-merge): %s" % cmd)
            skipped = True
            continue
        print("[pass] $ %s" % cmd)
        r = subprocess.run(cmd, shell=True, cwd=PACK_ROOT, text=True,
                           capture_output=True)
        if r.stdout:
            sys.stdout.write(r.stdout)
            lines.append(r.stdout.rstrip("\n"))
        if r.stderr:
            sys.stderr.write(r.stderr)
            lines.append(r.stderr.rstrip("\n"))
        if r.returncode != 0:
            lines.append("# FAILED (exit %d)" % r.returncode)
            with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines) + "\n")
            return False, skipped
    with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return True, skipped


def render_index(manifest):
    order = manifest.get("stageOrder") or STAGE_ORDER
    head = "| Repo | " + " | ".join(order) + " | Next |"
    sep = "|" + "---|" * (len(order) + 2)
    rows = []
    for repo in sorted(manifest["repos"]):
        cells = []
        for stage in order:
            st = manifest["repos"][repo]["stages"][stage]["status"]
            cells.append({"pending": "-", "in_progress": "~", "done": "x",
                          "blocked": "!"}.get(st, "?"))
        rows.append("| %s | %s | %s |" % (repo, " | ".join(cells), repo_next(manifest, repo) or "complete"))
    nxt = infer_next(manifest) or "complete"
    lines = [
        "# Org pass %s" % manifest["id"], "",
        "- Org: %s" % manifest["org"],
        "- Created: %s" % manifest.get("created_at", ""),
        "- Updated: %s" % manifest.get("updated_at", ""),
        "- Lenses: %s" % ", ".join(manifest.get("lenses", [])),
        "- Stages: `%s`" % " -> ".join(order),
        "- **Next phase: `%s`**" % nxt, "",
        "Legend: `-` pending, `~` in_progress, `x` done, `!` blocked.", "",
        head, sep] + rows + [
        "", "Commands are dry-run first (`tools/pass.py plan --id %s`); merges require explicit"
        % manifest["id"], "operator authorization. See `docs/PASS_CONTROL_PLANE.md`.", ""]
    return "\n".join(lines)


def write_index(manifest):
    path = os.path.join(pass_dir(manifest["id"]), "INDEX.md")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_index(manifest))
    return path


def out(obj, as_json, text):
    if as_json:
        print(json.dumps(obj, indent=2))
    else:
        print(text)


def summary(manifest):
    return {
        "id": manifest["id"], "org": manifest["org"],
        "next_stage": infer_next(manifest),
        "repos": {r: {"next_stage": repo_next(manifest, r),
                      "stages": {s: manifest["repos"][r]["stages"][s]["status"]
                                 for s in (manifest.get("stageOrder") or STAGE_ORDER)}}
                  for r in sorted(manifest["repos"])},
    }


# --- subcommands -----------------------------------------------------------------

def cmd_new(a):
    pid = a.id or ("%s-%s" % (datetime.now(timezone.utc).strftime("%Y%m%d"),
                              re.sub(r"[^a-z0-9-]", "", a.org.lower()) or "org"))
    pid = safe_id(pid)
    d = pass_dir(pid)
    if os.path.isdir(d) and os.listdir(d):
        die("refusing to touch non-empty pass dir: %s" % d)
    repos = [r.strip() for r in a.repos.split(",") if r.strip()]
    if not repos:
        die("--repos is empty")
    lenses = [x.strip() for x in a.lenses.split(",") if x.strip()]
    manifest = {
        "schema": SCHEMA_ID,
        "id": pid,
        "org": a.org,
        "created_at": now(),
        "updated_at": now(),
        "created_by": "tools/pass.py",
        "lenses": lenses,
        "stageOrder": STAGE_ORDER,
        "repos": {r: {"default_branch": "", "audit_run": None,
                      "stages": {s: new_stage() for s in STAGE_ORDER}}
                  for r in repos},
        "notes": ["Draft scaffolding only: no commands run. Plan first, execute last."],
    }
    save(manifest, os.path.join(d, "manifest.json"))
    write_index(manifest)
    if a.json:
        print(json.dumps(summary(manifest), indent=2))
    else:
        print("created pass %s" % d)
        print("manifest: %s" % os.path.join(d, "manifest.json"))
        print("INDEX:    %s" % os.path.join(d, "INDEX.md"))
        print("next: python3 tools/pass.py plan --id %s" % pid)


def cmd_status(a):
    manifest, _ = load(a.id)
    if a.json:
        print(json.dumps(summary(manifest), indent=2))
        return
    s = summary(manifest)
    print("pass %s (%s)  next stage: %s" % (s["id"], s["org"], s["next_stage"] or "complete"))
    for repo in sorted(manifest["repos"]):
        states = " ".join("%s=%s" % (st, manifest["repos"][repo]["stages"][st]["status"])
                          for st in STAGE_ORDER)
        print("  %-24s %s" % (repo, states))


def cmd_next(a):
    manifest, _ = load(a.id)
    nxt = infer_next(manifest)
    if a.json:
        print(json.dumps({"id": manifest["id"], "next_stage": nxt,
                          "repos": {r: repo_next(manifest, r) for r in sorted(manifest["repos"])}},
                         indent=2))
        return
    if not nxt:
        print("pass %s: complete" % manifest["id"])
        return
    print("pass %s: next stage = %s" % (manifest["id"], nxt))
    for repo in sorted(manifest["repos"]):
        print("  %-24s %s" % (repo, repo_next(manifest, repo)))


def cmd_plan(a):
    manifest, _ = load(a.id)
    nxt = infer_next(manifest)
    repos = [a.repo] if a.repo else sorted(manifest["repos"])
    if a.repo and a.repo not in manifest["repos"]:
        die("repo %r not in pass %s" % (a.repo, manifest["id"]))
    plan = []
    for repo in repos:
        stage = repo_next(manifest, repo)
        stage = (stage or "").split(" ")[0] or nxt
        cmds = stage_commands(manifest, repo, stage)
        plan.append({"repo": repo, "stage": stage, "commands": cmds})
    if a.json:
        print(json.dumps({"id": manifest["id"], "next_stage": nxt, "plan": plan}, indent=2))
        return
    print("pass %s (%s) - plan for next phase: %s" % (manifest["id"], manifest["org"], nxt))
    print("(dry-run only: nothing is executed)\n")
    for entry in plan:
        print("## %s -> %s" % (entry["repo"], entry["stage"]))
        for cmd in entry["commands"]:
            print("  %s" % cmd)
        print()


def cmd_advance(a):
    manifest, path = load(a.id)
    if a.stage not in STAGE_ORDER:
        die("--stage must be one of: %s" % ", ".join(STAGE_ORDER))
    if a.repo:
        if a.repo not in manifest["repos"]:
            die("repo %r not in pass %s" % (a.repo, manifest["id"]))
        repos = [a.repo]
    else:
        repos = sorted(manifest["repos"])
    status = a.status or "done"

    if a.execute:
        log_path = os.path.join(pass_dir(a.id), "commands.log")
        results = {}
        for repo in repos:
            ok, skipped = execute_stage(manifest, repo, a.stage, a, log_path)
            results[repo] = "done" if (ok and not skipped) else ("blocked" if not ok else "in_progress")
        status = a.status or None
        for repo in repos:
            manifest["repos"][repo]["stages"][a.stage]["status"] = status or results[repo]
            manifest["repos"][repo]["stages"][a.stage]["updated_at"] = now()
            if a.note:
                manifest["repos"][repo]["stages"][a.stage]["evidence"]["note"] = a.note
        save(manifest, path)
        write_index(manifest)
        if a.json:
            print(json.dumps({"id": manifest["id"], "stage": a.stage, "results": results}, indent=2))
        else:
            print("pass %s: stage %s -> %s" % (manifest["id"], a.stage,
                                               ", ".join("%s=%s" % (r, results[r]) for r in repos)))
            print("commands logged: %s" % log_path)
        if any(v == "blocked" for v in results.values()):
            raise SystemExit(1)
        return

    if status not in STATUSES:
        die("--status must be one of: %s" % ", ".join(STATUSES))
    for repo in repos:
        st = manifest["repos"][repo]["stages"][a.stage]
        st["status"] = status
        st["updated_at"] = now()
        ev = st["evidence"]
        if a.run_url:
            ev["run_url"] = a.run_url
        if a.pr:
            ev["pr_numbers"] += [int(x) if x.isdigit() else x for x in a.pr]
        if a.commit:
            ev["commit_shas"] += a.commit
        if a.note:
            ev["note"] = a.note
    save(manifest, path)
    write_index(manifest)
    if a.json:
        print(json.dumps(summary(manifest), indent=2))
    else:
        print("pass %s: %s -> %s for %s" % (manifest["id"], a.stage, status, ", ".join(repos)))
        print("INDEX updated: %s" % os.path.join(pass_dir(a.id), "INDEX.md"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new")
    p.add_argument("--org", required=True)
    p.add_argument("--repos", required=True, help="comma-separated repo names")
    p.add_argument("--lenses", default="security,supply-chain,ci")
    p.add_argument("--id", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_new)

    for name, fn in (("status", cmd_status), ("next", cmd_next)):
        p = sub.add_parser(name)
        p.add_argument("--id", required=True)
        p.add_argument("--json", action="store_true")
        p.set_defaults(fn=fn)

    p = sub.add_parser("plan")
    p.add_argument("--id", required=True)
    p.add_argument("--repo", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("advance")
    p.add_argument("--id", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--repo", default=None, help="one repo (default: all repos in the pass)")
    p.add_argument("--status", default=None, choices=STATUSES)
    p.add_argument("--execute", action="store_true", help="run the stage's documented commands")
    p.add_argument("--run-url", dest="run_url", default=None)
    p.add_argument("--pr", action="append", default=[], help="PR number/url (repeatable)")
    p.add_argument("--commit", action="append", default=[], help="commit SHA (repeatable)")
    p.add_argument("--note", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--sha", default=None)
    p.add_argument("--source-dir", dest="source_dir", default=None)
    p.add_argument("--run", default=None)
    p.add_argument("--patch-set", dest="patch_set", default=None)
    p.add_argument("--state", default=None)
    p.add_argument("--confirm-merge", dest="confirm_merge", action="store_true",
                   help="required for any merge-stage execution")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_advance)

    a = ap.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
