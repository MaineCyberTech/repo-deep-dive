# G3 — Backups / DR / Infra / Observability (Delta Re-audit)

## Audit Metadata

- Audit: delta re-audit of the G3 lens
- Repository: `MaineCyberTech/mainecybertech`
- Target: `origin/main` @ `3fa9f636c887fd28698852d37daa5dcef9593f60` (promoted 2026-11-07)
- Previous run: `/root/repo-deep-dive/runs/mainecybertech-20261103-0748-full-main-6b7aa1a` (`6b7aa1a`, 2026-11-03)
- Method: read-only worktree at `/tmp/opencode/mct-delta-g3`; `6b7aa1a..3fa9f636` diff review; public GitHub Actions API for run history; no secret values read or printed; no live bucket, droplet or restore executed.
- Limitation: workflow **logs** require admin (the public API returns 403 for `.../logs`), so step-level conclusions come from job/step status and timing plus the public check-run annotations. Repo/environment variable *values* are not readable; where a value matters (e.g. `S3_OFFSITE_BUCKET`) the evidence says so.

## What changed since Nov 3

- `#348`/`#370`/`#378`: optional offsite S3 endpoint (`S3_OFFSITE_ENDPOINT`), configurable `BACKUP_RUNNER_LABELS`, and Raven Garage promoted to the **primary** destination (DO Spaces bucket `mainecybertech-backups` does not exist). The scripts now skip a duplicate copy when bucket+endpoint match the primary (`11aa2a3e`).
- `#375`: `ALLOW_EMPTY_STORAGE=1` for dev storage backups.
- Backup secrets were provisioned on 2026-11-07 for storage (`SUPABASE_URL`/service-role/encryption) but **not** a working DB URL or Garage key; the three manual storage-backup dispatches that day still failed (`04:33Z` on `9c0485e6`, `05:31Z` on `65eba79f`, `06:08Z` on `a58e171c`).
- `#357`: deploy checkout is reset/cleaned before switching refs (`deploy-do.yml:776-782`); verified present, no defect found.
- CSRF alert doc: `00a3a086` records the resolved CodeQL CSRF alert and issue #31 is closed (public API `state=closed`, `closed_at=2026-11-07T01:40Z`); the global `csrfProtection` mount is present (`apps/api/src/app.ts:142`). Not re-scored under G3 (G1 owns the security verdict).
- `27cc92a7` also introduced a duplicated stale health-check table in `docs/MONITORING_AND_ALERTING.md` (new OBS-P3-009).

## Counts

| Area | Re-verified | New | verified-fixed | partially-fixed | open | regressed |
|---|---|---:|---:|---:|---:|---:|
| DR | 5 | 5 | 3 | 1 | 6 | 0 |
| IR | 2 | 0 | 0 | 1 | 1 | 0 |
| OBS | 2 | 1 | 2 | 0 | 1 | 0 |
| **G3 total** | **9** | **6** | **5** | **2** | **8** | **0** |

New findings: **1 P1, 2 P2, 3 P3**. No previously `verified-fixed` finding regressed. The only doc regression is OBS-P3-009.

## Findings

| ID | Sev | Status | Title | Key evidence |
|---|---|---|---|---|
| DR-P0-001 | P0 | open | No successful backup/restore run ever; Garage path still fails | 0 successes for all 4 workflows; 42212650616; 42345678702 |
| DR-P1-003 | P1 | verified-fixed | Restore location contract shared/documented | Matrix:125-146; `find-latest-backup.sh:37-67` |
| DR-P1-004 | P1 | partially-fixed | Encryption enforced; offsite copy optional/skipped/unverified | `REQUIRE_BACKUP_ENCRYPTION=1`; skip at `backup-*.sh:49-56/47-54` |
| DR-P2-001 | P2 | verified-fixed | Storage pagination/partial/empty guards | `backup-storage.sh:84-170` |
| DR-P3-008 | P3 | verified-fixed | Restore discovery distinguishes failure from empty | `find-latest-backup.sh:45-60`; negative fixture |
| IR-P2-011 | P2 | open | Only alert-path exercise failed; no evidence row | run 41323651243; `ALERT_PATH_EXERCISE.md:102-106` |
| IR-P0-003 | P0 | partially-fixed | Watchdog URL unset; no missed-heartbeat drill | `INCIDENT_RESPONSE.md:154-161`; `DATA_BREACH_RESPONSE.md:145-156` |
| OBS-P1-002 | P1 | verified-fixed | Prod deploy gate uses app-host API + JSON assertion | `deploy-do.yml:98-110,1184-1195` |
| OBS-P3-008 | P3 | verified-fixed | node-exporter alertable + real probe | `prometheus.rules.yml:11-34`; `docker-compose.yml:306-340` |
| DR-P1-008 | P1 | **open (new)** | Restore tests hard-code `ubuntu-latest`, cannot reach Garage | `db-restore-test.yml:46`; `storage-restore-test.yml:55` |
| DR-P2-010 | P2 | **open (new)** | Empty-dev success counts as fresh backup; restore test rejects it | `storage-backup.yml:106`; `backup-staleness-check.yml:60-84` |
| DR-P2-011 | P2 | **open (new)** | Plaintext dumps/user files left on persistent lab runner on failure | `backup-database.sh:121,163`; `backup-storage.sh:56-69,212` |
| DR-P3-009 | P3 | **open (new)** | No versioning/object-lock/immutability on backup buckets | `backup-database.sh:166-184`; `backup-storage.sh:214-231` |
| DR-P3-010 | P3 | **open (new)** | Offsite skip ignores prefix; copy never verified | `backup-database.sh:49-56,152-158`; `backup-storage.sh:47-54,206-210` |
| OBS-P3-009 | P3 | **open (new)** | Duplicated stale health-check table; CI doc names wrong gate | `MONITORING_AND_ALERTING.md:224-243`; `CI.md:57-60` |

