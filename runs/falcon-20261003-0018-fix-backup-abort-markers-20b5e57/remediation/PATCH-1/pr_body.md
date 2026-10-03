# Remediation PATCH-1 — Abort-marker contract (ARCH-P1-002)

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PATCH-1` — Abort-marker contract (ARCH-P1-002)
- Repo / base: `MaineCyberTech/falcon` @ `430da82274af4c0821542627fdb9e6ab74afa826` (`main`)
- Branch / commit: `remediation/patch-01-20261003-0018-fix-backup-abort-markers-20b5e57` @ `7a67d90`

## Summary

`ARCH-P1-002`: the abort-marker contract in the nightly backup job was self-contradictory. `bootstrap/85-backup-job.sh` cleared a prior run's marker at startup — *before this run completed* — and a normal non-zero exit (e.g. a failed snapshot) wrote no marker at all, so a half-finished or failed run was indistinguishable from a clean state on the next run. This patch makes the marker mean what the comments claim:

- the stale marker is **not** cleared at startup;
- the marker is written on **any** non-clean exit;
- the marker is cleared only as the **last** action of a genuine clean completion.

The SIGTERM/SIGINT path is unchanged (still writes the marker and exits 130).

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P1-002` | P1 | open → addressed (draft) | Early clear removed; failure exits now leave a marker; clean completion is explicit. Moves to `verified-fixed` only once merged. |

## Changes

| File | What changed |
|---|---|
| `bootstrap/lib.sh` | Adds `install_failure_trap` / `mark_clean_exit`. `install_failure_trap` installs an `EXIT` trap that writes the abort marker on any exit not explicitly marked clean; `mark_clean_exit` is the only way to suppress it. |
| `bootstrap/85-backup-job.sh` | Installs the failure trap; stops clearing a stale marker at startup and warns instead; leaves `clear_abort_marker` as the final successful action followed by `mark_clean_exit`. |
| `automation/validation/tests/abort_marker_test.sh` | Adds regression coverage: a normal failure exit leaves a marker; a clean completion (clear + mark) leaves none; and the job surfaces a stale marker while `clear_abort_marker` appears exactly once, after which `mark_clean_exit` runs. |

Scope: only the three patch-set files. No `review-package/` mirror or out-of-scope changes.

## Verification Performed

Runner: `ci-runner` (Proxmox LXC 200), clean LF snapshot of `7a67d90` (`dirty: 0`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | ci-runner | 0 | `validation_failures=0`; 30/30 shell suites pass (incl. `abort_marker_test.sh`) |
| `bash automation/validation/tests/abort_marker_test.sh` | ci-runner | 0 | `PASS abort_marker` |
| `shellcheck --severity=warning bootstrap/lib.sh bootstrap/85-backup-job.sh automation/validation/tests/abort_marker_test.sh` | ci-runner | 0 | no findings |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 0 | `no leaks found` |

- Secret scan (gitleaks): **pass** — `no leaks found`, captured in `remediation/PATCH-1/verify.log`.
- Scope check (files within patch set): **pass** — diff touches exactly the three patch-set files.

## Evidence bundle

- `remediation/PATCH-1/verify.log` — SHA-256 `90722dff05941e8c0d6dd72a374a8ede4457a5ce55b597656b88066eccdc0000`
- `remediation/PATCH-1/diff.patch` — SHA-256 `1a872e85dbc4afd9b502a3bc82eb960ec8e5c3b536f99a32b8b3f03f2ce11af0`
- `remediation/PATCH-1/manifest.json`

## Risk and rollback

- Risk: **low** — error-path bookkeeping in one bootstrap job; no change to the success path, topology, or credentials.
- Rollback: `git revert 7a67d906de819e80a49f890dce693ecd595f8920`.

## Review checklist

- [ ] Diff touches only the patch-set files (plus tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

`abort_marker_test.sh` asserts a snapshot-failure `exit 1` leaves a marker and a clean completion leaves none; a stale marker is not cleared at startup; `clear_abort_marker` remains the last successful action before `mark_clean_exit`. The full gate (`ci/validate.py`) stays green.

*Draft only — a human reviewer merges. No auto-merge, no self-approval. No secrets committed.*
