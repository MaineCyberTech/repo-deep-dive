# 32_backup_restore_drill — Prompt 32 - Backup and Restore Drill Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `32_backup_restore_drill.md` (area DR, prompt)

## Verification Performed

# Backup and Restore Drill Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` @ `f5cb7c9` (branch `main`; `origin/main` = `584e1a3` + publication commits)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-11T04:50Z
- Auditor: subagent (DR)
- Area code: DR
- Scope limitations: read-only; no restore, snapshot, prune, or upload was executed by this audit. The nightly backup's offsite upload was still running at audit time (falcon-backup.service activating since 03:30:03Z; rclone copying 1,981 files / 68.3 GiB), so offsite outcomes are stated as of the observation time. Supabase-specific prompt items are not applicable (this repository does not use Supabase); seeds/export tools are not present in the conventional sense.

## Scope

Reviewed the backup lifecycle at `f5cb7c9`: OpenSearch snapshot job and retention, encrypted configuration archives, new-services archives, Wazuh indexer snapshots, edge-secrets archives, offsite upload/verification/retention (Spaces), R2 cold copy, restore rehearsal and assertion, encryption/key custody, RPO/RTO documentation, coverage matrix, and restore guardrails. Live verification: success/freshness stamps, the local snapshot repository listing, the snapshot job journal, the offsite log and upload-state files, the running rclone process, cluster settings/health, container timers, and the alert history for backup-staleness and dead-letter.

## Evidence Reviewed

- `bootstrap/85-backup-job.sh` (3-attempt retry :51-65; keep-3 retention :68-76; config archive :78-84; offsite call :92-99; abort markers)
- `bootstrap/80-offsite-backup.sh` (retry/backoff :71-95; dead-letter :97-106; delta upload :254-409; Wazuh repo :411-448; retention :450-468; main flow :470-659; real snapshot path :55-59)
- `automation/validation/restore_rehearsal.sh`, `restore_assertion.sh`, `offsite_verify_all.py`, `wazuh_indexer_backup.sh`, `r2_cold_copy.sh`, `backup_new_services.sh`, `disk_guard.sh`
- `config/systemd/falcon-backup.{service,timer}`, `falcon-wazuh-backup.*`, `falcon-cold-copy.*`, `falcon-edge-secrets-backup.*`
- `ci/validate.py:386-400` (restore-assertion gate), `automation/validation/tests/restore_assertion_test.sh`
- `docs/phase7/runbooks/RESTORE.md` (RPO/RTO :202-213; coverage matrix :336-349; C5 addendum :298-312), `docs/security/CUSTODY_ATTESTATION.md`, `docs/runbooks/WAZUH_INDEXER_BACKUP.md`, `docs/runbooks/R2_COLD_TIER.md`
- Live: `.last_backup_epoch`, `.offsite-last-success`, `.offsite-dead-letter`, `.uploaded/` state files, `offsite.log`, `journalctl -u falcon-backup.service`, OpenSearch `_snapshot/falcon-backup/_all`, `_cluster/settings`, `_cluster/health`, `systemctl list-timers`, `ps`, Prometheus backup gauges

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `journalctl -u falcon-backup.service`: Oct 11 03:37:39Z `snapshot SUCCESS`; `retention: pruned local snapshot snap-20261007-033000`; `freshness state updated` | live | Prior DR-P1-001 (no retry/no immediate alert) closure | Supported: retry code present; local path healthy |
| OpenSearch `_snapshot/falcon-backup/_all` 04:39Z: snap-20261009-164150, snap-20261010-033013, snap-20261011-033003 (all SUCCESS) | live | Prior DR-P3-002 retention | Supported at 04:39Z; a concurrent session then pruned snap-20261009-164150 at 04:40Z (chain now 2, below keep-3) |
| `_cluster/settings?flat_settings=true`: persistent = ISM metadata only (no watermarks), transient = {}; health yellow, 45 unassigned (single node) | live | Prior DR-P2-001 watermarks | Supported: defaults restored |
| `/srv/falcon/backups/.uploaded/upload-state-opensearch.tsv` = 0 bytes (mtime Oct 10 03:39); offsite log Oct 10 `0 file(s) total ... 0 to upload`, then `FAIL (opensearch): could not download index-78` | live | New offsite state damage | Supported: state truncated by the Oct 10 run |
| Offsite log Oct 11 03:37:44Z: `opensearch upload delta: 1981 file(s) total, 0 unchanged, 1981 to upload`; rclone still running 1 h+; `.upload-new-VSCUy9` lists 1,981 files / 68.3 GiB | live | New full re-upload | Supported: full repository re-upload in progress |
| `.offsite-last-success` = 1791572497 = 2026-10-09T19:01:37Z (age 33.6 h at 04:39Z) | live | Offsite RPO | Supported: 24 h target breached |
| sudo journal 02:39:06Z: `rm -f /srv/falcon/backups/.offsite-dead-letter`; relay `RESOLVED: Offsite backup retries exhausted` 02:41:10Z | live | DLQ alert truth | Supported: marker cleared without a successful run |
| `ls automation/validation/restore_assertion.sh` in the live tree (5236 bytes); `systemctl list-timers --all` has no restore/drill timer | live/repo | Prior DR-P3-001 | Still open: assertion exists but is not scheduled |
| `docs/phase7/runbooks/RESTORE.md:340-349` matrix row `IRIS case DB | no | local volume only | unbounded | OPEN` | repo | Coverage gap | Supported: case data not backed up |
| `falcon_cold_copy_last_success_timestamp_seconds` = 1791607945 (Oct 10 04:52Z); `falcon_wazuh_backup_last_success_timestamp_seconds` = 1791687935 (Oct 11 03:05Z); new-services stamp Oct 11 03:37Z | live | Other backup legs | Supported: fresh |