## Re-verification detail

### DR-P0-001 — open (P0)

The public API answers `total_count: 0` for `status=success` on **all four** backup/restore workflows. The latest main `db-backup` (42212650616, 2026-11-06T11:45Z, main@`15393691`) failed its script step 0 s after start, consistent with the missing-URL guard at `scripts/backup-database.sh:67-70`. On the new Garage path, the three manual `storage-backup` dispatches on 2026-11-07 all failed at the script step: 42338975431 (04:33Z, before `#375`), 42343086424 (05:31Z, empty-dev allowance present) and 42345678702 (06:08Z, `a58e171c` = merged `#378`) — the latter ran on `ci-runner` with the lab labels, so the runner is not the blocker; the failure is past the runner/empty-guard stage and consistent with the operator-reported Garage key/upload problem. No run exists at `3fa9f636` yet. Honest residual (operator blockers): `SUPABASE_DB_URL` missing/stale, Garage access key not accepted, no non-empty restore drill (`docs/runbooks/backup-restore-drill-ledger.md:12-24` all `planned`).

### DR-P1-003 — verified-fixed (P1)

The write/read contract is documented (`docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:125-146`) and both restore workflows use the shared `scripts/ci/find-latest-backup.sh` helper (db `:89-111`; storage `:70-89`), which normalises `s3://bucket[/prefix]` and rebuilds the key once (`:37-67`). The prior inline discovery duplication is gone.

> Brief/ID note: the orchestrator brief labels DR-P1-003 “offsite + encryption”; in the Nov 3 register that is **DR-P1-004**. Both are covered — DR-P1-003 above, DR-P1-004 next.

### DR-P1-004 — partially-fixed (P1) — offsite + encryption

- **Encryption is enforced.** Both workflows set `REQUIRE_BACKUP_ENCRYPTION=1` (`db-backup.yml:109-115`; `storage-backup.yml:99-103`); both scripts encrypt before upload and delete the plaintext (`backup-database.sh:108-129`; `backup-storage.sh:172-184`); the decrypt paths fail closed without the key (`db-restore-test.yml:127-151`; `restore-storage.sh:97-109`).
- **Offsite is not proven and is currently skipped.** The copy is conditional on `S3_OFFSITE_BUCKET` (`backup-database.sh:152-159`; `backup-storage.sh:206-210`). The scripts clear that variable when bucket+endpoint match the primary (`:49-56` / `:47-54`), and the documented dev config promotes Garage to primary and says the duplicate is skipped (`GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:135-137`). The current documented state is therefore a **single destination**, and no run has produced even the primary object (DR-P0-001). `RTO_RPO.md:50-57` still tells the operator to confirm objects in “both buckets”.
- **No post-copy verification.** “Offsite copy complete” is printed on the `aws s3 cp` exit alone (`backup-database.sh:158`; `backup-storage.sh:209-210`), with no `head-object`/listing.

### DR-P2-001 — verified-fixed (P2)

Pagination until a short page (`backup-storage.sh:84-102`), folder recursion, listed-vs-downloaded count equality (`:128-144`), zero-object refusal (`:133-139`) and the tar+MANIFEST integrity gate (`:162-170`) all remain; the workflow sets `VERIFY_BACKUP=1` (`storage-backup.yml:103`). The default/prod path is fixed; the deliberately empty dev path is a separate monitoring issue (DR-P2-010), not a regression of the silent-truncation fix.

### DR-P3-008 — verified-fixed (P3)

