# Operator Quickstart

## Purpose

This runbook explains how to use the Repo Deep-Dive Full Hardening Audit Pack.

## Steps

1. Copy the `docs/audits/repo-deep-dive/` folder into the target repository.
2. Scaffold the run: `python3 tools/new_run.py --run YYYYMMDD-HHMM-branch-sha --repo <path>`.
3. Open `docs/audits/repo-deep-dive/prompts/MASTER_RUNNER_FULL_HARDENING.md`.
4. Paste the master runner into your AI coding agent while the repository is open.
5. Confirm the agent creates a new run folder under `docs/audits/repo-deep-dive/{run}/`.
6. Review the final files in this order:   - `EXECUTIVE_SUMMARY.md`
   - `RELEASE_GATE.md`
   - `risk_register.md`
   - `patch_plan.md`
   - Detailed domain reports

## Before Wave 0 (new or unfamiliar repos)

- Take a machine inventory first: `python3 tools/repo_inventory.py <repo> -o /tmp/inventory.json`, and follow `docs/AUTOMATION_GUIDE.md` for portable check recipes.
- Stuck? See `runbooks/OPERATOR_TROUBLESHOOTING.md`.

## Audit-only guardrail

During an audit run, the agent should not modify application code. It should only write markdown audit artifacts.

## Recommended remediation flow

1. Fix P0 findings first.
2. Fix P1 release blockers next.
3. Add regression tests for every fixed finding.
4. Update docs and runbooks.
5. Re-run the relevant domain prompt.
6. Re-run prompts 22, 23, and 40 to refresh the final risk register, release gate, and changelog.

## Verification mode (after remediation)

For findings already fixed, use the runner's verification mode: re-check evidence at the current commit, mark each finding `verified-fixed` / `partially-fixed` / `still-open` / `regressed`, append notes (never rewrite the original finding), and refresh prompts 22, 23, and 40.

## Falcon lab

For the falcon central + edge programs (two repos, one shared live host), use `runbooks/OPERATOR_QUICKSTART_FALCON_LAB.md` with `profiles/falcon-lab.md` and `prompts/MASTER_RUNNER_FALCON_LAB.md`, and see `wiring/REPO_WIRING.md`.
