# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-006** closes the data persistence/durability findings reported against run
`20261003-0018-fix-trust-root-87532ec` (audit report `07_data_schema_migration_runtime_validation.md`).

On the base commit (`origin/main` `af6f83a`) one of the two findings was already closed by earlier
reconciliation work:

- **DATA-P2-001** — the idempotency table is no longer unbounded. `Store.prune()` now applies a
  7-day TTL to `idempotency.created_at` (`src/falcon_control/store.py`, `RETENTION_DAYS` /
  `RETENTION_COLUMNS`), and it runs at control-plane start-up and hourly via `_prune_loop`
  (`src/falcon_control/__main__.py`). It is covered by
  `tests/phase2/test_store_lifecycle.py::test_prune_removes_only_rows_past_retention` (asserts one
  expired and one fresh idempotency row) and `test_prune_covers_control_datasets_and_audits_deletion`.

This PR closes the **residual** finding:

- **DATA-P3-001** — queue age-expiry was evaluable only on `enqueue` (`_evict`), while
  `BoundedQueue.purge_expired()` was reachable only from tests. A queue that stopped receiving new
  work could retain items past `max_age_seconds` and ship stale data late. `Agent.cycle()` now calls
  `self.queue.purge_expired()` at the start of every cycle, and a regression test proves a cycle
  purges an expired item with no new enqueue.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-006` — persistence/durability: idempotency retention + queue age-expiry
- Repo / base: `falcon-edge` @ `origin/main` (`af6f83a`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P2-001` | P2 | open -> already fixed on base (verified) | `Store.prune()` gives `idempotency` a 7-day TTL and is invoked at start-up + hourly (`__main__._prune_loop`); asserted by `tests/phase2/test_store_lifecycle.py`. No new code needed in this PR. Residual "cap stored body size" is not implemented and is called out as an open question. |
| `DATA-P3-001` | P3 | open -> fixed | `Agent.cycle()` now calls `queue.purge_expired()` every cycle; new `test_cycle_purges_expired_queue_items` fails when the call is removed. |

## Changes

| File | What changed |
|---|---|
| `src/falcon_agent/runner.py` | `Agent.cycle()` calls `self.queue.purge_expired()` before the first network operation, so age-expiry is enforced every cycle rather than only opportunistically on enqueue (DATA-P3-001). |
| `tests/phase3/test_agent_integration.py` | New `test_cycle_purges_expired_queue_items`: enrol, enqueue+bankrupt an item's age, run a cycle, assert `droppedTotal` advanced and the expired item is not delivered. |

No other application code, workflows, dependencies, or secrets changed. `src/falcon_control/store.py`
is in the patch-set file list but required no change because DATA-P2-001 is already implemented on the
base commit; this PR verifies it rather than re-implementing it.

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive` of the committed branch (preserves file
modes/LF); raw output and exit codes are in `remediation/PS-006/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM (pytest 7.4.4) | 0 (130 passed) | `remediation/PS-006/verify.log` |
| `python3 -m pytest -q tests/phase3/test_agent_integration.py -k cycle_purges` (negative control: purge call neutralized, then restored) | edge-builder VM (pytest 7.4.4) | 1 (1 failed, as intended) | `remediation/PS-006/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-006/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-006/verify.log` |

- Secret scan (gitleaks 8.30.1): **pass** — "no leaks found".
- Scope check: **pass** — only `src/falcon_agent/runner.py` (patch-set file) plus the Phase-3
  regression test changed.
- Negative control: with `self.queue.purge_expired()` neutralized, the new test fails
  (`AssertionError: 0 != 1`) and the stale event is delivered; restored immediately after. This
  demonstrates the test actually guards DATA-P3-001 and is not vacuously passing.

The patch-plan verification is "TTL prune test; queue purge-on-cycle test". The TTL prune test is
the existing `tests/phase2/test_store_lifecycle.py` retention suite (DATA-P2-001, green in
`verify.log`); the queue purge-on-cycle test is the new Phase-3 test (DATA-P3-001), shown to fail
without the fix.

## Evidence bundle

- `remediation/PS-006/diff.patch` — SHA-256 `5c693becbf3de7a83554055dd012349cadedfd3377d817c34e10c559dc728bed`
- `remediation/PS-006/manifest.json`
- `remediation/PS-006/verify.log`

## Risk and rollback

- Risk: **low**. A single idempotent call (`purge_expired`) at the top of `Agent.cycle()` that only
  deletes queued items already past `max_age_seconds` and accounts for them as drops; plus an
  additive test. No control-plane schema/data changes, no change to delivered-but-fresh items.
- Rollback: `git revert 8f6999d` removes the call and the test; the queue returns to enqueue-time-only
  expiry. No persisted state or migration is affected.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md`: "TTL prune test; queue purge-on-cycle test" — met. DATA-P2-001's TTL prune is
present on the base commit and green in `tests/phase2/test_store_lifecycle.py`; DATA-P3-001's
purge-on-cycle behavior is implemented and proven by the new Phase-3 regression test, all green in
`verify.log`.

## Open questions

- DATA-P2-001's recommended fix also mentioned "cap stored body size". The TTL prune is implemented,
  but `idempotency.response_body` is still stored in full. Capping it would change replay semantics
  for large responses and needs an owner decision; deferred, not guessed.
