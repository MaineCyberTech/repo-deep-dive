# Remediation PATCH-3 — Offsite retry/backoff + dead-letter (FEAT-P2-002)

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PATCH-3` — Offsite retry/backoff + dead-letter (FEAT-P2-002)
- Repo / base: `MaineCyberTech/falcon` @ `430da82274af4c0821542627fdb9e6ab74afa826` (`main`)
- Branch / commit: `remediation/patch-03-20261003-0018-fix-backup-abort-markers-20b5e57` @ `2e049a9`

## Summary

`FEAT-P2-002`: backup/offsite delivery was single-attempt with no retry, backoff, or dead-letter. The finding's core remedy **already landed on `main` before this patch** (commit `87addf7`, RES-P0-002):

- `bootstrap/80-offsite-backup.sh` retries the Spaces workflow with exponential backoff and writes a persistent `.offsite-dead-letter` marker on any non-zero exit (cleared only by a fully successful run);
- `bootstrap/85-backup-job.sh` surfaces an offsite failure as a non-zero job exit.

What was **still missing** is the signal the finding/patch plan calls for: there was no `falcon_backup_offsite_dlq` metric and no alert fired on *exhausted retries* (only a 36 h freshness rule).

This patch closes that residual gap:

- `automation/validation/export_monitor_metrics.sh` exports `falcon_backup_offsite_dlq` (1 when the dead-letter marker exists) and `falcon_backup_offsite_dlq_age_seconds` (marker age, -1 when absent), reading the same marker the retry path writes. The path is overridable with `FALCON_OFFSITE_DLQ` (consistent with the existing `FALCON_OFFSITE_LOG` / `FALCON_OFFSITE_UPLOAD_STATE` overrides).
- `bootstrap/90-alerting.sh` adds the `falcon-backup-offsite-dlq` rule (`falcon_backup_offsite_dlq > 0`, critical, 1 m) so an exhausted retry pages immediately instead of waiting for the 36 h window.
- `automation/validation/tests/remediation_guards_test.sh` adds static regression guards for both.

Deliberately **not** changed: `bootstrap/80-offsite-backup.sh` and `bootstrap/85-backup-job.sh` — their retry/backoff/dead-letter/non-zero-exit behaviour is already present and correct on the base commit. The dead-letter file holds the latest failure record (bounded overwrite) rather than an unbounded append; the age metric preserves the "how stale" signal an append log would provide.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FEAT-P2-002` | P2 | open → addressed (draft) | Retry/backoff/dead-letter already on `main`; this adds the required `falcon_backup_offsite_dlq` metric and an alert on exhausted retries. Moves to `verified-fixed` only once merged. |

## Changes

| File | What changed |
|---|---|
| `automation/validation/export_monitor_metrics.sh` | `STATE_OFFSITE_DLQ` (env-overridable); computes `offsite_dlq` / `offsite_dlq_age`; emits `falcon_backup_offsite_dlq` and `falcon_backup_offsite_dlq_age_seconds`; adds the family to the post-write self-check grep. |
| `bootstrap/90-alerting.sh` | New `falcon-backup-offsite-dlq` Grafana rule (`> 0`, critical, `for: 1m`) next to `falcon-backup-offsite-stale`. |
| `automation/validation/tests/remediation_guards_test.sh` | Static guards asserting the exporter emits `falcon_backup_offsite_dlq` and the rule `falcon-backup-offsite-dlq` exists. |

Scope note: the plan's file list is `85-backup-job.sh`, `80-offsite-backup.sh`, `export_monitor_metrics.sh`; the first two are already fixed on `main`, and the plan's own change text requires "a Grafana rule … on a non-zero/dead-letter age", which lives in `bootstrap/90-alerting.sh`. The diff is confined to the metric, the rule, and the guard test. No `review-package/` mirror or drive-by changes.

## Verification Performed

Runner: `ci-runner` (Proxmox LXC 200), clean LF snapshot of `2e049a9` (`dirty: 0`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | ci-runner | 0 | `validation_failures=0`; 30/30 shell suites pass (incl. `offsite_backup_reuse_test.sh`, `offsite_upload_delta_test.sh`, `remediation_guards_test.sh`) |
| `bash automation/validation/tests/offsite_backup_reuse_test.sh` | ci-runner | 0 | `checks=32 failures=0`; case 5 proves a successful run clears the dead-letter marker |
| `bash automation/validation/tests/offsite_upload_delta_test.sh` | ci-runner | 0 | `checks=65 failures=0`; case 11 proves a transient upload failure is retried in-run (RES-P0-002) |
| `bash automation/validation/tests/remediation_guards_test.sh` | ci-runner | 0 | `PASS remediation_guards` (asserts the new metric + rule) |
| `shellcheck --severity=warning <changed shell files>` | ci-runner | 0 | no findings |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 0 | `no leaks found` |

- Dedicated `export_monitor_metrics` test: **not present** in `automation/validation/tests` (recorded in `verify.log`, not silently skipped). The metric emission and rule are covered by `remediation_guards_test.sh`.
- Secret scan (gitleaks): **pass** — `no leaks found`.
- Honest limitation: the live exporter was **not** executed (it writes `/srv/falcon/textfile` and would mutate host state); the metric path is covered by the static guard and code review, not a live sample.

## Evidence bundle

- `remediation/PATCH-3/verify.log` — SHA-256 `80EC0566F9383584E7EF4F5A873C3EBEBF2F3C8231859EFF22082F8D3204A2F8`
- `remediation/PATCH-3/diff.patch` — SHA-256 `AE6F72DD0D1289B5C07A24F969F8B10A1FC37192652FC8C6FC8B1851000E0575`
- `remediation/PATCH-3/manifest.json`

## Risk and rollback

- Risk: **low** — one new Prometheus gauge family, one new alert rule, and a static test guard. No data-path, credential, topology, or retry-behaviour change. The rule is `noDataState: OK`, so a missing metric does not fire spuriously.
- Rollback: `git revert 2e049a94d5af532c67f452176e88f0f4c90a34ff`.

## Review checklist

- [ ] Diff touches only the patch-set files (plus the alerting rule the plan requires and the test guard)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Alert expression yields a positive value when true (bool/`>` form)
- [ ] Rollback is practical

## Definition of done (for this set)

`FEAT-P2-002`'s retry/backoff/dead-letter is inherited from `main` (RES-P0-002); exhausted retries now surface as `falcon_backup_offsite_dlq` and page via `falcon-backup-offsite-dlq` immediately. The full gate (`ci/validate.py`) and the offsite suites stay green.

*Draft only — a human reviewer merges. No auto-merge, no self-approval. No secrets committed.*
