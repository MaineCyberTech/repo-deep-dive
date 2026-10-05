#!/usr/bin/env python3
"""Client for the Proxmox lab job API used by repo-deep-dive.

Modes (one per invocation):
  run     Send a shell command to the ci-runner/edge-builder, in a repo workspace.
  sync    Clone/fetch an org repo into the lab workspace and report its HEAD.
  repos   List git workspaces already present on the lab.

Usage:
  # run a command in an already-synced repo workspace
  tools/lab_runner.py --url http://192.168.222.201:8722 --token <t> --repo chat \
      --command "corepack pnpm test"
  # sync (clone/fetch) a repo, then run against it
  tools/lab_runner.py --url ... --token <t> --sync --repo snowride \
      --org MaineCyberTech --ref main --github-token <pat>
  tools/lab_runner.py --url ... --token <t> --repos

Exit code mirrors the remote command's exit (0 ok). --json prints the raw response.
The token also reads from $LAB_API_TOKEN when --token is omitted; the GitHub token
for --sync reads from $LAB_GITHUB_TOKEN when --github-token is omitted.
"""

import argparse
import json
import os
import sys
import urllib.request

sys.dont_write_bytecode = True


def call(url, token, path, payload=None, timeout=1800):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url.rstrip("/") + path, data=data,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def preflight(url, token, timeout=10):
    """True iff the lab API reports healthy, i.e. lab access is set up and verified.

    Runs before any work is dispatched to the lab (run/sync), so a broken overlay or a
    down lab fails closed instead of queueing/half-sending jobs."""
    try:
        res = call(url, token, "/health", timeout=timeout)
        return str(res.get("status", "")).lower() == "ok"
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="lab API base, e.g. http://172.23.128.51:8722")
    ap.add_argument("--token", default=os.environ.get("LAB_API_TOKEN", ""))
    ap.add_argument("--token-file", default=None)
    ap.add_argument("--repo", default=None, help="repo under the lab root (e.g. chat)")
    ap.add_argument("--cwd", default=None, help="absolute working dir (overrides --repo)")
    ap.add_argument("--command", default=None, help="shell command to run (run mode)")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--sync", action="store_true", help="clone/fetch a repo into the lab workspace")
    ap.add_argument("--repos", action="store_true", help="list lab workspaces and exit")
    ap.add_argument("--org", default="MaineCyberTech", help="GitHub org for --sync")
    ap.add_argument("--ref", default="", help="branch/tag/SHA for --sync")
    ap.add_argument("--github-token", default=os.environ.get("LAB_GITHUB_TOKEN", ""))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-preflight", action="store_true",
                    help="skip the lab health preflight before dispatching work (not recommended)")
    a = ap.parse_args()

    token = a.token
    if a.token_file and os.path.isfile(a.token_file):
        token = open(a.token_file, encoding="utf-8").read().strip()
    if not token:
        print("error: no token (--token, --token-file, or $LAB_API_TOKEN)", file=sys.stderr)
        return 2

    try:
        # Fail closed: verify lab access before dispatching any work (run/sync).
        if not a.repos and not a.no_preflight and not preflight(a.url, token):
            print("error: lab preflight failed (%s/health not ok); refusing to dispatch work. "
                  "Set up/verify lab access (docs/LAB_VPN.md) or pass --no-preflight."
                  % a.url.rstrip("/"), file=sys.stderr)
            return 3

        if a.repos:
            res = call(a.url, token, "/repos", timeout=60)
            if a.json:
                print(json.dumps(res, indent=2))
            else:
                for r in res.get("repos", []):
                    print("%-20s %s %s%s" % (r["repo"], (r.get("head") or "")[:10],
                                             r.get("branch", ""),
                                             " (dirty)" if r.get("dirty") else ""))
            return 0

        if a.sync:
            if not a.repo:
                print("error: --sync requires --repo", file=sys.stderr)
                return 2
            res = call(a.url, token, "/sync",
                       {"repo": a.repo, "org": a.org, "ref": a.ref,
                        "token": a.github_token}, timeout=a.timeout + 120)
            if a.json:
                print(json.dumps(res, indent=2))
            else:
                print("synced %s @ %s (%s) -> %s" % (res.get("repo"), (res.get("head") or "")[:10],
                                                     res.get("branch"), res.get("cwd")))
            return 0 if res.get("exit") == 0 else 1

        if not a.command:
            print("error: --command required (or use --sync/--repos)", file=sys.stderr)
            return 2
        res = call(a.url, token, "/run",
                   {"repo": a.repo, "cwd": a.cwd, "command": a.command,
                    "timeout": a.timeout}, timeout=a.timeout + 30)
        if a.json:
            print(json.dumps(res, indent=2))
        else:
            sys.stdout.write(res.get("stdout", ""))
            if res.get("stderr"):
                sys.stderr.write(res["stderr"])
            print("[exit=%s duration=%ss cwd=%s]" % (res.get("exit"), res.get("duration"),
                                                     res.get("cwd")))
        return 0 if res.get("exit") == 0 else 1
    except Exception as e:
        print("lab request failed: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
