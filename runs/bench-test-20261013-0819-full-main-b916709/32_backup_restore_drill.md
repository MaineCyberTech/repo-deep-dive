# 32_backup_restore_drill — Prompt 32 - Backup and Restore Drill Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `32_backup_restore_drill.md` (area DR, prompt)

## Verification Performed

# 32_backup_restore_drill - 32_backup_restore_drill.md

Domain subagent `32_backup_restore_drill` (area DR), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - No backup of the control-plane SQLite database, which is the single system of record** (confidence: High)
  - `server/benchd.py:50 - DEFAULT_DB = server/data/benchd.sqlite; server/benchd.py:94-143 - one SQLite file holds every run, phase, telemetry row, log, event, artifact (base64), command, schedule and runner (with its api_key).`
  - `.gitignore:27 - 'server/data/' is excluded from version control, so the database exists in exactly one place on the lab box and nowhere else.`
  - `docs/CONTROL_PLANE.md:254 - the only retention statement is 'SQLite uses WAL; the DB grows ~1 row/second per active run (fine for a lab)'; there is no size cap, prune, rotation or archival.`
  - `Repo-wide grep for backup/rsync-of-db/vacuum/pg_dump/mysqldump/.bak found no backup script, timer, systemd unit or documentation that copies or snapshots benchd.sqlite; server/benchd.service:1-21 has no backup ExecStartPre/OnCalendar unit.`
  - Impact: Loss of the lab box, the LXC container, or the disk destroys all fleet history (runs, telemetry, artifacts, verdicts, schedules, runner identities/keys) with no copy to restore from. Ships in the Proxmox lab alongside the WireGuard overlay, so a node loss is a realistic scenario.
  - Recommendation: Add a documented, scheduled backup of benchd.sqlite using the online-backup API (sqlite3 '.backup' or VACUUM INTO) rather than a raw cp of a WAL database, writing timestamped copies off the host; ship a systemd timer + a small stdlib script (e.g. server/backup_benchd.sh/.py), set a retention count, and reference it from docs/CONTROL_PLANE.md. Add an integrity check (PRAGMA integrity_check) on the backup.
- **P1 - Restore is never exercised: no restore script, runbook, or test; the only import path cannot rebuild the DB** (confidence: High)
  - `server/import_results.py:2-14 - import_results.py only backfills *completed run directories* into a live server; it is one-way and only accepts the library file shapes (Windows manifest.json, Linux report + runs-index.jsonl).`
  - `server/import_results.py:194-217 - upload_run only POSTs phase/telemetry/artifact/finish; there is no GET/export of runs, telemetry, artifacts or the SQLite file, so the DB cannot be reconstituted from the importer's own inputs.`
  - `tests/run_all.py:26-28 - the suite covers control-plane API, reporting, presets, dashboards, soak, version, bootstrap and packaging; there is no restore/recovery module, and grep found no test that re-imports or restores a database.`
  - `No file matching restore/recover/dr-* exists in the tree (glob/grep); docs/ contains only METHODOLOGY, CONTROL_PLANE, FUTURE_WORK, PHASE_TIMINGS, DATA and the prior audit folder.`
  - Impact: The DR capability is 'configured at best and not exercised at all' - in fact not even configured. A backup without a rehearsed restore is unverified; here there is neither. Operators have no steps to bring the control plane back after data loss, and no measured RTO.
  - Recommendation: Write docs/DR_RUNBOOK.md with an explicit backup->restore procedure, add a `restore_benchd` step (drop-in replacement DB + service restart), and add a test (e.g. tests/test_backup.py) that backs up a populated test DB, deletes it, restores it, and asserts row counts + an artifact sha256 match. Record the last real restore date in the runbook or a status file so 'not exercised' can never silently persist.
- **P2 - Destructive deletes purge run data irreversibly with no snapshot, soft-delete, or confirmation** (confidence: High)
  - `server/benchd.py:665-670 - DELETE /api/v1/runs/<id> runs 'DELETE FROM phases|telemetry|events|artifacts WHERE run_id=?' then 'DELETE FROM runs WHERE id=?'; no export, tombstone or backup is taken first.`
  - `server/benchd.py:673-680 - DELETE /api/v1/runners/<id> removes that runner's commands and schedules and the runner row, so even scheduling/command history is lost.`
  - `server/import_results.py:379,385-390 - the importer's '--reset' flag deletes every existing run on the server ('DELETE /api/v1/runs/%s') before importing, i.e. a bulk wipe, again with no backup step.`
  - `docs/CONTROL_PLANE.md:132 - these DELETE routes are documented operator actions but no undo/backup is described.`
  - Impact: A single mistaken DELETE (or a mis-run --reset during a backfill) permanently destroys the run history, telemetry and attached artifacts that are the toolkit's evidence base, and there is no copy to recover from. This directly amplifies the missing-backup finding.
  - Recommendation: Make destructive deletes take a snapshot to a trash/backup location first (or implement soft-delete with a deleted_at column and a retention purge), require an explicit confirm flag / typed confirmation for bulk operations, and print the backup path on success. Have --reset archive rather than drop.
