# Remediation PATCH-2 — Extend the abort trap to all long-running jobs (ARCH-P2-005)

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PATCH-2` — Extend the abort trap to all long-running jobs (ARCH-P2-005)
- Repo / base: `MaineCyberTech/falcon` @ `430da82274af4c0821542627fdb9e6ab74afa826` (`main`)
- Branch / commit: `remediation/patch-02-20261003-0018-fix-backup-abort-markers-20b5e57` @ `38c18ef`

## Summary

`ARCH-P2-005`: the interrupt-safety abort trap was only installed by the nightly backup job, so offsite upload, cold-copy, indexer snapshot and restore could be interrupted mid-step without a durable marker. At the audited commit only `85-backup-job.sh` called `install_abort_trap`. On current `main`, `80-offsite-backup.sh`, `restore_rehearsal.sh` and `disk_guard.sh` already install it; **`r2_cold_copy.sh` and `wazuh_indexer_backup.sh` still did not.**

This patch closes the remaining gap by giving both jobs the shared interrupt-safety helper (`automation/validation/lib/abort.sh`, reached through the same pattern the other long-running scripts use):

- `install_abort_trap "<job>"` is installed early in `main` (a SIGTERM/SIGINT writes a durable marker under `FALCON_ABORT_DIR` and exits 130);
- a pre-existing marker is surfaced with a warning rather than silently ignored;
- the marker is cleared **only on a clean completion** — a failure or an interrupted run keeps it, so the next run can see the prior state.

This is scoped to trap installation. The stronger contract from `ARCH-P1-002` — writing a marker on *any* non-clean exit — is delivered by PATCH-1 (PR #18) in `bootstrap/lib.sh`; because both jobs call the shared helper, they inherit that behaviour once it lands. No conflict: the job names are new and disjoint.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P2-005` | P2 | open → addressed (draft) | `r2_cold_copy.sh` and `wazuh_indexer_backup.sh` now install the shared abort trap and clear the marker only on clean completion. Moves to `verified-fixed` only once merged. |

## Changes

| File | What changed |
|---|---|
| `automation/validation/r2_cold_copy.sh` | Sources `lib/abort.sh`; in `main` installs `install_abort_trap "r2-cold-copy"` and warns on a stale marker. `_r2_cold_copy_exit` keeps the existing metrics publishing and adds `clear_abort_marker "r2-cold-copy"` only when the exit is clean and not a dry run. |
| `automation/validation/wazuh_indexer_backup.sh` | Sources `lib/abort.sh`; in `main` installs `install_abort_trap "wazuh-indexer-backup"` and warns on a stale marker. `_wazuh_indexer_exit` keeps the existing metrics publishing and adds `clear_abort_marker "wazuh-indexer-backup"` only when the exit is clean and not a dry run. |
| `automation/validation/tests/abort_marker_test.sh` | Section 4 now requires `install_abort_trap` in `r2_cold_copy.sh` and `wazuh_indexer_backup.sh`, and requires `clear_abort_marker` in both. |
| `automation/validation/tests/wazuh_indexer_backup_test.sh` | Points `FALCON_ABORT_DIR` at the suite's temp workdir so the offline suite stays hermetic. |

Scope: only the patch-set files plus the test that consumes them. No `review-package/` mirror or out-of-scope changes.

## Verification Performed

Runner: `ci-runner` (Proxmox LXC 200), clean LF snapshot of `38c18ef` (`dirty: 0`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | ci-runner | 0 | `validation_failures=0`; all shell suites pass (incl. `abort_marker_test.sh` and `wazuh_indexer_backup_test.sh`) |
| `bash automation/validation/tests/abort_marker_test.sh` | ci-runner | 0 | `PASS abort_marker` |
| `bash automation/validation/tests/offsite_backup_reuse_test.sh` | ci-runner | 0 | `checks=32 failures=0` |
| `bash automation/validation/tests/offsite_upload_delta_test.sh` | ci-runner | 0 | `checks=65 failures=0` |
| `bash automation/validation/tests/wazuh_indexer_backup_test.sh` | ci-runner | 0 | `checks=20 failures=0` |
| `shellcheck --severity=warning <changed shell files>` | ci-runner | 0 | no findings |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 0 | `no leaks found` |

- Secret scan (gitleaks): **pass** — `no leaks found`, captured in `remediation/PATCH-2/verify.log`.
- Scope check (files within patch set): **pass** — diff touches exactly the two patch-set scripts plus the two tests.

## Evidence bundle

- `remediation/PATCH-2/verify.log` — SHA-256 `7a7f8e8e642c279d4e2dea31410bea483680069d4142cc789897fd6727dac746`
- `remediation/PATCH-2/diff.patch` — SHA-256 `5a07ef40efae0f52520c5021d2e8373a6d9b4eb79d3e7c32906c2981493c3fb1`
- `remediation/PATCH-2/manifest.json`

## Risk and rollback

- Risk: **low** — error-path bookkeeping in two validation scripts; the success/failure data paths, metrics emission, topology and credentials are unchanged.
- Rollback: `git revert 38c18ef75ab115a5e6bce550bec49f2bb11bfa47`.

## Review checklist

- [ ] Diff touches only the patch-set files (plus tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

`abort_marker_test.sh` requires `install_abort_trap` in all five long-running scripts (`85-backup-job.sh`, `80-offsite-backup.sh`, `restore_rehearsal.sh`, `disk_guard.sh`, plus `r2_cold_copy.sh` and `wazuh_indexer_backup.sh`), and requires `clear_abort_marker` in the jobs that must clear it. `r2_cold_copy.sh` and `wazuh_indexer_backup.sh` install the shared trap and clear the marker only on a clean completion. The full gate (`ci/validate.py`) stays green.

*Draft only — a human reviewer merges. No auto-merge, no self-approval. No secrets committed.*
