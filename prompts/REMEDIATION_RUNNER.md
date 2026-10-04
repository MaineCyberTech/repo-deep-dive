# Prompt 50 - Remediation Runner

@include `00_SHARED_AUDIT_RULES.md`

## Mission

Turn a completed audit run's patch plan into **scoped, tested, reviewed pull requests** -
without ever auto-merging and without fabricating any evidence.

This prompt is executed by an agent (e.g. an OpenCode subagent) per patch set. It consumes
the machine-readable plan produced by `tools/remediation_plan.py`.

## Inputs

- `{run}`: the audit run folder (contains `patch_plan.md`, `findings.json`,
  `remediation_plan.json`, `risk_register.md`).
- `{repo}`: the target repository (bare name under the org, or a local path).
- `{patch_set}`: a single `PS-00N` id (or `all`).
- `{mode}`: `plan` (default, no writes) or `apply`.
- `{lab}`: the test runner - the Proxmox `ci-runner` container or `edge-builder` VM.

## Non-negotiable guardrails

- **Never auto-merge, never self-approve.** PRs are opened as **draft** and require a human
  reviewer (the implementer cannot approve a review or release gate - see `00_SHARED_AUDIT_RULES.md`).
- **Preflight before work.** Run `bash tools/lab-vpn/lab-audit-preflight.sh` and require
  `RESULT: PASS` before compiling or applying any patch set and before dispatching lab
  verification. If it fails, stop and record **blocked** - do not dispatch work to the lab.
- **No fabrication.** Every claim in the PR (tests, lint, build) must cite real command output
  with exit codes. If a check cannot run, record it as `not run` and why.
- **Scoped changes only.** Touch only the files in the patch set (plus minimal tests/docs the
  fix requires). No drive-by refactors, reformatting, or dependency bumps outside the set.
- **Secrets.** Never commit secrets; run a `gitleaks` gate on the diff before pushing, and
  redact secret-like values anywhere in evidence.
- **Findings move to `verified-fixed` only with evidence at the new commit** (test/CI artifact),
  otherwise `partially-fixed` / `still-open`.
- Do not modify the audit run's original findings; append status via `tools/remediation_status.py`.

## Steps

1. **Plan.** Run `python3 tools/remediation_plan.py <run>`; read `remediation_plan.json`.
   In `plan` mode, print each patch set, its findings, files, dependencies, risk and verification
   commands, then stop.
2. **Select.** For `apply`, take one patch set (or iterate `all` in dependency order). Skip sets
   whose dependencies are not yet merged.
3. **Branch.** From the repo default branch:
   `git switch -c remediation/PS-00N-<run>`.
4. **Implement.** Make the minimal fix for every finding in the set. Reference finding IDs in the
   commit body. If any change is ambiguous or needs a product decision, stop and record an
   **open question** instead of guessing.
5. **Test (in the lab).** Run the set's verification commands in the lab - prefer the job API
   (`tools/lab_runner.py`), which can sync the repo and run the command in one hop, over ad-hoc SSH
   (fall back to local execution only when the runner is unavailable):
   `tools/lab_runner.py --url <ci-runner|edge-builder> --token <t> --sync --repo <repo> --org <org>`
   then `... --repo <repo> --command "<verification command>"`. Capture raw output + exit codes to
   `<run>/remediation/PS-00N/verify.log`. Fail closed: a failing gate blocks the PR.
   The lab images now include `actionlint`, `yq`, `hadolint`, `trivy`, `gh`, `shellcheck`, `jq`,
   `gitleaks`, and `pytest` (both guests), so most verification commands run without setup.
6. **Secret gate.** `gitleaks detect --no-git --redact` on the working tree; block on findings.
7. **Commit + push.** Conventional commit `fix(<area>): <title> [<finding-ids>]`; push the branch.
8. **Pull request.** Open a **draft** PR using `templates/remediation_pr.md`, including:
   summary, findings covered, patch-set mapping, exact verification commands + results, evidence
   bundle path/digest, risk, rollback, and a **review checklist**. Add reviewers.
9. **Evidence bundle.** Capture the diff, verify logs, and a manifest with SHA-256 for the PR
   (reuse the review-package/digest pattern from the falcon lab).
10. **Review (advisory).** Optionally run the review prompt to post an advisory review comment
    (never an approval). Human review decides.
11. **Reconcile.** After review/merge, run `tools/remediation_status.py` to update the run's
    `follow_up_register.md` + `verification_log.md` with per-finding status and the commit/PR as
    evidence.

## Output (per patch set)

- branch name, commit SHA(s), draft PR URL
- `<run>/remediation/PS-00N/{verify.log, diff.patch, manifest.json}`
- updated `follow_up_register.md` (statuses) via `remediation_status.py`

## Required response

```markdown
# Remediation Run - PS-00N

## Patch set

## Findings addressed

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|

## Diff summary

## Pull request

## Rollback

## Open questions

## Status changes (findings)
```