## Executive Summary

The local backup path is healthy and the DR-P1-001 remediation is real: the snapshot job retries 3x with 60 s spacing, keeps the newest 3 snapshots (live at 04:39Z: exactly 3 SUCCESS snapshots; a concurrent emergency prune at 04:40Z cut the chain to 2, below the keep-3 policy), updates freshness (Oct 11 03:37:41Z), and the Oct 10/11 nightly runs both completed their local steps. The watermarks were returned to defaults (DR-P2-001 closed) and the Wazuh indexer and cold-copy legs are fresh.

The offsite leg is the open risk. The 2026-10-10 run pointed the uploader at the compatibility symlink; `find` enumerated 0 files and the delta function wrote that empty enumeration back as the upload state (0 bytes). The run then failed verification, and #51 fixed the path - but the state damage means the 2026-10-11 run is re-uploading the entire 68.3 GiB repository (still running after >1 h, `falcon-backup.service` still activating). The offsite success stamp is 33.6 h old against a 24 h RPO target, and the prior verification run cleared the dead-letter marker by hand at 02:39Z so the DLQ alert resolved without a successful run; its register note claiming the Oct 11 offsite "succeeded" is unsupported by the live log and stamp. The 36 h offsite-stale rule is the remaining backstop (fires ~07:01Z if not complete).

