# Post-audit pipeline (standard)

The standard sequence after any audit. **Order matters:** publish the full audit first, then
remediate, then merge — with merging gated on explicit authorization.

```
preflight -> deterministic sweep -> audit -> PUBLISH AUDIT PR -> remediation plan
          -> draft remediation PRs -> MERGE ALL IN -> run all PRs OR stop for delegation
```

## 0. Setup + preflight (required)
Agent setup is one step: `bash tools/lab-vpn/lab-audit-gh.sh setup <name> --repos <r,...>` — it sets
up the connection, runs the preflight, and **confirms each repo's approvals** via
`tools/repo_approvals.py` (`runbooks/AGENT_SETUP.md`); record `NEEDS-HUMAN` controls, never fake them.

## 0b. Preflight (required for lab-dependent work)
`bash tools/lab-vpn/lab-audit-preflight.sh` (or `--mode lab`) must print `RESULT: PASS`
(see `docs/LAB_VPN.md`). If the lab genuinely can't be used, work still proceeds **locally**.

## 1. Deterministic sweep
Dispatch `.github/workflows/deep-dive-deterministic.yml` (`repos` blank = all org repos, `deep=true`).
Artifacts: per-repo `deterministic-findings.json` + `ORG_SUMMARY.md`.

## 2. Audit (focused or full)
Run the focused security/supply-chain/CI lenses (or the full master runner) per target repo and
produce, per repo, a `findings.json` + a human report. Evidence-first; validate every machine-check
hit as **real / false-positive / partially** (`prompts/00_SHARED_AUDIT_RULES.md`).

## 3. Publish the FULL AUDIT first (`tools/publish_audit.py`)
Publishes the canonical run to the repo **and** the portable copy to the pack:
```bash
tools/publish_audit.py --repo <repo> --branch <default> --sha <full-sha> \
    --source-dir <dir with findings.json + FINDINGS.md> [--dry-run]
```
It:
- normalizes findings to `AREA-Px-NNN` and writes a run folder that **passes `tools/check_run.sh`**
  (registers, finals, manifest, INDEX);
- installs `runs/<repo>-<run>/` and appends a `runs/INDEX.md` row;
- opens/updates a **draft** PR in the repo adding `docs/audits/repo-deep-dive/<run>/`.
Then: `bash tools/pack_digest.sh && bash tools/lint_pack.sh` → commit/push the pack.

> Repo settings that can't be set from code (branch protection, required checks, environment
> reviewers) are documented as prerequisites, never faked.

## 4. Remediation plan + draft PRs
1. `tools/remediation_plan.py <run>` → `remediation_plan.json` (patch sets).
2. Agents implement each patch set per `prompts/REMEDIATION_RUNNER.md`: minimal scope, run the
   declared verification (lab when available, else local — record which), `gitleaks` the diff.
3. Open **draft** PRs (one per patch set), each referencing the finding IDs and citing real
   command output. Never self-approve; never fabricate verification.

## 5. Merge all in (explicit authorization required)
Only with the operator's explicit go-ahead (draft-only is the default):
```bash
gh pr ready <n> && gh pr merge <n> --merge   # audition PR first, then remediation PRs
```
- Merge the **audit PR first**, then remediation PRs (the audit is the baseline evidence they cite).
- Record the merge commit as evidence; reconcile statuses via `tools/remediation_status.py`
  (`verified-fixed` only with a commit artifact at the current commit).
- Resolve conflicts conservatively; if a change is ambiguous, leave that PR open rather than guess.

## 6. Branch
After merging, either **run the remaining PRs** (finish the queue) or **stop for delegation**
(hand the remaining review/queue to a human; report the state and the open PRs).

## Gates and invariants
- Draft PRs only by default; **no auto-merge and no self-approval without explicit authorization**.
- Fail closed on verification you cannot run (`not run` + why), never fabricate.
- Repo secrets stay in GitHub; external machines route through Actions (`tools/lab-vpn/lab-audit-gh.sh`).
- Keep `PACK_DIGEST.txt` current and `tools/lint_pack.sh` green before every pack push.
