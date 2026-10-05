# Backup / restore drill plan — snowride @ `38b34a9`

Companion artifact for `32_backup_restore_drill.md`. The standing procedure is
`docs/runbooks/BACKUP_RESTORE.md`; this records the drill that must be re-run
per release candidate (finding `DR-P3-001`).

## Current state

- Standing backup: `pg_dump -Fc` + sha256 + tiered S3/DO Spaces rotation on the
  host cron (`infra/ops/crontab`: `0 4 * * *`).
- Launch gate records `LAUNCH_BACKUP_ID=snowride-20260923T033748Z.dump`.
- No dated drill transcript for commit `38b34a9` is committed under `evidence/`.

## Drill steps (append-only evidence)

1. Create a throwaway database and restore the most recent dump with
   `scripts/db.sh` (never raw `psql`).
2. Verify row counts for `profiles`, `runs`, `replay_objects`,
   `item_transactions` against the source snapshot.
3. Verify `replay_objects.digest_sha256` matches storage read-back for a
   sampled object.
4. Time dump -> restore -> verify; record observed RPO (dump age) and RTO.
5. Capture raw output under `evidence/<date>/backup-restore/` and link it here
   and from `docs/RELEASE_GATE.md`.

## Exit criteria

- A commit-bound drill transcript exists for the release candidate.
- RPO <= 24 h and the measured RTO is recorded and accepted by the owner.