Other current gaps: bulk telemetry snapshot repositories are still uploaded offsite unencrypted (DR-P2-002, unchanged); the IRIS case database is still not backed up (matrix says OPEN, unbounded RPO); and the merged restore assertion is still not scheduled on the lab (DR-P3-001).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Local snapshot job | `bootstrap/85-backup-job.sh` + `falcon-backup.timer` | Daily OpenSearch snapshot | Oct 11 SUCCESS; keep-3 pruned Oct 7 | Low | Retry 3x/60 s; immediate alert on final failure |
| Snapshot repository | `/var/lib/falcon-snapshots/opensearch` (root LV) | Local snapshot store | 69 GiB; 3 SUCCESS snapshots | High | Root LV at 19.56 GiB free (see RES-P1-002) |
| Encrypted config archive | `85-backup-job.sh:78-84` | Config/compose/automation archive | `config-20261011.tar.gz.enc` + plaintext `.tar.gz` left beside it | Low | Plaintext local copy is 0644 |
| New-services archive | `backup_new_services.sh` | WireGuard/Wazuh/IRIS/enrollment state | Oct 11 03:37Z stamp | Low | Encrypted at upload |
| Edge-secrets archives | `falcon-edge-secrets-backup.timer` | Edge PKI/secrets | Oct 11 02:47Z timer run; markers exist | Low | Restore not rehearsed |
| Wazuh indexer snapshots | `/opt/wazuh-backups/elasticsearch`, `wazuh_indexer_backup.sh` | Sibling indexer estate | Oct 11 03:05Z success | Low | Uploaded fail-soft |
| Offsite uploader | `bootstrap/80-offsite-backup.sh` | Spaces copy + retention + full verification | State truncated; full re-upload running; stamp 33.6 h | High | DR-P1-002 |
| R2 cold copy | `r2_cold_copy.sh` + `falcon-cold-copy.timer` | Oldest eligible index snapshot | Oct 10 04:52Z success | Low | Daily 04:40Z |
| Restore rehearsal | `restore_rehearsal.sh` | Offsite download + decrypt + restore | Last run 2026-10-01 (1.47 M docs/21 s) | Medium | Not scheduled |
| Restore assertion | `restore_assertion.sh`, `ci/validate.py:386-400` | Offline happy-path/corrupt/wrong-key assertions | Present; CI-only | Medium | DR-P3-001 |
| Key custody | `/srv/falcon/secrets/backup_enc.key`, `CUSTODY_ATTESTATION.md` | Archive key escrow | Attested 2026-10-02; decrypt-from-escrow not drilled | Medium | DR-P2-002 residual |
| Retention | `85:68-76` (local keep-3), `80:450-468` (remote keep-7 inventories) | Bounded retention | Working | Low | Local prune synchronous with the job |
| RPO/RTO | `RESTORE.md:202-213` | Owner targets | RPO <=24 h; RTO config <=1 h / data <=4 h (lab-scale) | Medium | Production re-measure pending |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database backups | 4 | Snapshot job + 3 SUCCESS snapshots + freshness | Root LV capacity risk | RES-P1-002 |
| Supabase restore docs | N/A | Not used by this repository | n/a | n/a |
| Storage backups | 4 | Offsite repo copy + full verification | State damage -> full re-upload | DR-P1-002 |
| Uploaded docs/files | 3 | Edge-secrets + new-services archives | Edge-secrets restore not rehearsed | Add a rehearsal |
| Secrets backup | 3 | Encrypted archives + custody attestation | Escrow decrypt not drilled | Drill |
| Infra config | 4 | Encrypted config archive + SHA-256 round trip | Plaintext local copy left | Remove/limit |
| Migration rollback | 4 | `index_rename_rollback_drill.sh` (2026-10-02) | Not scheduled | Schedule |
| Export tools | 3 | `offsite_verify_all.py`, `restore_rehearsal.sh` | Manual | Add timers |
| Seeds | 2 | No conventional seed path | n/a | Document |
| Restore scripts | 3 | Rehearsal + assertion + guardrails | Assertion not scheduled | DR-P3-001 |
| DR runbooks | 4 | `RESTORE.md`, `WAZUH_INDEXER_BACKUP.md`, `R2_COLD_TIER.md`, `DISK_PRESSURE.md` | RPO/RTO production re-measure | Update |
| RPO/RTO | 3 | Owner targets + measured lab numbers | 24 h RPO breached offsite now | DR-P1-002 |

## Detailed Review

### Item: Offsite upload state and delta

- Evidence: `80-offsite-backup.sh:254-409` (delta + state write at :400), `:55-59` (real path fix), offsite log Oct 10/11, `upload-state-opensearch.tsv` 0 bytes.
- What it does: enumerates the local repository, compares size+mtime with the state, uploads only new/changed files with `--files-from`, then replaces the state with the post-upload enumeration.
- How it appears to work: correct in the normal case; the Oct 10 run enumerated 0 files through the symlink and still wrote the state, which is the defect chain (state written even when the enumeration is empty/unexpected).
- Dependencies: `find` on the real path; Spaces write access; rclone.
- Current controls: retry/backoff, abort markers, dead-letter marker, full size verification before the success stamp.
- Missing controls: a sanity check that the enumeration is non-empty/comparable to the previous state; a state repair procedure; a run-time bound.
- Risks: full re-uploads (68.3 GiB), long stuck runs, offsite staleness.
- Recommended improvement: refuse to write a state whose file count drops unexpectedly (e.g. >50% below the previous state) and fail with a clear message; add a `OFFSITE_UPLOAD_SEED`-style repair path that requires a full verification first.
- Suggested tests: `automation/validation/tests/offsite_upload_delta_test.sh` extended with an empty-enumeration case asserting the state is not clobbered.
- Suggested docs: a state-repair section in `RESTORE.md`.

### Item: Restore assertion and rehearsal cadence

