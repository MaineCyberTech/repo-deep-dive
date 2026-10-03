#!/usr/bin/env python3
"""Client for the Proxmox lab job API (POST /run) used by repo-deep-dive.

Sends a shell command to the ci-runner or edge-builder and returns its exit/stdout/stderr.

Usage:
  tools/lab_runner.py --url http://172.23.128.51:8722 --token <t> [--repo chat] --command "corepack pnpm test"
  tools/lab_runner.py --url ... --token-file /path/to/token --cwd /srv/work/chat --command "..."

Exit code mirrors the remote command's exit (0 ok). --json prints the raw response.
The token also reads from $LAB_API_TOKEN when --token is omitted.
"""

import argparse
import json
import os
import sys
import urllib.request

sys.dont_write_bytecode = True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True, help="lab API base, e.g. http://172.23.128.51:8722")
    ap.add_argument("--token", default=os.environ.get("LAB_API_TOKEN", ""))
    ap.add_argument("--token-file", default=None)
    ap.add_argument("--repo", default=None, help="repo under the lab root (e.g. chat)")
    ap.add_argument("--cwd", default=None, help="absolute working dir (overrides --repo)")
    ap.add_argument("--command", required=True)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    token = a.token
    if a.token_file and os.path.isfile(a.token_file):
        token = open(a.token_file, encoding="utf-8").read().strip()
    if not token:
        print("error: no token (--token, --token-file, or $LAB_API_TOKEN)", file=sys.stderr)
        return 2

    payload = json.dumps({"repo": a.repo, "cwd": a.cwd, "command": a.command,
                          "timeout": a.timeout}).encode()
    req = urllib.request.Request(
        a.url.rstrip("/") + "/run", data=payload,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=a.timeout + 30))
    except Exception as e:
        print("lab request failed: %s" % e, file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps(res, indent=2))
    else:
        sys.stdout.write(res.get("stdout", ""))
        if res.get("stderr"):
            sys.stderr.write(res["stderr"])
        print("[exit=%s duration=%ss cwd=%s]" % (res.get("exit"), res.get("duration"), res.get("cwd")))
    return 0 if res.get("exit") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