`find-latest-backup.sh:45-54` now reports a bucket/prefix/endpoint/credential-presence diagnostic and preserves the AWS exit code; `:56-60` keeps “reachable but empty” distinct. The negative fixture covers exit 254, empty and success (`scripts/ci/test-find-latest-backup.sh:44-76`) and runs in CI (`.github/actions/shellcheck/action.yml:20-39`). Both restore workflows call it.

### IR-P2-011 — open (P2)

Only one `alert-path-exercise` run exists: 41323651243 (2026-11-01, main@`4199ce8c`), failed at “Exercise alert delivery on the droplet”; the preceding direct ntfy relay check succeeded, so the channel is not the failure. `docs/ALERT_PATH_EXERCISE.md:102-106` still says `_none recorded yet_`; the missed-heartbeat drill (`:84-100`) is also unrecorded. Next schedule: 2026-12-01.

### IR-P0-003 — partially-fixed (P0)

The Watchdog route (`alertmanager.tmpl.yml:86-100,145-152`) and the fail-closed prod deploy guard (`deploy-do.yml:870-889`) remain. The repo still states `ALERTMANAGER_WATCHDOG_WEBHOOK_URL` is unset (`INCIDENT_RESPONSE.md:154-161`; `DATA_BREACH_RESPONSE.md:145-156,464-467`) and no drill is recorded (`ALERT_PATH_EXERCISE.md:84-106`). The mechanism is not the residual; the external URL and drill are.

### OBS-P1-002 — verified-fixed (P1)

Prod now sets `PUBLIC_API_CHECK_URL=https://app.mainecybertech.com/api/v1/store/products` (`deploy-do.yml:98-110`) and the health gate requires `.success == true` for prod, not just HTTP 200 (`:1184-1195`). The docs match (`MONITORING_AND_ALERTING.md:186-195`). No prod deploy completed after promotion at audit time (run 42346818866 still in progress), so this is code-verified, not live-prod-verified.

### OBS-P3-008 — verified-fixed (P3)

`MCTServiceDown` includes `node-exporter` (`prometheus.rules.yml:11-22`), `MCTNodeExporterDown` fires at 5 m (`:24-34`), promtool case 53 asserts both (`prometheus.rules.test.yml:824-852`), and the digest-pinned `node-exporter-probe` scrapes the real filesystem series (`docker-compose.yml:306-340`) and is gated by deploy (`deploy-do.yml:1092-1100`).

## New findings (file:line)

### DR-P1-008 — restore tests cannot reach the Garage endpoint (P1)

`db-backup.yml:53` and `storage-backup.yml:56` use the lab-runner labels, and run 42345678702 proves the variable is set (`ci-runner`, self-hosted/Linux/X64/lab/lab-docker). Both restore workflows still hard-code `runs-on: ubuntu-latest` (`db-restore-test.yml:46`; `storage-restore-test.yml:55`) while reading the same `S3_ENDPOINT` (`db-restore-test.yml:105`; `storage-restore-test.yml:83`), which the matrix documents as the private `192.168.222.120:3900` Garage endpoint (`GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:135-137`) and warns a hosted runner cannot reach (`:188`). `BACKUP_RUNNER_LABELS` is scoped to the backup workflows only (`:189`). The first Monday run on the promoted main cannot reach the documented private endpoint and will fail at “Find latest backup” before any restore assertion, unless the endpoint/runner is changed to a reachable path in the same change.

### DR-P2-010 — empty-dev success masks prod freshness and poisons the restore test (P2)

`storage-backup.yml:104-106` sets `ALLOW_EMPTY_STORAGE=1` outside prod runs; `scripts/backup-storage.sh:133-139` writes a manifest-only archive and the job is green; `scripts/restore-storage.sh:130-133` refuses exactly that archive. The staleness alarm is branch/environment/event-agnostic (`backup-staleness-check.yml:60-84`), so a dev manifest-only (or any dev) success satisfies the 30 h storage-backup gate for prod too. The direct prod flag is not weakened, but the independent prod signal is.

### DR-P2-011 — plaintext backup data persists on the lab runner after failure (P2)

`backup-database.sh` deletes the plaintext dump only after encryption (`:121`) and the upload only at `:162-163`; `backup-storage.sh` stages user objects under `./storage-backups/<timestamp>/` (`:56-69`) and removes them only after both uploads (`:212`). Under `set -e`, any failure leaves the files in the repo workspace; neither workflow has an `if: always()` cleanup step (`db-backup.yml:55-152`; `storage-backup.yml:58-133`). The jobs run on persistent self-hosted runners (`db-backup.yml:53`; `storage-backup.yml:56`), so a full plaintext dump/user-file set is readable on the shared lab host until the next checkout of this repo cleans it.

### DR-P3-009 — no backup immutability (P3)