- Evidence: `restore_assertion.sh` (live tree), `ci/validate.py:386-400`, `restore_rehearsal.sh`, `RESTORE.md:298-312`.
- What it does: offline assertions (happy path, corrupt object, wrong key) plus a manual end-to-end rehearsal.
- Current controls: release-gate assertion; documented rehearsal procedure.
- Missing controls: any schedule; last real restore 2026-10-01.
- Risks: silent rot between rehearsals; the offsite state damage would not have been caught by the assertion alone.
- Recommended improvement: a monthly timer running the assertion plus a bounded rehearsal with a success stamp and staleness rule.
- Suggested tests: timer + stamp + rule; assert the stamp advances.
- Suggested docs: `RESTORE.md` cadence section.

### Item: Coverage matrix and guardrails

- Evidence: `RESTORE.md:336-349`.
- Covered: OpenSearch telemetry, Wazuh indexer, config, edge secrets. Not covered (accepted): Grafana SQLite, Prometheus TSDB, ntfy, Redis. Open: IRIS case DB (unbounded RPO).
- Guardrails: restore steps require scratch indices and cleanup; `restore_assertion.sh` fails closed on corrupt/wrong-key inputs; the offsite pruner refuses to prune with an empty protect list (`80-offsite-backup.sh:138-172`).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DR-001 | Database backups | 85/80 scripts; live snapshots | Daily snapshot + retry + keep-3 | Root LV capacity | P1 | RES-P1-002 |
| DR-002 | Supabase restore docs | n/a | n/a | n/a | n/a | n/a |
| DR-003 | Storage backups | offsite log; state file | Delta upload + full verification | State truncated -> 68.3 GiB re-upload | P1 | DR-P1-002 |
| DR-004 | Uploaded docs/files | edge-secrets markers | Encrypted upload | Restore not rehearsed | P2 | Add rehearsal |
| DR-005 | Secrets backup | `CUSTODY_ATTESTATION.md` | Owner attestation | Escrow decrypt not drilled | P2 | Drill |
| DR-006 | Infra config | config archive + round trip | Encrypted, verified | Plaintext local copy 0644 | P3 | Remove/limit |
| DR-007 | Migration rollback | `index_rename_rollback_drill.sh` | Drill 2026-10-02 | Not scheduled | P3 | Schedule |
| DR-008 | Export tools | `offsite_verify_all.py` | Runs inside offsite | Manual | P3 | Accept |
| DR-009 | Seeds | none | n/a | n/a | P3 | Document |
| DR-010 | Restore scripts | rehearsal + assertion | Manual + CI | Not scheduled | P3 | DR-P3-001 |
| DR-011 | DR runbooks | `RESTORE.md` et al. | Documented | Production RPO/RTO re-measure | P3 | Update |
| DR-012 | RPO/RTO | `RESTORE.md:202-213` | 24 h / 1-4 h targets | Offsite 33.6 h stale now | P1 | DR-P1-002 |

## Findings

### DR-P1-002 - Offsite upload state truncated to empty by the 2026-10-10 run; the 2026-10-11 run is re-uploading the full 68.3 GiB repository and the offsite success stamp is 33.6 h stale (24 h RPO target breached)

- Severity: P1
- Confidence: High (state file, offsite log, running process, stamp all captured live; causal chain read from the script)
- Area: DR
- Evidence:
  - `/srv/falcon/backups/.uploaded/upload-state-opensearch.tsv` = 0 bytes, mtime 2026-10-10 03:39
  - `offsite.log` Oct 10: `opensearch upload delta: 0 file(s) total, 0 unchanged, 0 to upload (0s)` then `FAIL (opensearch): could not download index-78`, `hash mismatch for index.latest`, `offsite verification failed`
  - `bootstrap/80-offsite-backup.sh:400` (`mv -f "$tmp_all" "$state_file"` - the empty enumeration becomes the state); `:55-59` (the real-path fix landed after the failure)
  - `offsite.log` Oct 11 03:37:44Z: `opensearch upload delta: 1981 file(s) total, 0 unchanged, 1981 to upload (--files-from --no-check-dest)`; `ps`: rclone still copying `--files-from /srv/falcon/backups/.uploaded/.upload-new-VSCUy9` at 04:39Z (elapsed 1 h 01 m); `.upload-all-4Rv3nW` sums to 1,981 files / 68.3 GiB
  - `falcon-backup.service` still `activating` since 03:30:03Z; `config/systemd/falcon-backup.service` has no `TimeoutStartSec`/`RuntimeMaxSec`
  - `/srv/falcon/backups/.offsite-last-success` = 1791572497 = 2026-10-09T19:01:37Z (age 33.6 h at 04:39Z) vs the documented RPO <=24 h (`docs/phase7/runbooks/RESTORE.md:204-208`)
  - sudo journal 02:39:06Z: `rm -f /srv/falcon/backups/.offsite-dead-letter` (manual clear); relay `RESOLVED: Offsite backup retries exhausted (dead-letter)` 02:41:10Z; `runs/falcon-20261011-0400-verify-main-584e1a3/follow_up_register.md:16` claims "Oct 11 offsite succeeded" - unsupported by the live log/stamp
  - Rule `falcon-backup-offsite-stale` (36 h, `bootstrap/90-alerting.sh:476-478`) will fire ~07:01Z if not complete
