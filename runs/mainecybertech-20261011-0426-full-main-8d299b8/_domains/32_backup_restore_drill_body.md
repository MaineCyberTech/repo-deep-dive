# Backup and Restore Drill Audit

## Audit Metadata

- Audit name: repo-deep-dive (full hardening rerun)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (read-only worktree `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` ("Merge PR #168: promote develop to main (metrics scrape fixes + register sync)")
- Generated at: 2026-10-11
- Auditor: domain subagent 32 (area DR)
- Area code: DR
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/32_backup_restore_drill.md` (pack-run copies: `_domains/32_backup_restore_drill.json` + `_body.md`)
- Scope limitations:
  - AUDIT-ONLY. No application, config, migration or infra file was modified; only the two run-folder outputs were written.
  - No backup, restore, decrypt, prune or destructive command was executed. Secret values were never read or printed.
  - GitHub Actions run history was read through the public (read-only) GitHub API to reproduce CI claims; job logs require authentication and were not retrievable, so the exact failure message inside the `db-backup` script step is inferred from the step timing + the script's fail-closed checks.
  - Live bucket state (Spaces versioning, object contents, IAM/ACL, Supabase PITR enablement) is operator-side and `Unknown` from the repository.
  - The product `backup_status` module (client backup tracking) is reviewed only where it intersects the platform's own DR.

## Scope

Reviewed at `8d299b8d`:

- **Database backups / restore:** `.github/workflows/db-backup.yml`, `db-restore-test.yml`, `backup-dispatch.yml`, `storage-backup.yml`, `.github/restore-test-baseline.env`, `scripts/backup-database.sh`, `scripts/backup-database.ps1`, `scripts/restore-database.sh`.
- **Storage / uploaded files:** `scripts/backup-storage.sh`, `scripts/restore-storage.sh`, `apps/worker/src/tasks/orphan-cleanup.ts` (retention context only).
- **Infra config / Terraform state:** `infra/terraform/digitalocean/providers.tf`, `env/backend.dev.hcl`, `env/backend.prod.hcl`, `docs/ROLLBACK_PROCEDURES.md` §4.
- **Migration rollback:** `.github/workflows/supabase-migrations.yml`, `docs/ROLLBACK_PROCEDURES.md` §3, `supabase/migrations/*` (ledger + rollback-relevant migrations).
- **Docs / RPO-RTO / runbooks:** `docs/RTO_RPO.md`, `docs/ROLLBACK_PROCEDURES.md`, `docs/runbooks/backup-disaster-recovery.md`, `docs/modules/backup-dr.md`, `docs/features/backup-disaster-recovery.md`, `docs/INCIDENT_RESPONSE.md`, `docs/PLATFORM_FAILURE_RUNBOOKS.md`, `docs/RELEASE_GATE.md`, `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, `docs/SECRETS_ROTATION.md`, `CHANGELOG.md`.
- **Validation / product surface:** `apps/worker/src/tasks/module-tasks.ts` (`backupDrCheck`), `apps/api/src/routes/final/backups.ts`, `final/crud.ts`, `apps/web/e2e/portal/backup-dr.spec.ts`, `supabase/seeds/*`.
- **CI evidence:** GitHub Actions run history for the four backup workflows (read-only API), and the previous run's DR register rows for the verification duty.

Not reviewed: live infrastructure, Supabase project settings/PITR enablement, bucket IAM/ACLs, droplet cron jobs outside the repo, operator machines, and anything requiring execution.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `.github/workflows/db-backup.yml` (66 lines) | Workflow | Daily `pg_dump` job | `environment: dev`; secrets from `dev`; ntfy notifier |
| `.github/workflows/db-restore-test.yml` (259 lines) | Workflow | Weekly restore verification | Baseline load, download/decrypt, throwaway Postgres, 6 assertion classes |
| `.github/workflows/storage-backup.yml` (76 lines) | Workflow | Daily upload mirror | Runs `scripts/backup-storage.sh` |
| `.github/workflows/backup-dispatch.yml` (111 lines) | Workflow | Scheduler→develop dispatcher | Needs `SCHEDULE_DISPATCH_TOKEN`; fails loudly without it |
| `.github/restore-test-baseline.env` (28 lines) | Config | Committed verification floors | 23 comment lines + 5 `KEY=VALUE` floors |
| `scripts/backup-database.sh` (138 lines) | Script | Canonical dump/encrypt/upload/prune | Fail-closed checks; AES-256-CBC; offsite copy |
| `scripts/backup-database.ps1` (136 lines) | Script | Windows helper | Marked NOT CANONICAL; no encryption/offsite |
| `scripts/restore-database.sh` (126 lines) | Script | Manual restore | `ALLOW_PROD_RESTORE` guard; plaintext `/tmp` staging |
| `scripts/backup-storage.sh` / `restore-storage.sh` (148/129 lines) | Scripts | Upload mirror + restore | Single-page listing; MANIFEST; no assertions |
| `infra/terraform/digitalocean/providers.tf`, `env/backend.*.hcl` | Infra | Terraform state location | S3/Spaces backend; buckets external; no versioning resource |
| `docs/RTO_RPO.md` (55 lines) | Docs | RPO/RTO + strategy + validation | PITR vs dump separated; operator actions listed |
| `docs/ROLLBACK_PROCEDURES.md` (277 lines) | Docs | Recovery runbook | DB/storage/Terraform restore, verification checklist |
| `docs/RELEASE_GATE.md:66-68` | Docs | Release criteria | Requires green `db-restore-test` + succeeding `db-backup` runs |
| `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:83-114` | Docs | Secret placement | Backup secrets marked Prod-only; workflows run in `dev` |
| `apps/worker/src/tasks/module-tasks.ts:278-331` | Code | Product backup monitor | Reads seeded `backup_status` only |
| GitHub Actions API (read-only) | CI evidence | Reproduce CI claims | 29/29 db-backup, 7/7 storage, 1/1 restore-test, dispatcher failing |

## Verification Performed

| Evidence / claim | Type | Why relevant | Outcome | Notes |
|---|---|---|---|---|
| Workflows present on the default branch (DR-P0-001) | Re-verify | Previous register row | **supported (verified-fixed)** | All four files at `8d299b8d`; schedules fire |
| Restore test asserts integrity (DR-P0-002) | Re-verify | Previous register row | **supported (verified-fixed)** | `db-restore-test.yml:135-232` + baseline floors |
| Storage backup/restore path exists (DR-P1-001) | Re-verify | Previous register row | **supported (verified-fixed)** | Workflow + both scripts present |
| S3_BUCKET/S3_PREFIX contract shared (DR-P1-002) | Re-verify | Previous register row | **supported (verified-fixed)** | Script + 3 workflows + docs agree |
| Encryption/offsite affordance (DR-P1-003) | Re-verify | Previous register row | **partially supported** | Code present; never exercised; operator key/bucket absent |
| Restore-test notifier (DR-P1-004) | Re-verify | Previous register row | **supported (verified-fixed)** | Ran on the failed 2026-10-05 run |
| Migration rollback + drift guard (DR-P1-005) | Re-verify | Previous register row | **partially supported** | Dry-run artifact + fail-closed drift; no reverse automation/drill |
| RPO/RTO doc separation (DR-P1-006) | Re-verify | Previous register row | **partially supported** | Docs fixed; no measured drill; CI never green |
| ntfy alert delivery (DR-P2-001) | Re-verify | Previous register row | **supported (verified-fixed)** | Wiring at HEAD; delivery exercised 2026-10-11 (run 38106946181) |
| Terraform state versioning claim (DR-P2-002) | Re-verify | Previous register row | **unsupported (still-open)** | No bucket resource; emergency doc names a different bucket |
| Runbook/module doc scope (DR-P2-003) | Re-verify | Previous register row | **partially supported** | Runbook banner added; module doc still stale |
| Manual restore guardrail (DR-P2-004) | Re-verify | Previous register row | **partially supported** | `ALLOW_PROD_RESTORE` added; plaintext `/tmp` staging remains |
| Product backup heartbeat (DR-P2-005) | Re-verify | Previous register row | **unsupported (still-open)** | `backupDrCheck` watches seeded rows only |
| Bash/PS duplicate scripts (DR-P3-001) | Re-verify | Previous register row | **partially supported** | NOT CANONICAL note; duplicate logic remains |
| Postgres image pinning (DR-P3-002) | Re-verify | Previous register row | **unsupported (still-open)** | `postgres:16-alpine` floating |
| Documented export endpoints (DR-P3-003) | Re-verify | Previous register row | **unsupported (still-open)** | `/backup-dr/*` docs vs `/final/backups*` code |
| Terraform state restore procedure (IR-P3-001) | Re-verify | Subject in DR scope | **unsupported (still-open)** | No procedure, wrong bucket name in doc |
| Backups actually run (headline) | Reproduce | CI claim | **unsupported — all runs fail** | GitHub API: 29/29 db-backup, 7/7 storage, 1/1 restore-test failed |

Exact commands run and observed results:

```text
git -C /tmp/opencode/mct-audit-target rev-parse HEAD      # 8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd
git ls-files .github/workflows | grep -E 'backup|restore'
# backup-dispatch.yml, db-backup.yml, db-restore-test.yml, storage-backup.yml
curl -s 'https://api.github.com/repos/MaineCyberTech/mainecybertech/actions/workflows/db-backup.yml/runs?per_page=100'
# 29 runs, conclusion=failure for all; oldest 2026-06-06, newest 2026-10-11 (manual 38106946181)
curl ... /actions/workflows/storage-backup.yml/runs        # 7 runs, 7 failures (2026-10-05..2026-10-10)
curl ... /actions/workflows/db-restore-test.yml/runs       # 1 run, failure (2026-10-05, run 37323743344)
curl ... /actions/runs/38106946181/jobs                    # 'Run database backup script' failed in <1s; 'Notify on failure' succeeded
curl ... /actions/runs/37323743344/jobs                    # 'Load restore-test baseline' failed; steps 4-9 skipped
curl ... /check-runs/111809078989/annotations              # Invalid format '# Baseline thresholds...'; env file command failed
curl ... /actions/runs/38046405190/jobs                    # backup-dispatch fails at 'Require a dispatch token'
grep -rn 'SUPABASE_DB_URL' .github scripts docs            # workflow:21, script:39-40, CHANGELOG:198, matrix:87
grep -rn 'restore-storage|storage-restore' .github/        # no CI job exercises storage restore
grep -n 'spaces_bucket|digitalocean_spaces' infra/terraform/*.tf   # 0 bucket resources
git diff 5241a9be HEAD -- .github/workflows/db-restore-test.yml    # only the notifier block changed
```

## Executive Summary

The DR tooling is far better documented and coded than at the original audit — encryption, offsite copy, destination contract, restore assertions, failure alerts and rollback docs all exist. **None of it has ever worked in practice.** Every CI run of the database backup (29/29 since 2026-06-06), the storage mirror (7/7) and the restore test (1/1) has failed; the dispatcher that was supposed to make the schedules fire fails because `SCHEDULE_DISPATCH_TOKEN` is unset. The repo itself records why: `CHANGELOG.md:191-200` lists `SUPABASE_DB_URL`, `BACKUP_ENCRYPTION_KEY` and the backup bucket as "still required from the operator", and `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:87-91` still documents those secrets as Prod-only even though the workflows now attach `environment: dev` — a contract mismatch that guarantees the jobs cannot resolve their configuration.

Three new defects compound the picture: the weekly restore test fails before it can verify anything because it appends a commented `.env` file to `$GITHUB_ENV` (runner rejects it as "Invalid format"), so the integrity assertions added for DR-P0-002 are unreachable; the storage mirror silently truncates listings at 1000 objects per prefix and accepts a zero-object archive; and no independent "no recent backup" alarm exists (the notifiers swallow delivery errors with `|| true`).

Net state: the platform has **no long-term backup of any kind**, the documented 30-day S3 recovery path and ≤24h dump RPO are fiction, and only Supabase PITR (7-day, never exercised) remains as a possible recovery path. Recommended next actions: (1) provision the backup secrets in the environment the workflows actually use (or move the workflows) and record green `db-backup` + `db-restore-test` run URLs; (2) fix the baseline-load step (one-line grep); (3) add the storage restore test and pagination/count guards.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| DB backup workflow | `.github/workflows/db-backup.yml` | Daily dump → Spaces | Implemented, **never green** | P0 | 29/29 failures; `environment: dev` |
| DB restore test | `.github/workflows/db-restore-test.yml` | Weekly restore + assertions | Implemented, **fails at baseline load** | P1 | Assertions unreachable |
| Backup dispatcher | `.github/workflows/backup-dispatch.yml` | Dispatch develop workflows from main | Implemented, **fails** | P2 | Missing `SCHEDULE_DISPATCH_TOKEN`; duplicate schedules (CI area) |
| Storage mirror | `.github/workflows/storage-backup.yml` + `scripts/backup-storage.sh` | documents/avatars/logos → Spaces | Implemented, **never green; silently partial** | P2 | Single 1000-object page; no count guard |
| Storage restore | `scripts/restore-storage.sh` | Archive → Supabase Storage | Implemented, **never exercised** | P2 | No assertions; no CI job |
| Baseline floors | `.github/restore-test-baseline.env` | Definition of "verified" | Committed, **cannot load in CI** | P1 | Comments break `$GITHUB_ENV` |
| Backup script (bash) | `scripts/backup-database.sh` | Canonical dump/encrypt/offsite/prune | Implemented, never exercised | P1 | Fail-closed without secrets |
| Backup script (PS) | `scripts/backup-database.ps1` | Windows helper | NOT CANONICAL, unencrypted | P3 | Duplicate logic drift |
| Manual restore | `scripts/restore-database.sh` | Operator restore | Implemented; prod guard; plaintext `/tmp` | P2 | Guard added, temp exposure remains |
| Terraform state | `providers.tf` + `env/backend.*.hcl` | Infra state in Spaces | External buckets; versioning unverified | P2 | Doc bucket name mismatch |
| Migration workflow | `.github/workflows/supabase-migrations.yml` | Push + drift guard | Implemented | P2 | Dry-run artifact; no reverse automation |
| RPO/RTO docs | `docs/RTO_RPO.md` | Targets + strategy | Documented, unvalidated | P1 | PITR/dump separated |
| Rollback docs | `docs/ROLLBACK_PROCEDURES.md` | Recovery procedures | Implemented; drill not exercised | P2 | §3a/§3b/§4 |
| Drill plan | `docs/audits/.../20261002-0344/backup_restore_drill_plan.md` | D1-D7 drills | Authored, no results | P3 | Only in dated audit folder |
| Product backup module | `apps/worker/src/tasks/module-tasks.ts:278-331` | Client backup tracking | Implemented, watches seeds | P2 | Not platform heartbeat |
| Seeds | `supabase/seeds/*` | Local dev data | Implemented, gated | — | Not a restore path; demo migrations gated on `app.seed_demo` |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database backups | 1 | `db-backup.yml` + `backup-database.sh` complete; 29/29 runs failed | Never produced an object; secrets unprovisioned | Provision secrets; record green run |
| Supabase restore docs | 3 | `ROLLBACK_PROCEDURES.md` §3 (PITR/reverse/restore), `RTO_RPO.md` | No dated exercise | Run D1/D2, record evidence |
| Storage backups | 1 | `storage-backup.yml` + scripts exist; 7/7 runs failed | Never produced an archive; silent truncation | Pagination + count guard + green run |
| Uploaded docs/files | 2 | Same as storage; restore script exists | Never restore-tested | Weekly storage restore test |
| Secrets backup | 2 | `SECRETS_ROTATION.md` rotation catalog | No escrow/backup; rotation not exercised | Document escrow decision + drill rotation |
| Infra config | 2 | Terraform state backend + docs | Versioning unverified; wrong bucket name in doc | Import buckets with versioning; fix doc |
| Migration rollback | 3 | Dry-run artifact + fail-closed drift; docs options | No reverse automation; no drill | Bad-migration drill D4 |
| Export tools | 1 | Documented `/backup-dr/export` does not exist | Docs vs code drift | Fix docs or implement |
| Seeds | 3 | `supabase/seeds/*`, gated demo migrations | Local-only; not relevant to prod restore | Keep gate; document |
| Restore scripts | 3 | `restore-database.sh` guard + checklist; `restore-storage.sh` | Plaintext `/tmp`; storage assertions absent | Stream-decrypt; add assertions |
| DR runbooks | 3 | `ROLLBACK_PROCEDURES.md`, `INCIDENT_RESPONSE.md`, `PLATFORM_FAILURE_RUNBOOKS.md` | Drill refs dangling; ledger empty | Stable paths + dated ledger |
| RPO/RTO | 2 | `RTO_RPO.md` accurate per method | Unvalidated; CI never green | Measure and date both methods |

## Detailed Review

### Item: Database backup workflow and script

- Evidence: `db-backup.yml:14,21,43-44`; `backup-database.sh:39-42,52-61,66-74,76-97,103,106-111,118-135`.
- What it does: daily (04:00 UTC) `pg_dump | gzip` → optional AES-256-CBC → `aws s3 cp` (STANDARD_IA) → optional offsite copy → 30-day prune; fails on missing URL, zero-byte dump and (with `REQUIRE_BACKUP_ENCRYPTION=1`) missing key.
- How it appears to work: complete and fail-closed; it is the only path that would produce a long-term backup.
- Dependencies: `SUPABASE_DB_URL`, `BACKUP_ENCRYPTION_KEY`, Spaces keys, bucket, `pg_dump`, `aws`, `jq`.
- Current controls: fail-closed checks, encryption, offsite affordance, retention, failure notifier.
- Missing controls: provisioned secrets; a green run; an independent staleness alarm.
- Risks: P0 — no backup exists; RPO unbounded beyond PITR.
- Recommended improvement: provision `SUPABASE_DB_URL` + `BACKUP_ENCRYPTION_KEY` in `dev` (or move the workflow to the environment that holds them), fix the secrets matrix, run it green.
- Suggested tests: a CI guard test that asserts required secrets exist before the schedule matters; a synthetic bad-URL run that fails and alerts.
- Suggested docs: correct `GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`; add the green run URL to `RELEASE_GATE.md`.

### Item: Restore-test workflow and baseline

- Evidence: `db-restore-test.yml:20-29,135-232,241-259`; `.github/restore-test-baseline.env:1-28`; run 37323743344 annotations.
- What it does: weekly restore of the newest object into throwaway `postgres:16-alpine`, then table/migration/row/freshness/tenant/RLS assertions.
- How it appears to work: the assertions are exactly what DR needs, but the job dies at step 3 loading the baseline file into `$GITHUB_ENV` (runner: "Invalid format '# Baseline thresholds...'").
- Dependencies: an existing backup object (none exists), Spaces creds, encryption key, Docker.
- Current controls: fail-closed assertions; floors in a committed file; ntfy failure alert.
- Missing controls: comment-safe env loading; a green run; storage equivalent.
- Risks: P1 — the only recoverability proof cannot execute.
- Recommended improvement: filter to `KEY=VALUE` lines before appending; re-run; record the first green run.
- Suggested tests: lint that every line appended to `$GITHUB_ENV` matches `^[A-Za-z_][A-Za-z0-9_]*=`; negative test with a truncated dump.
- Suggested docs: note in `ROLLBACK_PROCEDURES.md` that CI is the machine check and how to read a failed run.

### Item: Storage backup and restore

- Evidence: `backup-storage.sh:57-67,86-90,92-101,123`; `restore-storage.sh:94-121`; `storage-backup.yml`.
- What it does: REST-lists each bucket, downloads objects, tars + optionally encrypts, uploads, prunes; restore extracts and re-uploads with upsert.
- How it appears to work: functionally complete for small buckets; the list endpoint is called once with `limit:1000` and no offset loop, and nothing fails when zero objects are archived.
- Dependencies: `SUPABASE_URL`, service-role key, Spaces creds, encryption key.
- Current controls: encryption gate, MANIFEST, offsite copy, retention, notifier.
- Missing controls: pagination, object-count assertions, a restore test, checksums.
- Risks: P2 — silent partial/empty backups; unproven recovery.
- Recommended improvement: paginate; assert counts; add a weekly storage restore test comparing MANIFEST `object_count` to extracted files.
- Suggested tests: >1000-object prefix fixture; zero-object bucket fails; encrypted archive round-trip.
- Suggested docs: storage section of the drill plan with the restore verification checklist.

### Item: Terraform state and infrastructure recovery

- Evidence: `providers.tf:6-19`; `env/backend.dev.hcl:5`; `env/backend.prod.hcl:5`; `RTO_RPO.md:26`; `ROLLBACK_PROCEDURES.md:214-223`.
- What it does: state lives in Spaces buckets external to Terraform; the docs claim versioning and give an emergency restore recipe.
- How it appears to work: `encrypt` + `use_lockfile` are configured; versioning is a Spaces API setting with no repo resource, and the doc names a bucket that does not match the backend config.
- Dependencies: `DO_SPACES_*` keys, bucket versioning setting.
- Current controls: state encryption, lockfile, `prevent_destroy` on the droplet.
- Missing controls: versioning proof, correct bucket names, a tested state-restore procedure.
- Risks: P2 — state corruption may be unrecoverable; the emergency recipe misleads.
- Recommended improvement: import/declare both buckets with `versioning { enabled = true }`, fix the doc, run a state-restore drill.
- Suggested tests: a plan/apply that asserts the backend bucket exists and is versioned; drill D6 evidence.
- Suggested docs: `ROLLBACK_PROCEDURES.md` §4 rewrite.

### Item: Migration rollback and the bad-migration drill

- Evidence: `supabase-migrations.yml:67-83,90-127`; `ROLLBACK_PROCEDURES.md:78-112`; `RTO_RPO.md:45-47`.
- What it does: captures a dry-run plan artifact, pushes, then fails closed on post-push drift; docs offer reverse migration/PITR/manual undo.
- How it appears to work: the guard is real; the reverse path is manual and has never been drilled.
- Dependencies: Supabase CLI, project ref, access token, prod approval settings.
- Current controls: plan artifact, drift check, concurrency serialization.
- Missing controls: reverse-migration automation/template, drill record.
- Risks: P1 residual — extended outage risk during a bad migration.
- Recommended improvement: D4 drill on a throwaway project; record timings; template the reverse migration.
- Suggested tests: inject a deliberately bad migration on a scratch project and execute the documented undo.
- Suggested docs: `ROLLBACK_PROCEDURES.md` §3 Option A example with a real migration.

### Item: RPO/RTO claims vs exercise

- Evidence: `RTO_RPO.md:5-13,22-27,40-47`; run history; `RELEASE_GATE.md:66-68`.
- What it does: separates PITR (≤5 min) from dump (≤24 h) per service and states PITR is not yet proven.
- How it appears to work: the text is honest, but no measurement exists and the freshness assertion has never run.
- Dependencies: Supabase plan/PITR enablement; a working dump.
- Current controls: documented targets; freshness canary in the restore test.
- Missing controls: measured numbers; a dated exercise.
- Risks: P1 — targets cannot be relied on in a board/regulator conversation.
- Recommended improvement: get the pipeline green, then record one dump restore (measured) and one PITR fork (dated).
- Suggested tests: the restore test itself plus a recorded PITR exercise.
- Suggested docs: add a results table (date, method, measured RPO/RTO) to `RTO_RPO.md`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DR-001 | Database backups | `db-backup.yml`, `backup-database.sh` | Complete script; fail-closed | 0 successful runs; secrets unprovisioned | P0 | Provision + green run |
| DR-002 | Supabase restore docs | `ROLLBACK_PROCEDURES.md` §3 | PITR/reverse/S3 documented | No exercise | P2 | Run D1/D2, record |
| DR-003 | Storage backups | `storage-backup.yml`, `backup-storage.sh` | Encrypted mirror | 0 runs; truncation risk | P2 | Pagination + count guard |
| DR-004 | Uploaded docs/files | `restore-storage.sh` | Restore script + manifest | Never tested | P2 | Weekly storage restore test |
| DR-005 | Secrets backup | `SECRETS_ROTATION.md` | Rotation catalog | No escrow; rotation unexercised | P3 | Document escrow decision |
| DR-006 | Infra config | `providers.tf`, `env/*.hcl` | Encrypted backend + lock | Versioning unproven; wrong bucket in doc | P2 | Import buckets w/ versioning |
| DR-007 | Migration rollback | `supabase-migrations.yml` | Drift fail-closed; docs options | No reverse automation/drill | P1 | Bad-migration drill D4 |
| DR-008 | Export tools | `docs/modules/backup-dr.md:32` | None | Documented export does not exist | P3 | Fix docs or implement |
| DR-009 | Seeds | `supabase/seeds/*` | Local-only, demo gated | None (not a restore path) | — | Keep gate |
| DR-010 | Restore scripts | `restore-database.sh`, `restore-storage.sh` | Prod guard; checklist | Plaintext `/tmp`; no storage assertions | P2 | Stream decrypt; assert counts |
| DR-011 | DR runbooks | `ROLLBACK_PROCEDURES.md`, `INCIDENT_RESPONSE.md` | Real platform runbooks | Dangling drill refs; empty ledger | P3 | Stable paths + ledger |
| DR-012 | RPO/RTO | `RTO_RPO.md` | Documented per method | Unvalidated | P1 | Measure and date |

## Findings

Structured rows (severity, evidence, status) are in `32_backup_restore_drill.json`. Summary:

| Title | Severity | Status |
|---|---|---|
| No successful backup has ever run: every db-backup, storage-backup and db-restore-test CI run fails | P0 | open (new) |
| The weekly restore test fails at baseline load (invalid `GITHUB_ENV` format) so no restore verification ever executes | P1 | open (new) |
| Storage backups can be silently partial or empty (1000-object listing cap; zero-object archive accepted) | P2 | open (new) |
| Storage backups are never restore-tested and the restore script asserts nothing | P2 | open (new) |
| No independent backup-staleness alarm; notifier delivery failures are swallowed | P2 | open (new) |
| Platform DR drill plan is only in a dated audit folder and the drill ledger is empty | P3 | open (new) |
| Scheduled backup and restore-test workflows never run because they are absent from the default branch | P0 | verified-fixed |
| The restore test never asserts integrity and therefore cannot fail on a bad backup | P0 | verified-fixed |
| No backup or restore path exists for uploaded files in Supabase Storage | P1 | verified-fixed |
| Restore-test backup location contract (`S3_BACKUP_BUCKET`) is undocumented and can silently mismatch | P1 | verified-fixed |
| Database backups are unencrypted and stored in a single location with no offsite copy | P1 | partially-fixed |
| The restore test has no failure alert | P1 | verified-fixed |
| No automated migration reverse/rollback and no bad-migration drill | P1 | partially-fixed |
| RPO/RTO targets are documented but unvalidated; Postgres RPO conflates PITR with the daily dump | P1 | partially-fixed |
| Backup-failure alerting is present but cannot be trusted to deliver | P2 | verified-fixed |
| Terraform state bucket versioning is claimed but not backed by any resource | P2 | still-open |
| The backup/DR runbook and module docs describe a client-facing product, not the platform's recovery | P2 | partially-fixed |
| Manual restore has no environment guardrail and the transient dump is written unencrypted to `/tmp` | P2 | partially-fixed |
| The product `backup_status` module is not wired to any real platform backup heartbeat | P2 | still-open |
| Duplicate backup-script logic in bash and PowerShell risks drift | P3 | partially-fixed |
| Unpinned Postgres image in the restore test; no jq/aws pinning in the backup job | P3 | still-open |
| Documented backup/DR export endpoints do not exist | P3 | still-open |
| Terraform state restore guidance lacks a tested procedure | P3 | still-open |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No recoverable long-term backup exists | P0 | Certain (29/29 failed) | Unbounded data loss beyond PITR; unrecoverable client files | Run history; `CHANGELOG.md:198` | Provision secrets; green run |
| Restore verification never executes | P1 | Certain (1/1 failed) | False confidence; undetected corruption | Run 37323743344 annotations | Fix env loading |
| Storage archive silently incomplete | P2 | Medium | Partial client-file loss discovered in an incident | `backup-storage.sh:61` | Paginate + assert counts |
| Terraform state unrecoverable | P2 | Medium | Infra-management loss; wrong emergency recipe | `RTO_RPO.md:26`; `backend.*.hcl:5` | Versioning resource + drill |
| Silent stop of backups | P2 | Medium | No signal until a restore is attempted | Prometheus rules; `\|\| true` notifiers | Independent staleness alarm |
| Bad migration without tested undo | P1 | Medium | Extended outage | No drill record | D4 drill |

## Recommendations

### Immediate / Release Blocking

1. Provision `SUPABASE_DB_URL`, `BACKUP_ENCRYPTION_KEY` and the backup bucket in the `dev` environment (or repoint the workflows to the environment that holds them) and set `SCHEDULE_DISPATCH_TOKEN` or retire the dispatcher; run `db-backup` + `db-restore-test` manually and record the green run URLs in `docs/RELEASE_GATE.md` (closes the new P0).
2. Fix the restore-test baseline load (strip comments before `$GITHUB_ENV`) and re-run (new P1).
3. Correct `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:87-91` so the documented environment matches the workflows.

### This Week

- Record one measured dump restore and one PITR exercise in `RTO_RPO.md` (DR-P1-006).
- Add the storage restore test with MANIFEST count assertions (new P2s).
- Add an independent "no successful backup in 24/48h" check and stop swallowing notifier delivery failures.

### This Month

- Import/declare the Terraform state buckets with versioning enabled; fix the bucket name in `ROLLBACK_PROCEDURES.md` §4; run the state-restore drill (DR-P2-002, IR-P3-001).
- Rewrite `docs/modules/backup-dr.md` against `/api/v1/final/backups*` and `backup_status`; fix or implement the documented export (DR-P2-003, DR-P3-003).
- Run the bad-migration drill D4 and record it (DR-P1-005).
- Stream-decrypt the manual restore to avoid plaintext `/tmp` staging (DR-P2-004).

### Later / Platform Evolution

- Wire a platform backup heartbeat (metric or table) and keep the client module separate (DR-P2-005).
- Pin the Postgres/aws/jq tool versions (DR-P3-002).
- Retire or delegate the PowerShell helper (DR-P3-001).
- Move the drill plan to a stable path and maintain a dated drill ledger (new P3).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `grep -E '^[A-Za-z_][A-Za-z0-9_]*=' baseline.env >> $GITHUB_ENV` | Unblocks the entire restore test | `.github/workflows/db-restore-test.yml` | Dispatch the workflow; step passes |
| Provision `SUPABASE_DB_URL` in `dev` | Makes the daily backup runnable | GitHub environment (operator) | Green `db-backup` run URL |
| Fix the secrets-matrix table | Removes the root-cause confusion | `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` | Table matches workflow `environment:` values |
| Add `if [ "$OBJECT_COUNT" -eq 0 ]; then exit 1; fi` | Prevents empty archives | `scripts/backup-storage.sh` | Zero-object fixture fails |
| Fix the Terraform bucket name in the emergency recipe | Makes the doc usable | `docs/ROLLBACK_PROCEDURES.md` §4 | Names match `backend.*.hcl` |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Provision backup secrets + green runs | P0 | platform/ops | S | Operator access |
| Fix baseline load + first green restore test | P1 | CI owner | S | Backup object exists |
| Storage restore test + pagination/count guards | P2 | backend/ops | M | Working storage backup |
| Independent backup-staleness alarm | P2 | ops | M | Heartbeat or Prometheus metric |
| Terraform state versioning + restore drill | P2 | infrastructure | M | Spaces API |
| Bad-migration drill D4 + reverse template | P1 | backend | M | Scratch Supabase project |
| Drill plan relocation + ledger | P3 | docs/ops | S | None |
| Platform backup heartbeat | P2 | backend | M | Metric/table decision |

## Suggested Tests

- **Unit/CI config:** a test that every line appended to `$GITHUB_ENV` matches `^[A-Za-z_][A-Za-z0-9_]*=`; a test that fails when a required backup secret is unset (fast, actionable message).
- **Integration:** truncated/empty dump must fail the restore test; encrypted object round-trips through decrypt; >1000-object prefix backs up completely; zero-object bucket fails the storage job.
- **E2E/manual:** D1 dump restore into a throwaway Postgres with the §3a checklist; D2 PITR fork; D4 bad migration + reverse; D5 storage restore; D6 Terraform state restore; D7 droplet-loss paper drill.
- **Security/regression:** confirm the restore script refuses a non-local target without `ALLOW_PROD_RESTORE=yes`; confirm the ntfy notifier fails visibly when no channel is configured.
- **Observability:** a synthetic "no backup in 48h" condition fires the independent alarm.

## Suggested Documentation Updates

- `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` — make the backup-secret environment columns match the workflows.
- `docs/RELEASE_GATE.md` — record the green `db-backup`/`db-restore-test` run URLs when they exist.
- `docs/RTO_RPO.md` — add a measured-results table (date/method/measured RPO/RTO).
- `docs/ROLLBACK_PROCEDURES.md` — correct the state bucket names; document stream-decrypt; link the storage restore test.
- `docs/modules/backup-dr.md` — rewrite against `/api/v1/final/backups*` and `backup_status`; mark export as not implemented.
- `docs/INCIDENT_RESPONSE.md` / `docs/PLATFORM_FAILURE_RUNBOOKS.md` — point at the relocated drill plan and record drill results.
- New: `docs/runbooks/backup-restore-drill-plan.md` (stable path for the D1-D7 plan + results ledger).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which GitHub environment actually holds `SUPABASE_DB_URL` today? | Determines the one-line fix for the daily failure | Environment secret inventory (operator) |
| Is Supabase PITR enabled on the production project? | The only remaining recovery path | Supabase plan/PITR setting (operator) |
| Is Spaces versioning enabled on the state buckets? | Whether state rollback is possible | `aws s3api get-bucket-versioning` (operator) |
| Does the production database have any backup path outside the repo? | Whether prod is genuinely unprotected | Operator confirmation / external cron |
| What is the largest object count in a single storage folder today? | Whether the 1000-object cap is already biting | Storage listing (operator) |

## Appendix

### Drill plan (condensed from `docs/audits/repo-deep-dive/20261002-0344-develop-6286137/backup_restore_drill_plan.md`)

| ID | Drill | Target | Cadence | Current status |
|---|---|---|---|---|
| D1 | Full DB restore from latest S3 dump | Throwaway Postgres | Weekly | Never executed (no dump exists) |
| D2 | PITR exercise | Throwaway Supabase project | Monthly | Never executed |
| D3 | Restore integrity + tenant assertions | D1 target | Every D1 | Blocked by baseline-load bug |
| D4 | Bad-migration drill (roll forward + reverse) | Throwaway project | Quarterly | Never executed |
| D5 | Storage recovery drill | Throwaway bucket | Quarterly | Never executed |
| D6 | Terraform state recovery | Scratch backend | Semi-annual | Never executed |
| D7 | Droplet-loss exercise | Dev/scratch | Semi-annual | Never executed (all ledger rows `_pending_`) |

### Restore dependency inventory

- Database restore: Spaces creds → newest `s3://${S3_BUCKET}/${S3_PREFIX}/*.sql.gz(.enc)` → `BACKUP_ENCRYPTION_KEY` (if `.enc`) → throwaway Postgres → §3a checklist. Currently missing: the object itself (no successful backup).
- Storage restore: Spaces creds → newest `storage-backups/*.tar.gz(.enc)` → `BACKUP_ENCRYPTION_KEY` → `SUPABASE_URL` + service-role key → MANIFEST + object uploads. Currently missing: the archive itself.
- Terraform state: Spaces creds → versioned object in `portal-terraform-state-{development,production}` → backend re-init. Versioning unverified.
- Migration undo: Supabase CLI + access token → reverse migration or PITR. Unexercised.

### Backup inventory (what exists vs what is exercised)

| Dataset | Mechanism | Exercised? | Evidence |
|---|---|---|---|
| Postgres (dev) | daily `pg_dump` → Spaces | **No** | 29/29 runs failed |
| Postgres (prod) | none in repo (PITR claimed) | **No** | 07-domain finding; `RTO_RPO.md` |
| Storage buckets | daily mirror | **No** | 7/7 runs failed |
| Terraform state | Spaces, versioning claimed | **No** | no resource; no drill |
| Redis | rebuilt from DB (no backup) | N/A | `RTO_RPO.md:12` |
| Secrets | rotation only, no escrow | **No** | `SECRETS_ROTATION.md` |

### Verification checklist (post-restore, from `docs/ROLLBACK_PROCEDURES.md:148-165`)

- [ ] `S3_BUCKET`/`S3_PREFIX` resolved to the location the backup wrote to.
- [ ] Public table count ≥ `RESTORE_MIN_TABLES` (120).
- [ ] `supabase_migrations.schema_migrations` ≥ `RESTORE_MIN_MIGRATIONS` (1).
- [ ] Critical tables present and populated (`profiles`, `organizations`, `tickets`, `documents`, `audit_logs`).
- [ ] Newest `audit_logs` row within `RESTORE_MAX_DATA_AGE_DAYS` (2).
- [ ] Tenant-scoped tables still carry `organization_id`.
- [ ] No restored public table has RLS disabled (`RESTORE_MAX_TABLES_WITHOUT_RLS=0`).
- [ ] Storage restore paired with the DB restore (document paths resolve).

### Cross-domain rows (not duplicated here)

- `FILE-P2-004` (no backup path for uploads) is superseded by DR-P1-001 (verified-fixed); residual tracked in the new storage findings.
- `OBS-P2-003` / `RES-P2-006` (backup not exercised) remain covered by the new P0 + DR-P1-003/006 rows.
- `CI-P2-004` / `CI-P3-007` remain owned by the CI area (DR-P0-002 / DR-P3-002 are the DR-side rows).
- Production-vs-dev backup coverage is a DATA-area finding this run (07 domain) and is cross-referenced in DR-P1-006.
- Backup-dispatcher duplicate schedules are a CI-area finding (10 domain).
