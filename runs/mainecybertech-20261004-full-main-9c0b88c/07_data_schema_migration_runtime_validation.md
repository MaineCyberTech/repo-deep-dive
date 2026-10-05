# 07_data_schema_migration_runtime_validation — Prompt 07 - Data, Schema, Migration, and Runtime Validation Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `07_data_schema_migration_runtime_validation.md` (area DATA, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| DATA-P1-001 | P1 | Approved-membership RLS predicate reintroduced six times; pending/suspended members could access tenant data |
| DATA-P1-002 | P1 | `retention` worker task performs unbounded deletes and reports success on partial failure |
| DATA-P1-003 | P1 | Soft-delete columns remain dead schema; DELETE endpoints hard-delete |
| DATA-P2-001 | P2 | Blanket `anon` DML grant + default privileges make every future table anon-writable unless RLS happens to stop it |
| DATA-P2-002 | P2 | Destructive table-replacement migrations are not transaction-wrapped |
| DATA-P2-003 | P2 | `orphan-cleanup` deletes storage objects based on a truncated listing |
| DATA-P2-004 | P2 | Migration CI dry-run diff is non-blocking; drift is never gated |
| DATA-P2-005 | P2 | `audit_logs` org-delete cascade destroys compliance history; 365-day purge has no archive |
| DATA-P2-006 | P2 | Several stores lack a retention policy and owner |
| DATA-P3-001 | P3 | Pre-baseline policies created without a preceding `drop policy if exists` |
| DATA-P3-002 | P3 | Migration version gaps undocumented; brief states 141 migrations, tree has 127 |
| DATA-P0-001 | P0 | Orphan cleanup can recursively delete a bucket’s contents |
| DATA-P2-007 | P2 | Generated DB types / schema can drift from migration intent |
| DATA-P2-008 | P2 | Orphan cleanup reference query is unbounded in the object list |
