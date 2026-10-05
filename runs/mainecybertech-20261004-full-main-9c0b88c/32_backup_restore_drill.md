# 32_backup_restore_drill — Prompt 32 - Backup and Restore Drill Audit

- Run: `mainecybertech-20261004-full-main-9c0b88c`
- Target: `mainecybertech` @ `9c0b88c` (branch `main`)
- Domain: `32_backup_restore_drill.md` (area DR, prompt)

## Verification Performed

Reconciliation full-domain pass at main `9c0b88c` (2026-10-04). Baseline findings were carried from the repository's committed audit corpus and re-bound to this run: the `a97425d` verification ledger (ancestor of main, so its verified-fixed statuses hold here), the `178b91c` main-tip focused run, and the `20261002-0344` full run for domains the later ledgers did not cover. Each row cites its provenance. Machine deterministic checks are recorded in `lens_deterministic.md`.

## Findings

| ID | Severity | Title |
|---|---|---|
| DR-P0-001 | P0 | Scheduled backup and restore-test workflows never run because they are absent from the default branch |
| DR-P0-002 | P0 | The restore test never asserts integrity and therefore cannot fail on a bad backup |
| DR-P1-001 | P1 | No backup or restore path exists for uploaded files in Supabase Storage |
| DR-P1-002 | P1 | Restore-test backup location contract (`S3_BACKUP_BUCKET`) is undocumented and can silently mismatch the backup script |
| DR-P1-003 | P1 | Database backups are unencrypted and stored in a single location with no offsite copy |
| DR-P1-004 | P1 | The restore test has no failure alert |
| DR-P1-005 | P1 | No automated migration reverse/rollback and no bad-migration drill |
| DR-P1-006 | P1 | RPO/RTO targets are documented but unvalidated, and the Postgres RPO conflates PITR with the daily dump |
| DR-P2-001 | P2 | Backup-failure alerting is present but cannot be trusted to deliver |
| DR-P2-002 | P2 | Terraform state bucket versioning is claimed but not backed by any resource |
| DR-P2-003 | P2 | The backup/DR runbook and module docs describe a client-facing product, not the platform's own recovery, and the module doc is stale |
| DR-P2-004 | P2 | Manual restore has no environment guardrail and the transient dump is written unencrypted to `/tmp` |
| DR-P2-005 | P2 | The product `backup_status` module is not wired to any real platform backup heartbeat |
| DR-P3-001 | P3 | Duplicate backup-script logic in bash and PowerShell risks drift |
| DR-P3-002 | P3 | Unpinned Postgres image in the restore test; no explicit jq/aws tool pinning in the backup job |
| DR-P3-003 | P3 | Documented backup/DR export endpoints do not exist |
