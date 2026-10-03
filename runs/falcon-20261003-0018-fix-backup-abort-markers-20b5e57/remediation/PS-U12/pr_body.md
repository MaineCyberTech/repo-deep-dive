# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U12` (unassigned SUPPLY findings) for the run
`20261003-0018-fix-backup-abort-markers-20b5e57`. After checking `origin/main`
(`430da82274af4c0821542627fdb9e6ab74afa826`), all three findings are still open at
base. The open `PATCH-5` PR (#17) covers the *different* findings `SUPPLY-P1-001`/`002`
(compose-gate scope + waivers, and the `--require-vuln` gate), so this set is deliberately
disjoint: it does not touch `automation/validation/check_compose_digests.py`,
`automation/validation/sbom_coverage_check.sh`, `pins/supply-chain-waivers.json`, or the
`check_compose_digests`/`check_sbom_vuln` gate bodies.

- `SUPPLY-P2-001` (open) - **fixed here**: the `.gitleaks.toml` allowlist that skipped the
  entire `docs/audits/` and `ledgers/` subtrees is narrowed to the two files that actually
  carry the classified matches. Any other file under those trees (and any new audit folder)
  is now scanned with the default rules; `secret_scan.py` remains the primary value-aware
  scanner and is unchanged.
- `SUPPLY-P2-002` (open) - **fixed here**: `pins/images.lock` freshness is wired into the
  release gate as a new `ci/validate.py` check (`lock-age`, `LOCK_MAX_AGE_DAYS=30`) that
  reuses the tested `check_compose_digests.py --max-lock-age-days` rule. The lock is 12 days
  old at this commit; the gate fails closed once it exceeds the window.
- `SUPPLY-P3-001` (open) - **fixed here**: `pins/verify-digests.sh` now requires the pinned
  digest to be a member of the image's full `.RepoDigests` set instead of comparing index 0
  only. A new offline fixture suite (`verify_digests_multiarch_test.sh`, 5/5) proves the
  multi-arch member passes and an absent digest fails.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U12` - Unassigned SUPPLY findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u12-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `5f9cf9a304fba3ecd82dfee951e8d299c9a93f15`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SUPPLY-P2-001` | P2 | open -> partially-fixed (draft PR) | The broad `paths = ['docs/audits/.*', 'ledgers/.*']` entry is replaced by the two classified files (`21_repo_hygiene_maintainability.md`, `ledgers/test_execution.csv`), still scoped to the `generic-api-key` rule. Recorded in `SCANNER_ALLOWLIST_CHANGES.md`. Tree and full-history gitleaks scans are clean; planted secrets under `ledgers/` and `docs/audits/` are still flagged. |
| `SUPPLY-P2-002` | P2 | open -> partially-fixed (draft PR) | New `lock-age` check invokes the tested checker with `--max-lock-age-days 30`; full gate reports `PASS image lock freshness (12d <= 30d)`. The negative control (`--max-lock-age-days 1`) fails. The "refresh on a schedule" half is an operational cadence (owner decision) - see deferred. |
| `SUPPLY-P3-001` | P3 | open -> partially-fixed (draft PR) | `verify-digests.sh` checks membership across all `.RepoDigests`; the new offline suite covers member-second, sole-member and absent-digest cases. The same `{{index .RepoDigests 0}}` idiom remains in `pins/pull-and-record.sh`, which the finding did not name - see deferred. |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and its evidence requirements are met.

## Changes

| File | What changed |
|---|---|
| `.gitleaks.toml` | Allowlist narrowed from the `docs/audits/` + `ledgers/` subtrees to the two classified files (`21_repo_hygiene_maintainability.md`, `ledgers/test_execution.csv`); rule scope unchanged. |
| `ci/validate.py` | New `check_lock_age` + `LOCK_MAX_AGE_DAYS=30`, registered as `lock-age` in `CHECKS`; docstring check list updated. It invokes `automation/validation/check_compose_digests.py --max-lock-age-days 30`. |
| `pins/verify-digests.sh` | Compare the pinned digest against the full `.RepoDigests` set (`grep -qxF`) instead of `{{index .RepoDigests 0}}`; header comment updated. |
| `automation/validation/tests/verify_digests_multiarch_test.sh` | New offline fixture suite (stub `docker`, 5 checks) for the multi-arch membership behaviour. |
| `docs/security/SCANNER_ALLOWLIST_CHANGES.md` | Allowlist table row updated; 2026-10-03 re-validation section added (tree + history clean, planted negatives caught). |

Scope: `.gitleaks.toml`, `ci/validate.py`, `pins/verify-digests.sh`, one security doc, and
one new test file under `automation/validation/tests/`. No compose-gate/waiver/vuln-gate
edits, no runtime service, dependency, schema, workflow or lockfile change.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced
with `scripts/lab-sync.ps1 -Repo falcon` and driven over SSH / the job API
(`tools/lab_runner.py`). Raw log: `remediation/PS-U12/verify.log` (commit `5f9cf9a`). The lab
tar extraction sets `core.fileMode=false`, so the tracked mode-100755 files were `chmod +x`'d
before the gate.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` - `validation_failures=0`; 31/31 shell suites incl. `verify_digests_multiarch_test.sh` (5/5); `PASS image lock freshness (12d <= 30d)`; secret scan/edge pin pass |
| `python3 ci/validate.py --only lock-age` | lab `ci-runner` | 0 | `verify.log` - `PASS image lock freshness (12d <= 30d)` |
| `bash automation/validation/tests/verify_digests_multiarch_test.sh` | lab `ci-runner` | 0 | `verify.log` - `verify_digests_multiarch_test: 5/5 checks passed` |
| `python3 automation/validation/check_compose_digests.py --max-lock-age-days 30` | lab `ci-runner` | 0 | `verify.log` - `lock_age_days=12`, `compose_digest_findings=0` |
| `python3 automation/validation/check_compose_digests.py --max-lock-age-days 1` | lab `ci-runner` | 1 (expected) | `verify.log` - `FINDING pins/images.lock is 12 days old (limit 1)` (negative control) |
| `gitleaks detect --no-git --source . --redact --config .gitleaks.toml` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `verify.log` - `no leaks found` (~7.43 MB); the 4 previously suppressed matches are still covered by the two file paths |
| `gitleaks detect --source . --config .gitleaks.toml --redact --log-opts=--all --exit-code 1` | lab `ci-runner` | 0 | `verify.log` - 747 commits scanned, `no leaks found` |
| Negative control: plant `api_key = "<32-hex>"` under `ledgers/` and `docs/audits/`, re-run gitleaks | lab `ci-runner` | 1 (expected) | `verify.log` - 2 `generic-api-key` hits (the planted files); removed afterwards |

- Secret gate (gitleaks): **pass** - tree and history clean; narrowing does not blind the gate.
- Scope check: **pass** - only the five files above.
- The negative-control files were created in the lab worktree and removed; nothing was committed.

## Evidence bundle

- `remediation/PS-U12/diff.patch` - SHA-256 `b698d29a3cdcd3fcb118f6794393bd9c0a461c9bbb6ea6a11add3a0d330d6610` (22,206 bytes)
- `remediation/PS-U12/verify.log`
- `remediation/PS-U12/manifest.json`
- `remediation/PS-U12/pr_body.md`

## Risk and rollback

- Risk: **low**. One narrowed secret-scanner allowlist (strictly tighter), one additive gate
  check (`lock-age`) that reuses tested logic, one read-only membership fix in a manual
  verification script, and one offline test. No compose scope, waiver, vuln-gate, runtime,
  service or delivery-artifact change.
- Rollback: `git revert 5f9cf9a304fba3ecd82dfee951e8d299c9a93f15`.

## Review checklist

- [ ] Diff touches only the five patch-set files (no compose-gate/waiver/vuln-gate edits)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] The gitleaks negative control proves the narrowed allowlist still catches new files
- [ ] No secrets added; gitleaks clean on the diff (tree + history)
- [ ] `LOCK_MAX_AGE_DAYS=30` is an acceptable refresh window
- [ ] Rollback is practical

## Open questions / deferred

1. **`SUPPLY-P2-002` refresh cadence.** The gate now fails closed on a stale lock; the
   *scheduled* refresh (`pins/pull-and-record.sh` + `pins/verify-digests.sh` on a cadence) is
   an operational/owner decision and is not automated in the repository. The lock is 12 days
   old at this commit, so the gate currently passes and will force a refresh after day 30.
2. **`SUPPLY-P3-001` `pins/pull-and-record.sh`.** The same `{{index .RepoDigests 0}}` idiom
   is used when *recording* the lock, but the finding names only `verify-digests.sh`. Changing
   the recorder could alter recorded digests, so it is left untouched here (out of the named
   scope).
3. **`SUPPLY-P2-001` line-level narrowing.** A line-scoped regex (`regexTarget`/`regexes`)
   for the `REDACTED` marker was attempted but did not suppress the hits under gitleaks
   8.30.1, so the two-file path narrowing was used; it is verified to keep tree *and* full
   history clean while catching new files.

## Not run

| Command | Reason |
|---|---|
| Live `docker image inspect` on the real host | The lab guest has no docker daemon and this is a read-only remediation; the new suite stubs `docker` and the finding's suggested fixture (two RepoDigests) is covered. |
| Scheduled lock refresh | Operational cadence; no scheduler in the repository (owner decision). |
