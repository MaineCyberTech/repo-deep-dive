# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U13` (unassigned TEST findings) for the run
`20261003-0018-fix-backup-abort-markers-20b5e57`. After checking `origin/main`
(`430da82274af4c0821542627fdb9e6ab74afa826`), part of the testing-confidence work was
already on `main` from the 2026-10-01 review-fix wave (the offline shell-test gate and the
`docs/phase9/TEST_PROCEDURES.md` provenance policy), but each of the three audit findings
still had an unimplemented, actionable part. This PR adds the missing guards/tests:

- `TEST-P1-001` (open) - **fixed here**: add an offline ledger-provenance guard plus an
  explicit legacy allowlist. New `ledgers/test_execution.csv` rows whose command uses an
  absolute `/home/` or `/tmp/` path must be allowlisted by the SHA-256 of their raw
  evidence artifact; the historical rows are marked, not rewritten.
- `TEST-P1-002` (open) - **fixed here**: add `python3 ci/validate.py --fast`, a bounded
  smoke subset (parsers, compose pins, gate ledger, credential sourcing, shell syntax)
  that runs in ~2s on Linux with no evidence tree, network, docker or root, and document
  it.
- `TEST-P2-001` (open) - **fixed here**: add `automation/validation/tests/backup_e2e_test.sh`,
  an offline end-to-end suite that runs `bootstrap/80-offsite-backup.sh` `main()` against a
  fake OpenSearch snapshot API (`docker` stub) and a fake object store (`rclone` stub) and
  asserts the freshness stamp plus the abort/dead-letter marker lifecycle.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U13` - Unassigned TEST findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u13-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `ed2f739a05030a860b06f9f4e58b58d054fd28ca`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `TEST-P1-001` | P1 | open -> partially-fixed (draft PR) | `ledgers/test_execution.csv` stays append-only; its 464 historical host-path rows are explicitly marked in `automation/validation/ledger_provenance_legacy.sha256` (457 unique raw-artifact hashes). A new absolute-path row that is not allowlisted fails `ledger_provenance_test.sh`. Policy documented in `TEST_PROCEDURES.md` §3. |
| `TEST-P1-002` | P1 | open -> partially-fixed (draft PR) | `ci/validate.py --fast` is a documented bounded subset (measured ~2s on the lab). The full gate remains the release authority. The "container image for the gate" part of the finding is deferred (infra/owner decision). |
| `TEST-P2-001` | P2 | open -> partially-fixed (draft PR) | The offsite lifecycle now runs end to end in the gate: newest SUCCESS snapshot selection, repository upload, SHA-256 read-back, full size verification, freshness stamp, and the abort/dead-letter marker lifecycle (success, SIGTERM, probe failure, recovery). The `85` snapshot-creation leg is not driven offline yet (see deferred). |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and its evidence requirements are met.

## Changes

| File | What changed |
|---|---|
| `ci/validate.py` | New `--fast` mode backed by `FAST_CHECKS` (parsers, compose-pins, gate-ledger, credential-sourcing, shell-syntax); usage and docstring updated. `--only` is unchanged. |
| `docs/phase9/TEST_PROCEDURES.md` | Document `--fast`; add the two suites to the durable-suite index; state the repo-relative-row policy and the provenance enforcement. |
| `automation/validation/tests/backup_e2e_test.sh` | New offline e2e suite (22 checks) driving `80-offsite-backup.sh` `main()` with fake snapshot API + fake object store. |
| `automation/validation/tests/ledger_provenance_test.sh` | New offline provenance guard over `ledgers/test_execution.csv` + the legacy allowlist. |
| `automation/validation/ledger_provenance_legacy.sha256` | Explicit allowlist of historical host-path raw-artifact SHA-256 values (457; 464 rows). |
| `automation/validation/tests/remediation_guards_test.sh` | Pin the `--fast` subset, the provenance guard/allowlist, and the backup e2e suite so they cannot silently regress. |

Scope: `ci/validate.py`, one docs file, and four `automation/validation/` test/allowlist
files. No runtime service, workflow, dependency, schema, ledger or lockfile change.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced
with `scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U13/verify.log` (commit `ed2f739`). The lab tar extraction sets
`core.fileMode=false`, so the tracked mode-100755 files were `chmod +x`'d before the gate
(592 files).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` - `validation_failures=0`; 32/32 shell suites incl. the two new ones; shell syntax 602 scripts; shellcheck 174 scripts; secret scan; edge-pin skipped |
| `python3 ci/validate.py --fast` | lab `ci-runner` | 0 | `verify.log` - 5 checks, `validation_failures=0`, ~2s (`time` real 0m1.951s on the earlier run) |
| `bash automation/validation/tests/backup_e2e_test.sh` | lab `ci-runner` | 0 | `verify.log` - `backup_e2e_test_checks=22 backup_e2e_test_failures=0`; cases 2 (SIGTERM) and 3 (probe failure) are built-in negative controls |
| `bash automation/validation/tests/ledger_provenance_test.sh` | lab `ci-runner` | 0 | `verify.log` - `PASS ledger_provenance (rows=1127; absolute_path_rows=464; allowed_legacy_hashes=457)` |
| Negative control: append a new absolute-path row, then run the guard | lab `ci-runner` | 1 (expected) | `verify.log` - `FAIL ledger_provenance ... /tmp/opencode/new-absolute-proc.sh` |
| Restore the ledger, then run the guard | lab `ci-runner` | 0 | `verify.log` - `PASS ledger_provenance` (ledger restored byte-for-byte via backup copy) |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` - `no leaks found` (~52 KB scanned) |

- Secret scan (gitleaks): **pass** - no leaks on the diff.
- Scope check: **pass** - only the six files above.
- The negative control's ledger edit was made in the lab worktree and restored from a
  backup copy before the final guard run; the committed ledger is unchanged.

## Evidence bundle

- `remediation/PS-U13/diff.patch` - SHA-256 `287c3ee9202a98ab3b25e445457f90c436bd04e34aa5231b95f0a9ba7499a88f` (106,814 bytes)
- `remediation/PS-U13/verify.log`
- `remediation/PS-U13/manifest.json`
- `remediation/PS-U13/pr_body.md`

## Risk and rollback

- Risk: **low**. Three offline test/allowlist files and one additive CLI flag; no runtime
  behaviour, service, or delivery artifact changes. The `--fast` flag is opt-in; the full
  gate is unchanged. The provenance allowlist only constrains future ledger captures. The
  backup e2e suite stubs `docker`, `rclone` and `id` and touches nothing outside
  `/tmp/opencode`.
- Rollback: `git revert ed2f739a05030a860b06f9f4e58b58d054fd28ca`.

## Review checklist

- [ ] Diff touches only the patch-set files (no runtime/data/service edits)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] The provenance negative control proves the new guard fails closed
- [ ] No secrets added; gitleaks clean on the diff
- [ ] `--fast` is an acceptable smoke subset (full gate remains the release authority)
- [ ] Rollback is practical

## Open questions / deferred

1. **`TEST-P1-002` gate container image.** The audit asked for a documented fast subset and
   a container image for the gate. The fast subset (`--fast`, plus the existing `--only`)
   is implemented and documented; baking a gate image changes the build/release model and
   CI runner assumptions, so it is left as an infrastructure/owner decision.
2. **`TEST-P2-001` full `85` snapshot-creation leg in the offline gate.** The e2e added
   here drives `80-offsite-backup.sh` `main()` (snapshot selection -> upload -> read-back ->
   retention -> freshness/marker lifecycle). Executing `85-backup-job.sh` itself offline
   would require making its hardcoded `/srv` paths and helper-script calls overridable, and
   `85` is being changed by the open `PATCH-1`/`PATCH-2` abort-contract PRs. To avoid an
   overlapping/conflicting change, this is deferred as a sequencing/owner decision and
   recorded as `partially-fixed`.
3. **`TEST-P1-001` ledger format.** The finding's alternative "add a repo-relative
   command/procedure column (or a resolver)" would regenerate `ledgers/test_execution.csv`
   from the off-repo evidence tree, which is not available in CI and would rewrite
   historical rows. The guard plus explicit allowlist closes the "flag new absolute paths"
   validation without rewriting history; whether to add a derived column is a ledger-format
   owner decision.

## Not run

| Command | Reason |
|---|---|
| `85-backup-job.sh` offline orchestration | `85` hardcodes `/srv/falcon` paths and calls repo scripts by absolute path; making it testable overlaps the open `PATCH-1`/`PATCH-2` changes to the same file (sequencing/owner decision). The offsite leg (`80`) is covered end to end. |
| Gate container image build | infrastructure/owner decision (no container policy in the patch set). |
