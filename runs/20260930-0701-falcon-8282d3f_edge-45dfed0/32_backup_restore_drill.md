# Backup and Restore Drill Audit

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repositories: central `/home/user/falcon-build` `main` @ `8282d3f`; edge `/home/user/falcon-edge-build` HEAD `f1c5def` (manifest `45dfed0`); delivery `/home/user/falcon-edge-delivery`
- Generated: 2026-09-30T14:30Z · Auditor: prompt-32 subagent (read-only; no root, no Docker, no OpenSearch auth)
- Area code: DR · Output: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/32_backup_restore_drill.md` · Companion: `backup_restore_drill_plan.md`
- Working tree (falcon): dirty — ` M evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out`; `?? …same….meta.json`; `?? docs/audits/`
- Scope limitations: `/srv/falcon/backups`, `/srv/falcon/secrets`, Docker, WireGuard and OpenSearch require root/credentials → live repo contents, Spaces/R2 listings and cluster state are `unverified`; no drill executed (mutating).

## Scope

Reviewed: local OpenSearch snapshots (`falcon-backup` fs repo), offsite Spaces copy/retention/verification, new-services backup, edge PKI/DB backup, R2 searchable cold-tier records, restore scripts/runbooks, freshness alerting, recoverability windows, duplicate jobs, coverage gaps, access controls/encryption, RPO/RTO, guardrails.
Not reviewed: runtime OpenSearch indices, Wazuh indexer beyond recorded artifacts (sibling `DATA-P1-002`), owner-side Cloudflare/R2 settings, root-only logs (read only via captures), live object listings.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `bootstrap/85-backup-job.sh`, `bootstrap/80-offsite-backup.sh`, `config/systemd/falcon-backup.{service,timer}` | code | Daily pipeline | Duplicate snapshot/config creation confirmed |
| `automation/validation/{backup_new_services,restore_rehearsal,phase6_backup_restore,disk_guard,export_monitor_metrics,post_reboot_verify}.sh` | code | Coverage, drills, retention, metrics | Drill lacks failure exit |
| `docs/phase7/runbooks/RESTORE.md`, `docs/phase9/CLEAN_HOST_REBUILD_RUNBOOK.md`, `PATCH_MAINTENANCE.md`, `docs/runbooks/CAPACITY_AND_TELEMETRY.md` | docs | Procedure/RPO/cadence | Monthly-rehearsal claim unenforced |
| `evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.{out,meta.json}` | evidence | Offsite recovery 03:55–07:43Z | SHA matches meta; **uncommitted**; committed blob 0 bytes |
| `evidence/raw/{P6-G03,P6-G09,P9-G06,P9-G08,P9-G09}/*` | evidence | Snapshot/offsite/drill history | Last restore 2026-09-23 |
| `ledgers/gate_ledger.csv` P6-G01…G10; `phase9_gate_ledger.csv` P9-G06/G09; `test_execution.csv` | ledger | Claims vs evidence | P6-G03: retention path not yet exercised |
| `ledgers/decision_log.md` 2026-09-27T17:50/21:25Z; `docs/phase9/review/PRODUCTION_VERDICT.md` | ledger | R2 tier, RPO/RTO | R2 manual, single index |
| Live: `live_snapshot.txt` 07:01Z; `falcon_metrics.prom` 14:22Z; `/srv/falcon/backups` deny; `/opt/wazuh-backups/elasticsearch` | live obs | Freshness, timers, indexer staleness | Backup epoch 03:34:01Z; indexer repo 2026-09-21 |
| Prior run `20260930-0320-…` + current-run siblings `03/07/09/12/31` | audit | Cross-refs | FEAT-P2-001, DATA-P1-002, SEARCH-P2-001/004 |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log`/`merge-base` both repos | repo | Bind claims to commits | `8282d3f` descends from `794ba31`; edge `f1c5def` |
| `python3 ci/validate.py` | repo | Ledger/evidence integrity | 4 PASS incl. "evidence integrity (462 captures)"; **FAIL secret scan: 2 long_hex hits in this run's own `01`/`02` audit files** |
| `sha256sum` offsite `.out` vs meta; committed blob check | repo | Evidence binding | `85f5b86b…` = meta (1708 B); committed version empty; manifests bind `e3b0c442…` |
| GNU tar 1.35 synthetic test (create `--absolute-names`, list `tar -tzf \| grep "$p"`) | repo | Reproduce new-services check | Absolute members list & match → logic plausible; last real capture (00:46) shows 4× `[MISSING]` |
| Source `/home/user/.env` in subshell; unquoted-whitespace scan | live | LIVE-P0-001 root cause | Clean (74 vars, no hazards) → operational cause fixed; values not printed |
| Metric read + epoch arithmetic; delivery/indexer listings; unit scan | live | Freshness/coverage | `1790739241` → 03:34:01Z, ~10.8 h at 14:22Z; edge backups host-local; no duplicate schedulers |

## Executive Summary

The estate is **functional but only partly proven**. Strengths: daily local snapshot + AES-256-CBC config archive; list-free offsite copy with SHA-256 round-trip; least-privilege `falcon-backup` role; scratch-only restore defaults; owner-approved RPO 24 h / RTO 1 h (config) / 4 h (data); clean-host reconstruction proven 2026-09-23 (4.79 M docs in 52 s). The 2026-09-30 offsite failure was **operationally fixed and re-run successfully** (1723 files, 07:37Z), but its outcome is still invisible to monitoring and the recovery evidence is uncommitted (package binds a 0-byte artifact). Highest risks: offsite retention deleting blobs by stale lists; duplicate snapshot/config creation; undocumented post-deletion window; rehearsal narrower than the claim; secrets/backup-key custody host-dependent; unbacked datasets (Wazuh — sibling `DATA-P1-002`; edge PKI/DB; Grafana/Prometheus/ntfy/Redis).

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Local snapshot repo | `/srv/falcon/backups/opensearch`; `85:18-25`, `80:59-69` | Index recovery | Daily, 2 snapshots/run | Med | Local keep 3 (`disk_guard.sh:14`) |
| Offsite copy | Spaces `monitoring/opensearch`; `80:71-96` | Cold tier | Fresh 07:37Z | High | No metric/alert |
| Offsite retention | `80:139-150` | Prune | Keep 7 inventories | High | First exercised 09-30 |
| Config archive | `85:27-33`, `80:98-113` | Infra config | Daily AES-256 | Med | No digest; same-day overwrite |
| New-services | `backup_new_services.sh` | WG/Wazuh/IRIS/enroll state | Daily + offsite | Med | IRIS dump silent skip |
| Edge PKI/DB | edge `backup_edge_secrets.py` → delivery dir | CA/seed/SQLite | Daily, keep 7, local-only | High | INTG-P1-003 |
| R2 cold tier | `compose/central/docker-compose.yml:56-80`; P9-G08 | 1-index cold copy | Manual mount | Med | SEARCH-P2-004 |
| Drills | `restore_rehearsal.sh`, `phase6_backup_restore.sh` | Rehearsals | Manual | Med | Last 2026-09-23; no fail exit |
| Runbook | `docs/phase7/runbooks/RESTORE.md` | Procedure | Good, partly stale | Med | Assets dated 09-21 |
| Alerting | `export_monitor_metrics.sh:80-84,276-278`; `90-alerting.sh:222-224` | Backup-stale | Local-only, 36 h | High | No offsite signal |
| Disk guard | `disk_guard.sh` | Reclaim <10 GiB | Keeps 3/3 | Med | Trusts offsite blindly |
| Coverage gaps | — | Wazuh/Grafana/Prometheus/ntfy/Redis/global state | Unbacked | High | DR-P2-001 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Action |
|---|---:|---|---|---|
| Database backups (OpenSearch) | 3 | Daily+offsite; P9-G06/G09 | Duplicates, window, enforcement | De-dup; document; verify |
| Supabase restore docs | 0 (N/A) | Not adopted | N/A | Keep N/A |
| Storage backups | 2 | Spaces; R2 manual | Retention risk; R2 manual | Safe retention; automate |
| Uploaded docs/files | 0 (N/A) | No app uploads | Edge secrets local | Offsite or accept |
| Secrets backup | 2 | New-services archive; custody claim | Key custody unverified | Attest; test decrypt |
| Infra config | 3 | Repo + archive | Host-only units; no digest | Digest; commit units |
| Migration rollback | 2 | `index_rename_migration.sh` note | No bad-migration drill | Add drill |
| Export tools | 2 | Snapshot/reindex tooling | No data export beyond snapshots | Accept/document |
| Seeds | 0 (N/A) | No app DB; config in git | N/A | Keep N/A |
| Restore scripts | 2 | `restore_rehearsal.sh` | No fail exit; local only | Assert; add offsite leg |
| DR runbooks | 3 | RESTORE.md, CLEAN_HOST | Stale; cadence claim | Refresh; schedule |
| RPO/RTO | 3 | P6-G09; P9-G06 | Lab-scale | Re-measure |

## Detailed Review

- **OpenSearch/offsite:** `85:19` snapshots `falcon-*` only (`include_global_state:false`); offsite is list-free (`80:1-10`, 0600 rclone conf) with 3-file sample + config round-trip, but deletes by stale lists and has no outcome signal (DR-P1-001/002); `.security`/dashboards rebuilt or lost; Wazuh excluded (DATA-P1-002).
- **New-services/edge:** 18 paths + IRIS dump, check gates 4 paths, dump failure silent (DR-P1-002); edge CA/seed/SQLite archived 0600 keep-7 but host-local in the release surface (DR-P1-005).
- **Drills:** `restore_rehearsal.sh` uses `set -uo pipefail` (no `-e`) and prints mismatches without failing; restores from the local repo; P9-G09 central-only; monthly cadence claimed without a timer (DR-P1-003).
- **Guardrails/migration:** scratch-only defaults + abort criteria (`RESTORE.md:200-209`), no technical live-overwrite block; only a comment guard at `index_rename_migration.sh:40`, no abort drill (DR-P2-002).
- **R2/coverage:** manual single-index mount outside bootstrap; Grafana/Prometheus/ntfy/Redis unbacked (DR-P2-001, SEARCH-P2-004).

## Scenario / Control Matrix

| ID | Scenario/control | Evidence | Control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DR-001 | OpenSearch snapshots | `85:18-25` | Daily | No job verification | P1 | Verification timer |
| DR-002 | Offsite copy | `80:71-96` | SHA round-trip sample | Unmonitored | P1 | Metric+rule |
| DR-003 | Offsite retention | `80:139-150` | Keep 7 | Stale-list delete | P1 | Retained-union delete |
| DR-004 | Config archive | `85:27-33` | Encryption | No digest; overwrite | P2 | Digest; timestamped |
| DR-005 | New-services | `backup_new_services.sh` | Gated check | No evidence; IRIS skip | P1 | Capture; fail on IRIS |
| DR-006 | Edge PKI/DB | `backup_edge_secrets.py` | Daily local | No offsite | P1 | Upload encrypted |
| DR-007 | Secrets custody | `RESTORE.md:30,47,93-103` | Owner claim | Unverified | P1 | Attest; decrypt drill |
| DR-008 | RPO/RTO | P6-G09; verdict | 24 h/1 h/4 h | Lab-scale | P2 | Re-measure |
| DR-009 | Restore drill | `restore_rehearsal.sh` | Manual | No fail exit; narrow | P1 | Enforce; widen |
| DR-010 | Bad migration | `index_rename_migration.sh` | Safety note | No abort drill | P2 | Add drill |
| DR-011 | Coverage gaps | `85:19`; `00`/CLEAN_HOST | Partial accept | Wazuh/other services | P1/P2 | Matrix + dispose |
| DR-012 | Evidence binding | untracked meta; empty manifest hash | ci passes tree | Package stale | P2 | Commit; rebind |

## Findings

### Finding ID: DR-P1-001 - Offsite outcome still has no metric/alert, and its recovery evidence is uncommitted (prior LIVE-P0-001)

- Severity: P1 (prior P0 while actively failing) · Confidence: High · Area: DR · Status: partially-fixed
- Evidence: `85-backup-job.sh:35` (freshness written before new-services/offsite), `:41-46` (offsite failure logged only); `export_monitor_metrics.sh:80-84,276-278` (local epoch); `90-alerting.sh:222-224` (36 h local rule); evidence `20260930T035539Z…` (silent 03:34Z failure; manual re-run exit 0 at 07:43Z); committed `.out` 0 bytes, `.meta.json` untracked, manifests bind `e3b0c442…` at `evidence/MANIFEST.sha256:927` and `PACKAGE_MANIFEST.sha256:1184`; sibling FEAT-P2-001.
- What is happening: local success marks the backup healthy when offsite/config/new-services fail, and the only recovery evidence sits outside the published package.
- Why it matters: the cold tier can go stale indefinitely; reviewers cannot see the recovery proof.
- User / business impact: host loss during a silent offsite outage loses the delta or tier; audit trust gap.
- Security / privacy / reliability impact: unverifiable DR posture; evidence-vs-package contradiction.
- Recommended fix: add `offsite_last_success_epoch` (+ new-services) gauges and stale rules; forced-failure drill; commit `.out`+`.meta.json` and refresh `evidence/manifest.sh`, `publish_digests.sh`, `verify_publication_chain.sh`.
- Suggested validation: Spaces revoked → rule fires; package verification passes with the 1708-byte artifact.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: publication flow · Status: still-open.

### Finding ID: DR-P1-002 - Backup verification weaknesses: offsite retention deletes blobs by stale inventory; config tars lack digests; new-services/IRIS completeness unproven (prior LIVE-P0-002)

- Severity: P1 · Confidence: Medium-High (remote unverifiable here) · Area: DR · Status: partially-fixed (new-services gate) / open (retention)
- Evidence: `bootstrap/80-offsite-backup.sh:74` (inventory = full `find` of the local repo), `:139-150` (delete every file listed in inventories beyond 7; failures `|| true`); `:77-96` samples 3 files **before** deletion; 09-30 log "deleting remote files for snap-20260923-033053" 07:37→07:43Z; P6-G03 ledger note "retention deletion path not yet exercised"; P9-G09 shows a deduplicated repo (915 files / 2.6 GB for ~8 snapshots); config tars lack a recorded digest (`85:27-33`); new-services check fix since `d0f4aaf` (`backup_new_services.sh:52` exits 1 on a missing item) but the last real capture (`REVIEW-FIX/…004624Z`) shows 4× `[MISSING]`, no post-fix `[ok]` exists, and `:38-45` silently drops the IRIS dump when `pg_dump` fails (the critical list `:49` omits the dump); synthetic tar 1.35 test shows the current check can match.
- What is happening: OpenSearch repos share segment blobs across snapshots; the remote pruner cannot know which blobs newer snapshots still reference, and each run re-uploads everything *before* deleting, leaving the remote incomplete until the next run; meanwhile the new-services gate is unproven and an IRIS dump failure leaves a "complete-looking" archive.
- Why it matters: the last-line copy may not restore when needed, and the keys/registry/IRIS set is the unrecoverable one.
- User / business impact: recovery failure discovered at incident time; missing case data/keys while backup reports success.
- Security / privacy / reliability impact: unrecoverable cold-tier loss; silent loss of security state.
- Recommended fix: compute the retained union of all non-retired inventories and delete only files absent from it; run the post-deletion check (or scheduled restore) and fail the run if the retained set is incomplete; record archive digests; capture one real `[ok]`×4 new-services run and fail when the IRIS container exists but no dump was produced.
- Suggested validation: after retention, restore the newest snapshot from Spaces on a scratch node; rerun the archive with `[ok]` evidence and simulate a dump failure → nonzero.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: offsite access/root run · Status: partially-fixed / open.

### Finding ID: DR-P1-003 - Backup structure: duplicate snapshots/config per run, undocumented window, rehearsal narrower than the claim (prior LIVE-P1-005)

- Severity: P1 · Confidence: High · Area: DR · Status: still-open
- Evidence: `85:18-25` and `80:59-69` both create snapshots; both create config tars (`85:27-33`, `80:98-105`); local keep 3 (`disk_guard.sh:14`), offsite keep 7 (`80:19`), ISM delete 14 d; `RESTORE.md:179-190` records RPO/RTO only; `restore_rehearsal.sh:5` (`set -uo pipefail`, no `-e`), `:63-76` restores from the **local** repo; last run T-P9-G06-367 (2026-09-23); `PATCH_MAINTENANCE.md:14` claims "monthly restore rehearsal" with no timer; P9-G09 was central-only.
- What is happening: one run doubles snapshot/archive work and only one snapshot is inventoried; no doc states how long a deleted index stays restorable; the repeatable drill can print mismatch/FAILED and still exit 0 while never proving offsite, edge, Wazuh or new-services recovery.
- Why it matters: storage/upload waste, ambiguous authority, false confidence in "tested" restores.
- User / business impact: long offsite lag windows; surprise data loss after the effective window.
- Security / privacy / reliability impact: untested key/PKI dependencies fail in a real incident.
- Recommended fix: pass `85`'s snapshot to `80` (pure uploader) and drop the second config tar; document per-store windows; add fail-fast assertions + offsite-restore leg; schedule and widen the drill.
- Suggested validation: one snapshot+archive/day; corrupted archive → nonzero; ISM-deleted index restored within the documented window.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: lab window · Status: still-open.

### Finding ID: DR-P1-004 - Secrets and backup-key custody unverified; offsite archives depend on a host-only key

- Severity: P1 · Confidence: High (repo) / Unknown (owner copies) · Area: DR · Status: open
- Evidence: `RESTORE.md:30-31,47,93-103` (secrets excluded by design; `backup_enc.key` never in the backup; owner custody path); `80:101-104,117-124` / `85:30-32` encrypt with `/srv/falcon/secrets/backup_enc.key`; P9-G09 ledger deviation "stack uses the lab secrets (owner custody path pending)"; `/home/user/.env` holds Spaces/R2 credential names (`s3_kid/s3_key`, `cf_r2_akid/sak` — names only).
- What is happening: if only host copies exist, encrypted offsite archives, snapshot access and the R2 tier are unrecoverable after host loss.
- Why it matters: a backup you cannot decrypt is not a backup.
- User / business impact: total-loss recovery stalls at key custody.
- Security / privacy / reliability impact: DR depends on undocumented owner material.
- Recommended fix: record an owner key-custody attestation (offline locations for `backup_enc.key`, CA, cloud keys) and exercise a decrypt/read test from custody; document rotation interplay.
- Suggested validation: drill decrypts the newest offsite archive using only the custody copy.
- Owner suggestion: owner + maintainer · Effort: S/M · Dependencies: owner · Status: open.

### Finding ID: DR-P1-005 - Edge PKI/DB backup remains local-only (prior INTG-P1-003); archives also sit in the release surface

- Severity: P1 · Confidence: High · Area: DR · Status: still-open
- Evidence: edge `automation/validation/backup_edge_secrets.py:31` → `/home/user/falcon-edge-delivery` (keep 7, same host); falcon `80` uploads only OpenSearch snapshots + falcon config/new-services; no offsite reference in the edge repo; delivery shows two archives (01:10Z user, 01:13Z root, 1.74/1.81 MB); release manifest lists them (`falcon-edge-release-manifest-20260930.json:49-59`); prior INTG-P2-003.
- What is happening: the fleet trust anchor (CA key, signing seed, control-plane DB) exists only on the shared host, inside a directory shared with release artifacts.
- Why it matters: host loss = fleet-wide re-enrollment/trust reset; secret-material distribution risk.
- User / business impact: multi-day fleet recovery; reviewer friction.
- Security / privacy / reliability impact: blast radius covers every enrolled sensor.
- Recommended fix: add the archive to the offsite flow with round-trip verification (or record explicit owner acceptance); separate backup ownership/schedule and keep secrets out of the release surface.
- Suggested validation: restore edge PKI/DB from offsite on a scratch host; re-enroll a test sensor.
- Owner suggestion: both maintainers · Effort: S/M · Dependencies: secret doctrine · Status: still-open.

### Finding ID: DR-P2-001 - Datasets with no backup are only partially accepted

- Severity: P2 · Confidence: High · Area: DR · Status: open
- Evidence: `85:19` snapshots `falcon-*` only (`include_global_state:false`); `/opt/wazuh-backups/elasticsearch` mtime 2026-09-21T15:17Z (sibling DATA-P1-002, not duplicated); edge archives host-local (DR-P1-005); no timer/script backs up Grafana SQLite, Prometheus TSDB, ntfy or Redis; `RESTORE.md:156-159` rebuilds/accepts only `.opendistro_security`, dashboards objects and "Grafana local DB"; R2 = manual single-index mount (SEARCH-P2-004).
- What is happening: the coverage map is implicit and partially contradictory.
- Why it matters: recovery plans silently omit services whose data disappears.
- User / business impact: dashboard/history loss; Wazuh identity/config loss.
- Security / privacy / reliability impact: restore claims overstated.
- Recommended fix: publish a dataset→backup→window→owner matrix; record "back up" or owner-accepted loss for each; link it from RESTORE.md.
- Suggested validation: every dataset has a disposition; no row contradicts `grep` evidence.
- Owner suggestion: maintainer + owner · Effort: S/M · Dependencies: owner decisions · Status: open.

### Finding ID: DR-P2-002 - No bad-migration/rollback drill exists for the index-rename path

- Severity: P2 · Confidence: High · Area: DR · Status: open
- Evidence: `automation/validation/index_rename_migration.sh` (reindex mon-*→falcon-*; only comment guard at :40 "never delete a source index until counts match"); P6-G03 rename evidence shows the real migration; no abort/partial-failure test in `test_execution.csv`; companion plan adds one.
- What is happening: the one production-shaped migration has no exercised rollback (partial reindex, interrupted task, wrong mapping).
- Why it matters: a failed rename in a maintenance window risks data loss/duplication.
- User / business impact: prolonged outage or corrupted indices.
- Security / privacy / reliability impact: recovery relies on ad-hoc operator judgment.
- Recommended fix: script and execute a bad-migration drill on a fixture index (interrupt reindex; verify no source deletion, counts, cleanup) and capture evidence.
- Suggested validation: drill evidence with PASS criteria under a new capture.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: lab window · Status: open.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Offsite stale/incomplete at host loss | High | Medium | Data loss | DR-P1-001/002 | Metric/rule; safe retention; restore test |
| Retention deletes needed blobs | High | Low-Med | Unrecoverable cold tier | DR-P1-002 | Retained-union delete; verify |
| Key custody missing | High | Low-Med | Recovery stall | DR-P1-004 | Attestation; decrypt drill |
| Edge fleet trust lost | High | Low | Fleet re-enrollment | DR-P1-005 | Offsite edge backup |
| Rehearsal false comfort | Medium | Medium | Hidden failures | DR-P1-003 | Assertions; widen; schedule |
| Wazuh data unrecoverable | High | Low | Forensic loss | DATA-P1-002 | Back up or accept |
| Duplicate jobs/waste | Medium | High | Long lag | DR-P1-003 | De-dup |

## Recommendations

### Immediate / Release Blocking
1. Commit/rebind the offsite-recovery evidence; refresh manifests (DR-P1-001).
2. Add `offsite_last_success` + `new-services_last_success` gauges/rules (DR-P1-001).
3. Fix offsite retention: delete only files absent from the retained union (DR-P1-002).

### This Week
4. De-duplicate snapshot/config creation; pass the snapshot name to the uploader (DR-P1-003).
5. Capture one real `[ok]` new-services run; fail on a missing IRIS dump (DR-P1-002).
6. Record key-custody attestation and the edge offsite decision (DR-P1-004/005); add fail-fast assertions + an offsite-restore leg to the drill (DR-P1-003).

### This Month
7. Publish the dataset coverage matrix; dispose of Wazuh/Grafana/Prometheus/ntfy/Redis (DR-P2-001).
8. Document recoverability windows; add an ISM-delete → restore test (DR-P1-003); execute the drill plan incl. bad migration (DR-P2-002).

### Later / Platform Evolution
9. Weekly restoration canary from the offsite copy on a scratch node.
10. Automate R2 registration/lifecycle or formally retire the searchable tier (SEARCH-P2-004).

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Offsite epoch metric + rule | Ends silent offsite staleness | `export_monitor_metrics.sh`, `90-alerting.sh`, `85-backup-job.sh` | Forced-failure drill fires |
| Commit offsite evidence | Package matches reality | `evidence/raw/REVIEW-FIX/*`, manifests | `verify_publication_chain.sh` = 0 |
| Snapshot reuse in uploader | Removes duplicate snapshot | `85-backup-job.sh`, `80-offsite-backup.sh` | One snapshot/day |
| Retained-union retention | Protects cold tier | `80-offsite-backup.sh` | Post-retention sample verify |
| Fail on missing IRIS dump | Stops silent coverage loss | `backup_new_services.sh` | Simulated failure exits 1 |
| Drill exit codes | Makes rehearsals meaningful | `restore_rehearsal.sh` | Corrupt input → nonzero |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Offsite/new-services freshness instrumentation | P1 | falcon maintainer | S | none |
| Reference-safe remote retention + verify | P1 | falcon maintainer | M | offsite keys |
| Drill hardening + scheduling | P1 | falcon maintainer | M | lab window |
| Key-custody attestation + decrypt test | P1 | owner + maintainer | S/M | owner |
| Edge PKI/DB offsite | P1 | edge + falcon maintainer | S/M | secret doctrine |
| New-services `[ok]` capture + IRIS gate | P1 | falcon maintainer | S | root run |
| Dataset coverage matrix; bad-migration drill | P2 | falcon maintainer | S/M | owner decisions |
| Wazuh indexer backup (DATA-P1-002); R2 automation or retirement | P1/P2 | maintainer + owner | M | Wazuh creds / owner |

## Suggested Tests

- Shell: `restore_rehearsal.sh` exits nonzero on SHA mismatch/restore failure; `backup_new_services.sh` exits nonzero on a missing critical item or IRIS dump; shellcheck in CI.
- Integration: forced offsite failure → offsite-stale alert; post-retention restore of the newest snapshot from Spaces on scratch; ISM-deleted index recovery within the documented window.
- E2E/security: extend P9-G09 with edge PKI/DB + new-services restore (re-enroll a test sensor); decrypt using only the custody key copy; verify archive encryption/perms and scan the delivery dir.
- Regression/manual: one snapshot + archive per daily run; `ci/validate.sh` passes with committed evidence; quarterly bad-migration drill; annual total-loss walkthrough.

## Suggested Documentation Updates

- `docs/phase7/runbooks/RESTORE.md`: refresh assets; add per-store windows, key custody, offsite verification semantics, coverage-matrix link.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: correct "searchable snapshots blocked" to the working R2 state + manual registration.
- `docs/phase7/runbooks/PATCH_MAINTENANCE.md`: align rehearsal cadence with a real timer or mark "when scheduled".
- `docs/phase9/CLEAN_HOST_REBUILD_RUNBOOK.md`: add edge PKI/DB and new-services steps.
- New `docs/runbooks/BACKUP_COVERAGE_AND_WINDOWS.md`.
- `mct/runbooks/backup-*`, `dr-restore-*`, `mct/scripts/backup-*`: "imported MCT — not the falcon procedure" banner (unwired legacy estate).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Do owner-custody copies of `backup_enc.key`, CA and cloud keys exist, and where? | Decryptability after host loss | Owner attestation; decrypt drill |
| Do the newest remote snapshots actually restore after retention? | Falsifies DR-P1-002 | Root + Spaces keys; scratch restore |
| Was the 03:34 new-services check `[ok]` or `[MISSING]`? | Closes LIVE-P0-002 | `/srv/falcon/backups/new-services.log` (root) |
| Intended post-deletion window (3, 7 or 14 days)? | RPO expectations | Owner decision; retention test |
| Is Wazuh indexer data backed up off-host anywhere? | DATA-P1-002 | Wazuh creds; repo listing |
| Back up or accept Grafana/Prometheus/ntfy/Redis; does R2 replace Spaces? | Coverage/cost closure | Owner decision |

## Appendix

- Pipeline: `falcon-backup.timer` 03:30Z → `85-backup-job.sh` (snapshot #1, config #1, epoch, new-services, offsite call) → `80-offsite-backup.sh` (Spaces probe, snapshot #2, repo upload, config #2 upload, new-services upload, 3-file verify, retention).
- 09-30 timeline: scheduled offsite failed ~03:34Z silently; manual fix/re-run 03:55:39–07:43:40Z exit 0; 1723 files inventoried; new-services uploaded; remote files for `snap-20260923-033053` deleted.
- Prior-run status: LIVE-P0-001 partially-fixed; LIVE-P0-002 partially-fixed; LIVE-P1-005 still-open; INTG-P1-003 still-open.
- Unverified live items: `/srv/falcon/backups` contents, OpenSearch cluster, Spaces/R2 listings (root/credential-only); companion plan: `backup_restore_drill_plan.md`.
