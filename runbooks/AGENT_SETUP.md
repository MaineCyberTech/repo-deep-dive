# Agent setup — pack + lab + repo approvals

What an agent does when it starts work here, and what it must **confirm or record**. Keep it
scoped: only do the steps that apply to the work you're about to do.

## 1. Lab connection (only if the work uses the lab)
```bash
gh auth status                                   # needs repo scope
bash tools/lab-vpn/lab-audit-gh.sh onboard <me>  # self-service; no lab secret handled locally
bash tools/lab-vpn/lab-audit-preflight.sh --mode local --remote-key ~/.ssh/labvpn
```
`RESULT: PASS` required when using the lab. If the lab genuinely can't be used, the work runs
locally (`lab-audit-run.sh`) and you record `MODE=local`. Audits that don't touch the lab are
exempt from the preflight.

## 2. Confirm the local repos' approvals (record, never fake)
Approvals that cannot be set from code — branch protection, required checks, environment
reviewers, tag rules, required secrets — must be **confirmed or recorded**:
```bash
python3 tools/repo_approvals.py --org MaineCyberTech \
    --repos <repo,repo,...> \
    --required-check "Lab preflight / lab" \
    --secret LAB_ENDPOINT_SSH_KEY \
    --write docs/REPO_APPROVALS.md
```
The tool prints a `CONFIRMED / MISSING / NEEDS-HUMAN` table per repo (default-branch protection,
required status checks, required reviews, environments + reviewers, required secret names).

## 3. Record what was done
- Copy the `CONFIRMED / MISSING / NEEDS-HUMAN` summary into the audit/remediation run or PR body
  (or the `docs/REPO_APPROVALS.md` artefact).
- List every `NEEDS-HUMAN` control with the owner action required. **Do not claim a control is set
  when only declared in code** (e.g. a workflow `environment:` needs a matching environment with
  required reviewers in repo settings to actually gate).
- A one-shot setup stamp is written by the preflight to `.git/lab-audit-ready.json`.

## 4. Then proceed
Audit → `runbooks/POST_AUDIT_PIPELINE.md` (publish first, then remediate, then merge on
authorization). Keep the pack green: `tools/pack_digest.sh`, `tools/lint_pack.sh`, `tools/self_test.sh`.
