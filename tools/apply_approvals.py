#!/usr/bin/env python3
"""Apply repo approvals from a declarative `approvals.yml` (approvals-as-code).

Idempotent; **dry-run by default**. `--apply` writes. Verify afterwards with
`tools/repo_approvals.py`. Only controls GitHub exposes via API are applied; anything else is
reported as `NEEDS-HUMAN` rather than faked.

approvals.yml:
  repos:
    MaineCyberTech/chat:
      branch: develop
      required_checks: ["foundation"]
      strict: true
      required_reviews: 0
      enforce_admins: false
      environments:
        production: { reviewers: ["JulianB-MCT"] }

Usage:
  tools/apply_approvals.py --file approvals.yml [--apply]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

try:
    import yaml
except ImportError:
    print("error: PyYAML required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

API = "https://api.github.com"


def api(method, path, body=None, token=""):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
        "Content-Type": "application/json", "User-Agent": "repo-deep-dive-apply-approvals"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]


def user_id(login, token):
    code, doc = api("GET", "/users/%s" % login, token=token)
    return doc.get("id") if code == 200 and isinstance(doc, dict) else None


def current_checks(owner, repo, branch, token):
    code, doc = api("GET", "/repos/%s/%s/branches/%s/protection" % (owner, repo, branch), token=token)
    if code == 200 and isinstance(doc, dict):
        sc = doc.get("required_status_checks") or {}
        return sc.get("contexts") or []
    return []


def apply_repo(full, cfg, token, do_apply):
    owner, repo = full.split("/", 1)
    branch = cfg.get("branch", "main")
    checks = cfg.get("required_checks", [])
    strict = cfg.get("strict", True)
    reviews = int(cfg.get("required_reviews", 0) or 0)
    enforce = bool(cfg.get("enforce_admins", False))

    have = current_checks(owner, repo, branch, token)
    missing = [c for c in checks if c not in have]
    print("[%s@%s] checks now=%s wanted=%s missing=%s" % (full, branch, have, checks, missing))

    body = {
        "required_status_checks": {"strict": strict, "contexts": checks} if checks else None,
        "enforce_admins": enforce,
        "required_pull_request_reviews": ({"required_approving_review_count": reviews} if reviews else None),
        "restrictions": None,
    }
    if do_apply and (missing or reviews):
        code, resp = api("PUT", "/repos/%s/%s/branches/%s/protection" % (owner, repo, branch), body, token)
        print("  PUT branch protection -> HTTP %s%s" % (code, "" if code in (200, 201) else " %s" % resp))

    for env, ecfg in (cfg.get("environments") or {}).items():
        reviewers = []
        for login in (ecfg or {}).get("reviewers", []) or []:
            uid = user_id(login, token)
            if uid:
                reviewers.append({"type": "User", "id": uid})
            else:
                print("  NEEDS-HUMAN: reviewer %s not resolvable" % login)
        ebody = {"reviewers": reviewers} if reviewers else {}
        print("  env %s reviewers=%s" % (env, [r["id"] for r in reviewers]))
        if do_apply and reviewers:
            code, resp = api("PUT", "/repos/%s/%s/environments/%s" % (owner, repo, env), ebody, token)
            print("    PUT environment -> HTTP %s%s" % (code, "" if code in (200, 201) else " %s" % resp))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default="approvals.yml")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    a = ap.parse_args()
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("error: GH_TOKEN not set", file=sys.stderr)
        return 2
    if not os.path.isfile(a.file):
        print("error: %s not found" % a.file, file=sys.stderr)
        return 2
    doc = yaml.safe_load(open(a.file, encoding="utf-8")) or {}
    repos = doc.get("repos") or {}
    print("=== apply_approvals (%s) ===" % ("APPLY" if a.apply else "DRY-RUN"))
    for full, cfg in repos.items():
        apply_repo(full, cfg or {}, token, a.apply)
    print("done. Verify with tools/repo_approvals.py --repos <...>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