- **P2 - Schema has no version record and migrations are additive-only with no rollback path (bad-migration drill impossible)** (confidence: High)
  - `server/benchd.py:159-176 - _migrate() only issues 'ALTER TABLE ... ADD COLUMN' guarded by PRAGMA table_info; there is no schema_version table, no migration list, and no down/reverse migration.`
  - `server/benchd.py:155 - startup runs executescript(SCHEMA) then _migrate() and commits; a partially-applied or wrong migration has no documented recovery or downgrade.`
  - `tests/run_all.py:26-28 - no migration test exists; the DB is created fresh in tests/harness.py:59-60, so additive migrations and upgrade-from-old-schema are never exercised.`
  - Impact: A future migration that drops/renames a column or runs a data fix cannot be rolled back, and there is no way to record or verify which schema version a given database is at. The required 'bad migration drill' cannot be performed, and a botched deploy is unrecoverable without a backup (which does not exist).
  - Recommendation: Introduce a schema_version table and numbered, forward+reverse migrations (or document 'additive-only' as an explicit, tested constraint), add a test that opens an old-schema DB and migrates it, and add a documented rollback/restore step to the DR runbook. Bind each migration to the app commit that introduced it.
- **P2 - Secrets have no backup/recovery or rotation procedure (per-runner keys live only in the DB)** (confidence: Medium)
  - `server/benchd.py:98 - runners.api_key column; server/benchd.py:1203-1204 - the per-runner key is generated with secrets.token_urlsafe(32) and stored only in the SQLite row; benchd.py:1217 returns it once at registration.`
  - `docs/CONTROL_PLANE.md:204-212 - runners store their key in ~/.config/bench-agent.json and the operator token lives in server/benchd.conf // etc/benchd.conf, both git-ignored; there is no documented backup or safe recovery of the token/key material.`
  - `README.md:362 and AGENTS.md:181 - the only secret guidance is 'rotate it if a stick leaves the lab'; there is no rotation/backup runbook and no re-issue path for a lost operator token.`
  - `No secret-manager, vault, sops/age or sealed-secret usage exists in the tree (grep).`
  - Impact: Losing the DB loses every per-runner key (runners must re-register), and losing /etc/benchd.conf loses the only operator credential with no documented recovery - an availability failure on top of the data-loss finding. There is also no way to back up secrets encrypted and separately from the data.
  - Recommendation: Document token/key backup, storage and rotation in the DR runbook (e.g. keep the operator token in a password manager / sealed secret, back it up separately from the DB), add a re-issue/regenerate path for the operator token, and note how runner keys are recovered after a DB restore.
- **P2 - No encryption at rest for the database, artifacts, or (hypothetical) backups** (confidence: Medium)
  - `server/benchd.py:154 - the only pragma applied is journal_mode=WAL / synchronous=NORMAL; there is no SQLCipher/encryption and the file is a plaintext SQLite DB.`
  - `server/benchd.py:126-129,1137-1141 - uploaded files are stored as base64 text in the artifacts.content column inside the same plaintext DB (reports, telemetry CSV, sensors dumps, screenshots), so 'file storage' and the database share one unencrypted file.`
  - `bench/Get-EnvInfo.ps1:45 - the toolkit records BitLocker status of the *tested host* but there is no requirement, check or doc that the benchd host's disk/DB is encrypted.`
  - Impact: The DB contains secrets (per-runner api_keys) and potentially sensitive host inventory/telemetry; both are readable in cleartext by anyone with host or backup-media access. Any future backup inherits the same exposure.
  - Recommendation: Document an at-rest encryption requirement for the control-plane host/volume (full-disk/LUKS), or move secrets out of the DB (env/sealed file); if encrypted backups are added, specify the key handling and test a decrypt-on-restore. Note the base64 limitation explicitly (it is encoding, not encryption).
- **P3 - No DR runbook and no infrastructure-config backup; deployment is imperative/manual** (confidence: Medium)
  - `docs/CONTROL_PLANE.md:168-187 - deployment is a hand-run sequence of 'pct create/push/exec' commands with a password literal; there is no IaC (Terraform/Ansible/compose) and no step that captures or backs up the resulting container/config.`
  - `server/benchd.service:1-21 - the unit is in-repo but /etc/benchd.conf is created by hand (docs/CONTROL_PLANE.md:44-46) and never captured; losing the container loses the unit + config unless reconstructed from docs.`
  - `server/benchd.py:233-264,267-282 - the deployed commit/version is read from .deployed-commit/.bench-version or a .git checkout, but the deploy steps at docs/CONTROL_PLANE.md:178-182 push neither VERSION nor a stamp, so a rebuilt container is not reproducible from the repo.`
  - `No file matching runbook/dr-roster/backup-plan exists in the tree.`
  - Impact: Rebuild relies on tribal knowledge: the exact unit, config, and deployed commit are not versioned, so 'restore the control plane' means manually re-running docs and hoping. RPO/RTO are undefined, so no one can say what is recoverable or how fast.
  - Recommendation: Version the deploy as code (a small script or Ansible playbook that also writes .deployed-commit/VERSION), include /etc/benchd.conf content as a sealed secret or template, and add docs/DR_RUNBOOK.md stating RPO/RTO, the backup schedule/retention, the restore steps, the validation checklist, and the last-tested date.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| DR-P1-001 | P1 | No backup of the control-plane SQLite database, which is the single system of record |
| DR-P1-002 | P1 | Restore is never exercised: no restore script, runbook, or test; the only import path cannot rebuild the DB |
| DR-P2-001 | P2 | Destructive deletes purge run data irreversibly with no snapshot, soft-delete, or confirmation |
| DR-P2-002 | P2 | Schema has no version record and migrations are additive-only with no rollback path (bad-migration drill impossible) |
| DR-P2-003 | P2 | Secrets have no backup/recovery or rotation procedure (per-runner keys live only in the DB) |
| DR-P2-004 | P2 | No encryption at rest for the database, artifacts, or (hypothetical) backups |
| DR-P3-001 | P3 | No DR runbook and no infrastructure-config backup; deployment is imperative/manual |
