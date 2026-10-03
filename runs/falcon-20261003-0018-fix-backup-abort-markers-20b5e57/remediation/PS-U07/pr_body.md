# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U07` (unassigned FINAL finding `FINAL-P1-001`, "Operational resilience
remains incomplete across the backup lifecycle"). The finding is an aggregate: its recommended fix
sequences the C1-style resilience work as (1) fix the abort-marker contract, (2) extend the abort
trap to the remaining long-running jobs, (3) add offsite retry/backoff + dead-letter, then
(4) set data retention.

On `origin/main` the first three are partly done: `RES-P0-001`/`RES-P0-002` fixed the marker
contract and installed the trap in `85-backup-job.sh`, `80-offsite-backup.sh`,
`restore_rehearsal.sh` and `disk_guard.sh`, and the offsite workflow now has bounded
retry/backoff with a dead-letter marker. Two long-running jobs were still uncovered by the abort
trap: the R2 cold-copy job (`automation/validation/r2_cold_copy.sh`) and the Wazuh indexer backup
job (`automation/validation/wazuh_indexer_backup.sh`). This PR closes that gap (the "extend the
trap" step).

Each job now sources the shared abort helper, installs the SIGTERM/SIGINT trap (durable marker +
exit 130), warns when a stale marker is present so the run re-verifies, and clears the marker only
on a clean (exit 0) completion. The offline regression test `abort_marker_test.sh` is extended to
assert both jobs install the trap and clear the marker. The retention step (DATA-P1-001) needs the
owner's retention decision and is recorded as an open question, not guessed here.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U07` — Unassigned FINAL findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u07-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `a981b7b449ba48bf755ce9e9c0b17f1a94178e28`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FINAL-P1-001` | P1 | open -> partially-fixed (draft PR) | The abort trap is extended to the two remaining long-running jobs and the offline test asserts it. The marker-contract and retry/dead-letter parts were already fixed at `RES-P0-001`/`RES-P0-002`; the retention part (`DATA-P1-001`) needs the owner's retention decision (see below). |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and the finding's evidence requirements are met.

## Changes

| File | What changed |
|---|---|
| `automation/validation/r2_cold_copy.sh` | Sources `lib/abort.sh`; installs the trap as `r2-cold-copy`; warns on a pre-existing marker; new `r2_cold_copy_exit` EXIT handler clears the marker only on exit 0 (metrics publishing unchanged). |
| `automation/validation/wazuh_indexer_backup.sh` | Sources `lib/abort.sh`; installs the trap as `wazuh-indexer-backup`; warns on a pre-existing marker; new `wazuh_indexer_backup_exit` EXIT handler clears the marker only on exit 0 (metrics publishing unchanged). |
| `automation/validation/tests/abort_marker_test.sh` | Extends the existing coverage loop to the two new jobs (install) and asserts the newly covered jobs clear the marker on clean completion. |

Scope: two job scripts plus their existing offline test. No workflow, dependency, schema, ledger,
machine artifact or unrelated script was changed.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against the branch synced with
`scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U07/verify.log` (commit under test `a981b7b`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` — `validation_failures=0`; 30/30 shell suites incl. `abort_marker_test.sh` and `wazuh_indexer_backup_test.sh`; shellcheck 172 scripts; secret scan |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` — `no leaks found` (5,638 bytes scanned) |

- Secret scan (gitleaks): **pass** — no leaks on the diff.
- Scope check: **pass** — two job scripts + one test file.
- Note: `lab-sync.ps1` extracts the Windows working tree; the extracted clone has
  `core.fileMode=false`, so tracked `*.sh`/`*.py` files were `chmod +x` before the gate (without
  that the offline suites that execute tracked scripts exit 126). Pre-existing mixed-EOL
  `docs/phase8/reviews/*.md` blobs (HYG-P2-002) are unrelated to this patch and not part of the diff.

## Evidence bundle

- `remediation/PS-U07/diff.patch` — SHA-256 `B442B099FED1F7610E25871EFD5172A0A8CEA6AEAE8CC63510434E8C472B6718`
- `remediation/PS-U07/verify.log`
- `remediation/PS-U07/manifest.json`
- `remediation/PS-U07/pr_body.md`

## Risk and rollback

- Risk: **low**. The change adds interrupt-safety around two existing jobs and an assertion to an
  existing offline test. Behaviour on the happy path is unchanged: the trap only fires on
  SIGTERM/SIGINT (durable marker + exit 130) and the EXIT handler only removes a marker file.
- Rollback: `git revert a981b7b449ba48bf755ce9e9c0b17f1a94178e28`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] The fix does not weaken existing marker/verification behaviour
- [ ] Rollback is practical

## Open questions / deferred

1. **Retention (`DATA-P1-001`) needs the owner's decision.** `FINAL-P1-001`'s fourth step
   (Wazuh/IRIS retention) requires an explicit retention window chosen by the owner; the audit
   recorded it as an owner decision. A code/test change here would guess a number and is not
   fabricated. Recorded as an open question.
2. **Other long-running jobs.** `85-backup-job.sh`, `80-offsite-backup.sh`,
   `restore_rehearsal.sh` and `disk_guard.sh` already carried the trap; the two jobs in this PR
   were the remaining gaps identified by the audit (`ARCH-P2-005`). Any future long-running job
   should adopt the same `lib/abort.sh` pattern.
