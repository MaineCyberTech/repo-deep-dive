#!/usr/bin/env python3
"""Confirm the approvals/permissions of the repos an agent will work on.

Part of the standard agent setup (see runbooks/AGENT_SETUP.md): after setting up the pack and
the lab connection, confirm each local repo's approvals and RECORD what was done - especially
for controls that cannot be set from code (branch protection, required checks, environment
reviewers, tag rules). Read-only; never fakes a control.

Checks per repo: default-branch protection (required status checks, required reviews,
enforce-admins), environments with required reviewers, and the presence of required
secret/variable names. Requires a token with repo admin to read protection.

Usage:
  tools/repo_approvals.py --repos chat,buddy,falcon [--org MaineCyberTech]
      [--required-check "Lab preflight / lab"] [--secret LAB_ENDPOINT_SSH_KEY]
      [--write docs/REPO_APPROVALS.md] [--json out.json]

Exit 0 unless a repo is unreachable; and prints a CONFIRMED / MISSING / NEEDS-HUMAN summary.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"


def api(path, token):
    req = urllib.request.Request(API + path, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-deep-dive-approvals"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # noqa: BLE001
        return 0, {"_error": str(e)}


def names(path, token, key):
    code, doc = api(path, token)
    if code == 200 and isinstance(doc, dict):
        return sorted(x.get("name", "") for x in doc.get(key, []))
    return None


def check_repo(org, repo, token, required_check=None, required_secret=None):
    r = {"repo": "%s/%s" % (org, repo), "findings": {}}
    code, doc = api("/repos/%s/%s" % (org, repo), token)
    if code != 200 or not doc:
        r["findings"]["repo"] = "MISSING (unreachable: HTTP %s)" % code
        return r
    r["default_branch"] = doc.get("default_branch", "main")
    r["archived"] = doc.get("archived", False)
    br = r["default_branch"]

    code, prot = api("/repos/%s/%s/branches/%s/protection" % (org, repo, br), token)
    if code == 404:
        r["findings"]["branch_protection"] = "MISSING (no protection on %s) -> NEEDS-HUMAN" % br
    elif code != 200 or prot is None:
        r["findings"]["branch_protection"] = "NEEDS-HUMAN (cannot read: HTTP %s)" % code
    else:
        sc = prot.get("required_status_checks") or {}
        contexts = sc.get("contexts") or []
        reviews = prot.get("required_pull_request_reviews") or None
        admins = (prot.get("enforce_admins") or {}).get("enabled", False)
        bits = []
        if contexts:
            bits.append("checks=%s" % ",".join(contexts))
        else:
            bits.append("checks=none")
        bits.append("reviews=%s" % (reviews.get("required_approving_review_count", 0) if reviews else 0))
        bits.append("enforce_admins=%s" % admins)
        r["findings"]["branch_protection"] = "CONFIRMED (%s)" % " ".join(bits)
        if required_check:
            r["findings"]["required_check:%s" % required_check] = (
                "CONFIRMED" if required_check in contexts else "MISSING -> NEEDS-HUMAN")

    envs = None
    code, edoc = api("/repos/%s/%s/environments" % (org, repo), token)
    if code == 200 and isinstance(edoc, dict):
        envs = []
        for e in edoc.get("environments", []):
            rules = [p.get("type") for p in (e.get("protection_rules") or [])]
            envs.append("%s(%s)" % (e.get("name"), ",".join(rules) or "none"))
        r["environments"] = envs
        r["findings"]["environments"] = ("CONFIRMED (%s)" % "; ".join(envs)) if envs else "MISSING (none)"
    else:
        r["findings"]["environments"] = "NEEDS-HUMAN (cannot read: HTTP %s)" % code

    secrets = names("/repos/%s/%s/actions/secrets" % (org, repo), token, "secrets")
    r["secrets"] = secrets
    if required_secret:
        r["findings"]["secret:%s" % required_secret] = (
            "CONFIRMED" if (secrets and required_secret in secrets)
            else "MISSING -> NEEDS-HUMAN" if secrets is not None else "NEEDS-HUMAN (cannot read)")
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", default="MaineCyberTech")
    ap.add_argument("--repos", required=True, help="comma-separated repo names")
    ap.add_argument("--required-check", default=None)
    ap.add_argument("--secret", action="append", default=[], help="secret name that must exist (repeatable)")
    ap.add_argument("--write", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("error: GH_TOKEN not set", file=sys.stderr)
        return 2

    results = []
    for repo in [x.strip() for x in a.repos.split(",") if x.strip()]:
        r = check_repo(a.org, repo, token, a.required_check, a.secret[0] if a.secret else None)
        for extra in a.secret[1:]:
            secrets = names("/repos/%s/%s/actions/secrets" % (a.org, repo), token, "secrets")
            r["findings"]["secret:%s" % extra] = ("CONFIRMED" if secrets and extra in secrets
                                                  else "MISSING -> NEEDS-HUMAN" if secrets is not None
                                                  else "NEEDS-HUMAN (cannot read)")
        results.append(r)

    lines = ["# Repo approvals confirmation", "",
             "Generated %s by `tools/repo_approvals.py` (agent setup). "
             "MISSING/NEEDS-HUMAN items are controls that cannot be set from code - "
             "record them, do not fake them." % datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "", "| Repo | Control | Result |", "|---|---|---|"]
    for r in results:
        for k, v in r.get("findings", {}).items():
            lines.append("| %s | %s | %s |" % (r["repo"], k, v))
    text = "\n".join(lines) + "\n"
    print(text)
    if a.write:
        os.makedirs(os.path.dirname(os.path.abspath(a.write)), exist_ok=True)
        open(a.write, "w", encoding="utf-8", newline="\n").write(text)
        print("[approvals] wrote %s" % a.write)
    if a.json:
        json.dump(results, open(a.json, "w", encoding="utf-8", newline="\n"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
