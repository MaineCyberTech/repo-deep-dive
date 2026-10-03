# Backup / Restore Drill Plan — Snowride

Based on `docs/runbooks/BACKUP_RESTORE.md` (host crontab `backup_snowride.sh`, `pg_dump -Fc`, S3 tiered rotation, `pg_restore`).

## Objective

Prove a release can be recovered within an agreed RPO/RTO. No RPO/RTO is currently documented — set one (proposed: RPO ≤ 24 h, RTO ≤ 2 h) before the drill.

## Prerequisites

- Latest `/home/user/backups/snowride-<UTC>.dump` + `.sha256`.
- A scratch Postgres 17 container (never restore into production first).

## Procedure

1. Record `LAUNCH_BACKUP_ID` and the dump's sha256; verify `sha256sum -c`.
2. Start scratch Postgres (`docker run … postgres:17-alpine`).
3. `pg_restore --no-owner --no-privileges --clean --if-exists` into scratch.
4. Verify: row counts on `runs`/`profiles`/`inventories`; one anonymous sign-in; one `/runs` submission against the scratch stack.
5. Verify RLS on scratch (own-row SELECT; cross-user denial).
6. Record timings; append an append-only evidence entry.

## Success criteria

- Restore completes; counts match the source snapshot; RLS holds; a submission classifies.
- Measured restore time ≤ RTO.

## Notes / risks

- The assurance freshness check was fixed to `*.dump` (audit-20260927), but `BACKUP_RESTORE.md` still calls it "known-broken" (HYG-P2-003) — correct the doc before relying on it.
- "Configured" ≠ "exercised": this plan is a plan, not evidence of a recent successful restore.