Both prune functions delete in place (`backup-database.sh:166-184`; `backup-storage.sh:214-231`) with 30-day retention (`:33` / `:57`). Only the Terraform-state bucket has versioning (`infra/terraform/digitalocean/state-bucket.tf:28-34`); `RTO_RPO.md:24-26` documents retention but no object lock/versioning for backup buckets. A bad run or stolen write key can permanently delete the backup history.

### DR-P3-010 — offsite skip ignores prefix; copy not verified (P3)

The skip predicate compares only bucket+endpoint (`backup-database.sh:49-56`; `backup-storage.sh:47-54`), so a same-bucket/different-`S3_OFFSITE_PREFIX` second copy is dropped (only the generic 'skipping duplicate copy' log line) and that prefix is never written or pruned. The copy itself is declared complete on the `aws s3 cp` exit (`backup-database.sh:152-158`; `backup-storage.sh:206-210`), with no destination `head-object`/listing.

### OBS-P3-009 — duplicated stale monitoring table (P3)

`docs/MONITORING_AND_ALERTING.md:224-233` is the current table (with `node-exporter-probe`); `:235-243` is a stale duplicate without it (introduced in `27cc92a7`). `docs/CI.md:57-60` names `node-exporter` as the deploy gate while the code gates `node-exporter-probe` (`deploy-do.yml:1100`).

## Regression / operator-blocker summary

- **No regression of a previously verified finding.** The only regression is a documentation duplication (OBS-P3-009).
- **DR-P0-001 is still the release blocker and is operational, not architectural.** Exact residual:
  - `SUPABASE_DB_URL` missing/stale: every `db-backup` fails at the URL guard; latest main run 42212650616 (2026-11-06).
  - Garage access key not accepted: storage-backup 42345678702 (2026-11-07T06:08Z, `a58e171c`, `ci-runner`) still fails after the Garage promotion; no object is uploaded.
  - No non-empty restore drill: zero green `db-restore-test`/`storage-restore-test` runs; the drill ledger is all `planned` (`docs/runbooks/backup-restore-drill-ledger.md:12-24`).
- **DR-P1-008** means that even after the operator fixes the backup credentials, the restore tests will still fail unless the runner/endpoint reachability is fixed in the same change.
- **DR-P2-010** means a green dev storage backup must not be accepted as proof for the prod schedule; the current staleness query would accept it.

## Other checks performed

- **Offsite copy actually attempted?** The code path exists on both scripts (`backup-database.sh:152-159`; `backup-storage.sh:206-210`) but is conditional on `S3_OFFSITE_BUCKET`; in the documented dev topology Garage is the primary and the duplicate is skipped (`GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:135-137`). No successful run has produced either object, so there is no evidence of a landed offsite copy (DR-P0-001 / DR-P1-004).
- **Encryption on both destinations:** the same already-encrypted `.enc` object is uploaded/copied to both, so client-side encryption applies to both; the residual is whether a second destination exists and is verified, not the cipher path.
- **Runner-label injection:** `runs-on: ${{ fromJSON(vars.BACKUP_RUNNER_LABELS || '["ubuntu-latest"]') }}` is fed only by a repository variable (admin-controlled), not by a PR, issue or dispatch input; no injection path found. A malformed value fails workflow start, which is an operational error rather than a security boundary bypass.
- **Secret leakage in logs:** no workflow/script echoes a secret or enables `set -x`; `find-latest-backup.sh` prints only credential *presence* and the AWS error text. The DB URL is still passed as `pg_dump`/`psql` argv (`backup-database.sh:74,81`; `record-backup-heartbeat.sh:27`; `restore-database.sh:115`), which is pre-existing and becomes a local-process exposure concern on the shared lab runner rather than a log leak — noted as a residual, not a new delta finding.
- **Empty-dev weakening prod:** the direct guard is intact — a `workflow_dispatch environment=prod` or a scheduled run with `PROD_BACKUP_ENABLED=true` gets `ALLOW_EMPTY_STORAGE=0` (`storage-backup.yml:106`). The weakening is indirect, through the branch-agnostic staleness signal and the restore-test selection (DR-P2-010).
- **Deploy clean checkout (#357):** `git reset --hard HEAD` + `git clean -fd` before `git checkout -B` (`deploy-do.yml:776-782`) is present and consistent with the documented immutable-checkout intent; no defect found.

## Coverage not claimed

This is a delta audit of the G3 lens, not a full 43-domain sweep. No live bucket, droplet, Prometheus/Alertmanager instance or restore was touched; workflow logs were not downloadable without admin. The CSRF alert doc was checked for truthful state (issue closed, global middleware mounted) but its security verdict belongs to G1. The deploy clean-checkout change (`deploy-do.yml:776-782`) was reviewed and no defect found; the deploy run for `3fa9f636` was still in progress at audit time.
