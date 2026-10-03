# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **PS-007** closes the data schema/migration findings reported against run
`20261003-0018-fix-trust-root-87532ec` (audit report `07_data_schema_migration_runtime_validation.md`).

On the base commit (`origin/main` `f5811d1`) the core of both findings is **already implemented**
by earlier reconciliation commit `85a1097` ("review-fix: control-plane data lifecycle - retention,
migrations, foreign keys"):

- **DATA-P2-003** — the store is versioned via `PRAGMA user_version` and a migration 0 -> 1 runs at
  startup (`Store._migrate`); a pre-foreign-key database is rebuilt in place, orphans removed, and
  the version asserted in `tests/phase2/test_store_lifecycle.py::MigrationTests`.
- **DATA-P2-002** — foreign keys with `ON DELETE CASCADE` now exist on every sensor-scoped table and
  `PRAGMA foreign_keys=ON` is set on every connection; retention covers `state_reports`, `events`,
  `heartbeat_samples` and `inventory` (`RETENTION_COLUMNS` / `Store.prune()`), with FK-violation and
  cascade tests in `ForeignKeyTests`.

This PR closes the **residual** item the same finding names but the base does not yet implement:
**`audit_log` had no retention**, so the append-only audit table (and the `retention.pruned` entries
the retention job writes into it) grew without bound.

- Audit run: `20261003-0018-fix-trust-root-87532ec`
- Patch set: `PS-007` — data schema / migration correctness
- Repo / base: `falcon-edge` @ `origin/main` (`f5811d1`)
- Findings: `DATA-P2-002`, `DATA-P2-003`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `DATA-P2-002` | P2 | open -> fixed | FKs + `foreign_keys=ON` + retention for `events`/`state_reports`/`heartbeat`/`inventory` already on base (verified); this PR adds the missing **`audit_log`** retention window and its index, an explicit recommendation of the finding. |
| `DATA-P2-003` | P2 | open -> already fixed on base (verified) | `PRAGMA user_version` migration 0 -> 1 applied at startup; migration/reopen idempotency now also asserted by a new test. No migration framework change needed beyond this. |

## Changes

| File | What changed |
|---|---|
| `src/falcon_control/store.py` | `RETENTION_DAYS["audit_log"] = 365` (proposed) and `("audit_log", "at")` added to `RETENTION_COLUMNS`, so the existing hourly `Store.prune()` job bounds the audit log; new `idx_audit_log_at` supports the prune. Idempotent `CREATE INDEX IF NOT EXISTS` statements are (re)applied on every open so a database created before an index existed still receives it without a schema-version bump. Docstrings updated. |
| `tests/phase2/test_store_lifecycle.py` | New `test_prune_applies_audit_log_retention` (old audit row pruned, recent kept) and `test_reopen_is_idempotent_and_reapplies_indexes` (reopen is a no-op that preserves rows and re-adds an index dropped from an older DB). |

No `migrations/` directory is added: DATA-P2-003's mechanism is already in-code on the base and is
verified here rather than re-implemented (the patch-plan file list allows it; refactoring to a
directory would be churn). No workflows, dependencies, API, or secrets change.

## Verification Performed

All commands ran on the **edge-builder VM** (`172.23.128.52`, Ubuntu 24.04, Python 3.12.3,
pytest 7.4.4, gitleaks 8.30.1) against a `git archive --format=tar.gz` of the committed branch
(preserves modes/LF); raw output and exit codes are in `remediation/PS-007/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `python3 -m pytest -q tests/phase2 tests/phase3` | edge-builder VM (pytest 7.4.4) | 0 (131 passed) | `remediation/PS-007/verify.log` |
| `python3 -m pytest -q tests/phase2/test_store_lifecycle.py` | edge-builder VM (pytest 7.4.4) | 0 (8 passed) | `remediation/PS-007/verify.log` |
| `bash ci/validate.sh` | edge-builder VM | 0 (`validation: ALL PASS`) | `remediation/PS-007/verify.log` |
| `gitleaks detect --no-git --redact --source . -v` | edge-builder VM (gitleaks 8.30.1) | 0 (no leaks found) | `remediation/PS-007/verify.log` |

- Secret scan: **pass** — "no leaks found".
- Scope check: **pass** — only `src/falcon_control/store.py` (patch-set file) plus the Phase-2
  regression tests.

The patch-plan verification is "migration round-trip test; FK violation test". Both already exist on
the base and are green in `verify.log` (`MigrationTests.test_v0_to_v1_rebuilds_with_foreign_keys`,
`ForeignKeyTests.test_fk_violation_rejected_and_cascade_deletes`); the added tests extend them to the
new `audit_log` retention and migration idempotency.

## Evidence bundle

- `remediation/PS-007/diff.patch` — SHA-256 `8cf56ad5340794ba41a92f9b3fdadb7a63d5e1ce10ba9bbd2e2a6d4d83ba7794`
- `remediation/PS-007/manifest.json`
- `remediation/PS-007/verify.log`

## Risk and rollback

- Risk: **low**. Additive retention for one append-only table on a long (365 d) window; rows newer
  than the window are untouched. The index is created with `IF NOT EXISTS` and applied on open, so
  old databases gain it without a version bump. The prune deletion is itself recorded in `audit_log`.
- Rollback: `git revert` removes the retention entry, the index and the tests; the schema and all
  retained data remain valid (no destructive migration).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

- The `audit_log` window (`365 d`) is marked *proposed* in code, matching the repo convention for the
  other retention windows and the earlier audit's "audit 365 d" recommendation. It is configurable
  per call (`Store.prune(retention={...})`) and is not a hidden product decision, but owner
  confirmation (ED window) is still desirable before it is treated as final policy.

## Definition of done (for this set)

From `patch_plan.md`: "migration round-trip test; FK violation test" — the existing migration and
FK/cascade tests are green, and the residual `audit_log` retention recommended by DATA-P2-002 is
implemented and covered by a new boundary test, all green in `verify.log`.