- What is happening: the Oct 10 symlink bug made the delta enumerate 0 files; the empty enumeration was written back as the upload state and the run failed verification. The path fix (#51) restored enumeration, but with the state empty every file is "new", so the Oct 11 run re-uploads the entire 68.3 GiB repository; the success stamp has not advanced and the run is unbounded.
- Why it matters: the offsite DR copy is the authoritative recovery source; it is now 33.6 h stale (target 24 h) and the re-upload may take hours. If it fails, the next run repeats the same 68.3 GiB upload (the state only updates on success), and the DLQ alert state was already cleared by hand.
- User / business impact: offsite recoverability window grows; the nightly run is occupied for hours.
- Security / privacy / reliability impact: reliability/DR; no data exposure.
- Recommended fix: (a) add a state sanity check (refuse to persist an enumeration that is empty or dramatically smaller than the previous state) and fail loudly; (b) repair the state after a verified full upload (or via a guarded seed); (c) bound the run (`TimeoutStartSec`/`RuntimeMaxSec`) and alert on a stuck run; (d) stop clearing the DLQ marker outside a successful run (document that manual clears must be followed by a verification).
- Suggested validation: `offsite_upload_delta_test.sh` empty-enumeration case; a bounded offsite failure drill asserting marker + alert + no stamp; confirm the stamp advances after the current upload.
- Owner suggestion: platform
- Effort estimate: S (sanity check) / M (bounded run + repair procedure)
- Dependencies: the in-flight upload (do not interrupt without a plan)
- Status: open
- Endpoint / data path: `80-offsite-backup.sh` -> rclone -> `spaces:falcon-mct/monitoring/opensearch` -> `.offsite-last-success`
- Attack path: none identified

### DR-P2-002 - Bulk telemetry snapshot repositories are still stored offsite unencrypted; only config/secrets archives are encrypted

- Severity: P2
- Confidence: High (code unchanged; rclone config has no SSE)
- Area: DR
- Evidence:
  - `bootstrap/80-offsite-backup.sh:549-563` (`upload_repo_delta` uploads the OpenSearch repository as plain files; same for the Wazuh repository at :423-427)
  - `bootstrap/80-offsite-backup.sh:493-507` (rclone config written without SSE settings)
  - `docs/security/CUSTODY_ATTESTATION.md` (key escrow by owner attestation; decrypt-from-escrow not drilled)
  - `docs/phase7/runbooks/RESTORE.md:320` (key-custody residual)
- What is happening: syslog, flow, IDS and Wazuh alert data are copied to Spaces as plaintext snapshot files; the Spaces key is access-controlled but no encryption-at-rest evidence exists for these objects.
- Why it matters: a bucket/key compromise exposes raw telemetry; no owner-accepted decision is recorded for the plaintext choice.
- Recommended fix: enable SSE on the bucket/objects or record an explicit owner acceptance; add a decrypt-from-escrow drill for `backup_enc.key`.
- Suggested validation: `rclone` SSE round trip or a signed owner acceptance in the decision log.
- Owner suggestion: owner/security
- Effort estimate: S
- Status: still-open

### DR-P2-003 - IRIS case database is not backed up; the coverage matrix marks it OPEN with unbounded RPO

- Severity: P2
- Confidence: High (repository matrix + no backup mechanism found)
- Area: DR
- Evidence:
  - `docs/phase7/runbooks/RESTORE.md:340-349`: `IRIS case DB | no | local volume only | unbounded | **OPEN** (owner: case-data backup decision)`
  - No IRIS dump/backup job in `bootstrap/`/`automation/validation/` (backup scripts cover OpenSearch, Wazuh indexer, config, new-services, edge secrets, R2)
  - `runs/falcon-20261009-2117-full-08e20d1/follow_up_register.md:25` (PRIV-P1-001 retention/deletion window owner-gated)
- What is happening: case data lives only in the local Docker volume; the owner decision on backing it up is still open.
- Why it matters: a host/volume loss destroys case data with no recovery point; retention/privacy decisions also depend on this.
- Recommended fix: owner decision + an encrypted IRIS dump to the offsite bucket with a freshness rule; or a recorded owner acceptance of the loss.
- Suggested validation: a bounded dump/restore drill with row counts and tenant integrity checks.
- Owner suggestion: owner
- Effort estimate: M
- Status: open

### DR-P3-001 - Scheduled end-to-end restore assertion still absent; the merged assertion exists in the live tree but is not scheduled

- Severity: P3
- Confidence: High (live tree + timer inventory)
- Area: DR
- Evidence:
  - `ls /home/user/falcon-build/automation/validation/restore_assertion.sh` -> present (5,236 bytes, 2026-10-10)
  - `ci/validate.py:386-400` + `automation/validation/tests/restore_assertion_test.sh` (release gate only)
  - `systemctl list-timers --all` -> no restore/drill/assert timer; `config/systemd/` has no restore unit
  - Last live rehearsal remains 2026-10-01 (`RESTORE.md:298-303`: 1,470,746 docs in 21 s)
- What is happening: the assertion is merged and the live tree now contains it, but nothing runs it on a schedule; the lab cannot demonstrate periodic restore proof.
- Why it matters: restore readiness is only proven at release time; silent rot between rehearsals.
- Recommended fix: add a monthly timer (assertion + bounded rehearsal) with a success stamp and a staleness rule.
- Suggested validation: timer fires, stamp advances, staleness rule tested.
- Owner suggestion: platform
- Effort estimate: S
- Status: still-open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Offsite copy stays stale / re-upload loops | P1 | High (in progress) | DR copy unusable; RPO breach | state 0 bytes; 68.3 GiB re-upload; stamp 33.6 h | DR-P1-002 |
| Root LV fills and snapshots fail | P1 | High | Local RPO growth | RES-P1-002 | RES-P1-002 |
| IRIS case data loss | P2 | Medium | Case data unrecoverable | matrix OPEN | DR-P2-003 |
| Telemetry plaintext offsite | P2 | Low-Medium | Confidentiality | code + rclone config | DR-P2-002 |
| Restore readiness rots | P3 | Medium | Slow recovery | no schedule | DR-P3-001 |

## Recommendations

### Immediate / Release Blocking

- Let the current full re-upload finish (or bound it) and confirm the success stamp advances; do not clear the DLQ marker outside a successful run (DR-P1-002).
- Repair the upload state after a verified full upload (DR-P1-002).

### This Week

- Add the empty-enumeration guard and a run-time bound to the backup job (DR-P1-002).
- Owner decision on IRIS backups (DR-P2-003).
- Schedule the restore assertion (DR-P3-001).

### This Month

- SSE or an owner acceptance for the plaintext telemetry repositories; escrow decrypt drill (DR-P2-002).
- Add the edge-secrets restore rehearsal.

### Later / Platform Evolution

- Production-scale RPO/RTO re-measurement (`RESTORE.md:210-213`).
- Move the snapshot repository off the root LV (RES-P1-002).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Empty/shrunk-enumeration guard | Prevents state clobbering | `bootstrap/80-offsite-backup.sh` | delta test empty case |
| `RuntimeMaxSec` on the backup unit | Bounds stuck runs | `config/systemd/falcon-backup.service` | timeout test |
| Monthly restore-assertion timer | Periodic restore proof | `config/systemd/` + `ci/validate.py` | timer + stamp |
| Document DLQ-clear rule | Prevents silent alert clearing | `docs/phase7/runbooks/RESTORE.md` | doc review |
| Remove the local plaintext config copy | Reduces exposure | `bootstrap/85-backup-job.sh:78-84` | guard run |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Offsite state integrity + repair | P1 | platform | M | none |
| IRIS backup decision + job | P2 | owner | M | owner decision |
| Telemetry SSE / owner acceptance | P2 | owner/security | S | owner decision |
| Scheduled restore assertion | P3 | platform | S | none |
| Edge-secrets restore rehearsal | P3 | platform | S | none |

## Suggested Tests

- Unit: `offsite_upload_delta_test.sh` extended for empty/shrunk enumerations; `restore_assertion_test.sh` in CI.
- Integration: bounded offsite failure drill (block Spaces) asserting the DLQ marker, the alert, and no stamp advance; a stuck-run simulation asserting the runtime bound.
- E2E: monthly rehearsal (offsite download -> decrypt -> restore -> row-count and tenant-integrity checks -> cleanup) with a stamp.
- CI: keep `restore-assertion` in `ci/validate.py`; add a catalogue check that the offsite rule IDs exist.
- Manual: confirm the current upload's completion and the stamp; verify the next nightly delta is small.

## Suggested Documentation Updates

- `docs/phase7/runbooks/RESTORE.md`: upload-state repair procedure; DLQ-clear rule; cadence section; IRIS decision status.
- `docs/security/CUSTODY_ATTESTATION.md`: escrow decrypt drill record.
- `docs/runbooks/R2_COLD_TIER.md`: cross-reference the state damage lesson.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: snapshot-repo root-LV capacity (joint with RES).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Will the current 68.3 GiB upload complete before the 36 h stale rule fires (~07:01Z)? | DR RPO | offsite log + stamp |
| What is the measured upload throughput? | Bound planning | rclone stats/network counters |
| Was the Oct 10 offsite failure deliberately followed by the marker clear, or accidental? | Process integrity | operator note |
| IRIS backup decision timeline? | Case-data loss risk | owner |

## Appendix

### Backup inventory (live, 2026-10-11)

| Dataset | Mechanism | Last success | Offsite | Freshness rule |
|---|---|---|---|---|
| OpenSearch `falcon-*` | Local snapshot + Spaces copy | 2026-10-11 03:37Z (local); 2026-10-09 19:01Z (offsite) | Spaces (plain files) | Backup stale / Offsite stale (36 h) |
| Config archive | `config-<date>.tar.gz.enc` | 2026-10-11 03:37Z | Spaces (encrypted) | Offsite stale |
| New services | `falcon-new-services-*.tar.gz` (encrypted at upload) | 2026-10-11 03:37Z | Spaces | New-services stale (36 h) |
| Edge secrets | `falcon-edge-secrets-backup-*.tar.gz.enc` | 2026-10-11 02:47Z (timer) | Spaces | Edge backup rules |
| Wazuh indexer | `/opt/wazuh-backups/elasticsearch` | 2026-10-11 03:05Z | Spaces | Wazuh indexer stale (36 h) |
| R2 cold copy | Oldest eligible index | 2026-10-10 04:52Z | R2 | Cold-copy stale (48 h) |
| IRIS case DB | none | n/a | none | none |

### Restore dependency inventory

OpenSearch container + snapshot repo mount -> snapshot repository -> Spaces credentials (`spaces.env`, `rclone.conf`) -> `backup_enc.key` (config/edge secrets) -> Docker/Compose + rendered configs -> Grafana/Prometheus state (config-derived). Key escrow: owner custody (attested).

### Drill plan (recommended)

1. Offsite failure drill: block Spaces; assert DLQ marker + alert + no stamp; restore; re-run.
2. State repair drill: simulate a 0-file enumeration; assert the state is not clobbered.
3. Full restore rehearsal (monthly): offsite download -> decrypt -> restore -> tenant/count checks -> cleanup.
4. Bad-migration drill: rerun the index-rename rollback with an interrupted reindex (existing script).
5. Root-LV drill: see RES chaos plan.

### Verification checklist (for the next drill)

- [ ] Offsite stamp advances and the delta is small in steady state
- [ ] Snapshot count == keep-3 after the job
- [ ] DLQ marker absent only after a successful run
- [ ] Restore rehearsal stamp fresh; assertion PASS
- [ ] Decrypt-from-escrow succeeds

## Findings

| ID | Severity | Title |
|---|---|---|
| DR-P1-002 | P1 | Offsite upload state truncated to empty by the 2026-10-10 run; the 2026-10-11 run is re-uploading the full 68.3 GiB repository and the offsite success stamp is 33.6 h stale (24 h RPO target breached) |
| DR-P2-002 | P2 | Bulk telemetry snapshot repositories are still stored offsite unencrypted; only config/secrets archives are encrypted |
| DR-P2-003 | P2 | IRIS case database is not backed up; the coverage matrix marks it OPEN with unbounded RPO |
| DR-P3-001 | P3 | Scheduled end-to-end restore assertion still absent; the merged assertion exists in the live tree but is not scheduled |
