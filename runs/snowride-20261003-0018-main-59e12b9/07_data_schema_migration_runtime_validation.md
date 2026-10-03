# 07 Data, Schema, Migration & Runtime Validation

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Schema integrity, migration ordering and drift, RLS/grants verification, and runtime validation of the data plane. Read-only; no database connection.

## Evidence Reviewed

- `supabase/migrations/0001`–`0056` (56 files; 0032 absent)
- `supabase/tests/0001`–`0016` (negative suites)
- `scripts/ci-migrations-dryrun.sh`, `.github/workflows/ci-foundation.yml`
- `infra/compose/docker-compose.yml` — launch attestation `LAUNCH_MIGRATION_HEAD`
- `docs/runbooks/MIGRATIONS.md`, `docs/runbooks/BACKUP_RESTORE.md`
- `evidence/closeout/EXCEPTION_REGISTER.md` (E3-003), `evidence/closeout/CLOSEOUT_REPORT.md`

## Verification Performed

- Enumerated migrations: last three files are `0054`, `0055`, `0056`; no `0032`.
- Read CI `migrations` job: applies all migrations to a fresh Postgres 17 stub (`ci-migrations-dryrun.sh`), `ON_ERROR_STOP=1`; it does not run `supabase/tests/*`.
- Compared repo migration head (`0056`) with the attestation head in compose (`LAUNCH_MIGRATION_HEAD: 0055_perf_sample_rate.sql`).
- Reviewed `0002` RLS/grants and `0017` guard conventions.

## Executive Summary

Migrations are ordered, idempotency-tested and applied to a fresh database in CI, which is the right baseline. Two gaps stand out. First, a concrete migration-head drift: the repository now contains `0056_hash_legacy_gpu.sql` while the production launch attestation and compose pin the migration head to `0055`, so the attested release does not cover the current schema head. Second, the 16 SQL negative suites that actually exercise RLS/grants are explicitly manual and not executed in CI, so RLS regressions would not be caught by the pipeline. There is no evidence-manifest/checksum for the migration set, and no production database was in scope.

## Inventory

| Item | Detail |
|---|---|
| Migrations | 56 files, `0001`–`0056` (0032 never existed) |
| SQL negative suites | 16 files, manual |
| CI migration job | fresh Postgres 17, `ON_ERROR_STOP=1` |
| CI RLS test job | none |
| Migration checksum manifest | none found |
| Live/prod schema | not in scope (E3-003) |

## Findings

### Finding ID: DATA-P1-001 - Attested migration head (0055) is one behind the repository head (0056)

- Severity: P1
- Confidence: High
- Area: DATA
- Evidence:
  - `supabase/migrations/0056_hash_legacy_gpu.sql` present
  - `infra/compose/docker-compose.yml` line 117 — `LAUNCH_MIGRATION_HEAD: "0055_perf_sample_rate.sql"`
  - `apps/realtime/src/config.ts` reads `LAUNCH_MIGRATION_HEAD`; gate compares it
- What is happening: The launch attestation binds to `0055`; the current commit ships `0056`.
- Why it matters: Either the deployed schema is un-attested relative to the code, or the attestation is stale — both break the "exact release identity" control.
- User / business impact: A release may be represented as verified while a migration is uncovered.
- Security / privacy / reliability impact: Schema-integrity / release-governance.
- Recommended fix: Re-attest at the current head (or explicitly document `0056` as post-attestation and re-run the gate); keep `LAUNCH_MIGRATION_HEAD` in lockstep with the newest migration.
- Suggested validation: A CI check asserts `LAUNCH_MIGRATION_HEAD` equals the lexically last migration file.
- Owner suggestion: Owner + release engineer
- Effort estimate: S
- Dependencies: SEC-P1-001, DATA-P2-002
- Status: open

### Finding ID: DATA-P2-001 - RLS/negative SQL suites are manual and not gated in CI

- Severity: P2
- Confidence: High
- Area: DATA
- Evidence:
  - `AGENTS.md` line 16 — "`supabase/tests` Manual SQL negative suites (not run in CI)"
  - `.github/workflows/ci-foundation.yml` — `migrations` job runs only `ci-migrations-dryrun.sh`
  - `supabase/tests/0001`–`0016` exist
- What is happening: The suites that prove deny-by-default RLS behavior are never executed by the pipeline.
- Why it matters: The most security-sensitive database control is validated only when a human remembers to run it.
- User / business impact: Silent RLS regression could expose tenant data.
- Security / privacy / reliability impact: Tenant isolation regression risk.
- Recommended fix: Run `supabase/tests/*.sql` in the CI `migrations` job after the dry-run (the job already has a fresh Postgres service).
- Suggested validation: CI fails when a deliberate RLS policy is weakened.
- Owner suggestion: DB/CI engineer
- Effort estimate: M
- Dependencies: None
- Status: open

### Finding ID: DATA-P2-002 - No migration checksum/manifest; gaps are only documented

- Severity: P2
- Confidence: High
- Area: DATA
- Evidence:
  - `supabase/migrations/` has no `.sha256`/manifest; the only manifest-like artifact is `evidence/MANIFEST.sha256` (per earlier review it once failed verification)
  - `0032` is absent with no in-repo tombstone file
- What is happening: There is no machine-verifiable digest list binding the migration files to a release.
- Why it matters: Detecting tampering or accidental edits requires manual diffing.
- User / business impact: Slower, less reliable release verification.
- Security / privacy / reliability impact: Integrity assurance gap.
- Recommended fix: Generate `supabase/migrations/MANIFEST.sha256` at release and verify it in CI.
- Suggested validation: Modify a migration and observe CI fail.
- Owner suggestion: DB/CI engineer
- Effort estimate: S
- Dependencies: DATA-P1-001
- Status: open

### Finding ID: DATA-P3-001 - Production database schema state is unverified in this audit

- Severity: P3
- Confidence: High
- Area: DATA
- Evidence:
  - `evidence/closeout/EXCEPTION_REGISTER.md` E3-003 — "live Supabase project is shared test; no production DB in scope"
  - `.env.example` / README describe hosted Supabase
- What is happening: No read-only production database was authorized for this audit.
- Why it matters: The recovered migration head cannot be confirmed against the live schema.
- User / business impact: Unknown drift.
- Security / privacy / reliability impact: Unknown.
- Recommended fix: Authorize a read-only `migration list`/schema dump for the next verification run.
- Suggested validation: Repo head == live `supabase_migrations.schema_migrations` head.
- Owner suggestion: Owner
- Effort estimate: S
- Dependencies: Owner authorization
- Status: open

## Risks

- R-DATA-1: Un-attested schema head in a "verified" release (P1).
- R-DATA-2: Un-gated RLS regression (P2).
- R-DATA-3: Undetectable migration tampering (P2).

## Recommendations

1. Re-attest / lock migration head and add a head-equality CI check.
2. Execute SQL negative suites in CI.
3. Add a migration checksum manifest.

## Quick Wins

- Add the head-equality check (S).
- Add SQL suites to the existing `migrations` CI job (M).

## Hardening Backlog

- Migration rollback compatibility matrix (`docs/runbooks/MIGRATIONS.md`).

## Suggested Tests

- CI: fresh-DB apply + `supabase/tests/*`; tamper-detection via manifest.

## Suggested Documentation Updates

- `AGENTS.md`, `docs/runbooks/MIGRATIONS.md`: record that suites now run in CI.

## Open Questions

- Why was migration `0032` skipped and is a tombstone required? (`Unknown`.)

## Appendix

- `ci-migrations-dryrun.sh` creates an `auth` stub and applies migrations in lexical order.
