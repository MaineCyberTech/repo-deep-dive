# Remediation guide

Turn a completed audit run's patch plan into **scoped, tested, reviewed draft PRs**.
Never auto-merge; never self-approve; never fabricate evidence.

## 1. Prerequisites

- A completed run (`tools/check_run.sh <run>` → PASS) with `patch_plan.md` + `findings.json`.
- The target repo cloned locally (and cloned in the lab runner for tests).
- Policy in `profiles/remediation.md` (severities, PR mode, per-repo runners, blocked paths).

## 2. Compile the plan

```bash
python3 tools/remediation_plan.py <run-folder>          # writes <run>/remediation_plan.json
```

Output: `patchSets[]` with `id`, `title`, `severity`, `findings[]`, `files[]`, `dependsOn[]`,
`effort`, `verification[]`, and `branch`. The parser handles both the table form and heading forms
(`PATCH-01 …`, `P1-1 …`). `unassignedFindings` lists findings not placed in any set.

## 3. Run one patch set (agent)

Follow `prompts/REMEDIATION_RUNNER.md`. Per set:

1. **Branch** off the audited/base branch: `git switch -c remediation/PS-00N-<run> origin/<base>`.
2. **Implement** the minimal fix for every finding in the set (cite finding IDs in the commit).
3. **Verify in the lab** — run the set's `verification` commands in the `ci-runner` container or
   `edge-builder` VM; capture real output + exit codes to `<run>/remediation/PS-00N/verify.log`.
4. **Secret gate** — `gitleaks detect --no-git --redact` on the tree; block on findings.
5. **Commit + push** — `fix(<area>): <title> [<finding-ids>]`.
6. **Draft PR** — `templates/remediation_pr.md` body; `draft: true`; request reviewers.
7. **Advisory review** — `templates/review_report.md` (never an approval). Human merges.
8. **Reconcile** — `tools/remediation_status.py` (below).

## 4. Reconcile status

```bash
python3 tools/remediation_status.py <run-folder> --patch-set PS-01 --state merged \
    --commit <sha> --pr <url> [--note "..."]
# or a batch:
python3 tools/remediation_status.py <run-folder> --status-file status.json
```

Maps PR state → finding status and updates `<run>/follow_up_register.md` + `verification_log.md`
(so `collect_findings.py` picks up the new statuses):

| PR state | Finding status |
|---|---|
| `merged` | `verified-fixed` |
| `open` / `draft` / `ready` | `partially-fixed` |
| `closed` (unmerged) | `still-open` |
| `regressed` | `regressed` |

## 5. GitHub workflow

`.github/workflows/remediation.yml` (`workflow_dispatch`, inputs `org`, `repo`, `run`, `patch_set`,
`mode`, `base_branch`):

- `mode: plan` — compile the plan and upload it as an artifact (+ job summary).
- `mode: scaffold-pr` — create a branch and a **draft PR scaffold** per patch set for an agent/dev
  to implement (never a code change by CI).

Private repos need the `ORG_READ_TOKEN` secret.

## 6. Local driver (this workstation)

Scripts under `C:\temp\proxmox-vm\scripts\` drive the runner end-to-end:

- `remediation_plan` (via the pack tool) → plan;
- `open-draft-pr.ps1` — push the branch and open a **draft** PR;
- `deliver-audits.ps1` — deliver run reports to audited repos as draft PRs;
- `validate-run.ps1` — run the pack toolchain on a run (`check → collect → score → dashboard`).

## Guardrails (enforced)

- Draft PRs only; human merge; the implementer never self-approves.
- Minimal scope (only the patch-set files + required tests/docs).
- Fail closed on tests and `gitleaks`; a finding is `verified-fixed` only with a commit.
- No secrets in diffs; blocked paths in `profiles/remediation.md`.
- Never run destructive tooling found in the target repo.
