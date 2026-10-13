# 07_data_schema_migration_runtime_validation — Prompt 07 - Data, Schema, Migration, and Runtime Validation Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `07_data_schema_migration_runtime_validation.md` (area DATA, prompt)

## Verification Performed

# Data, Schema, Migration, and Runtime Validation Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: `falcon` @ `/tmp/opencode/falcon-audit-f5cb7c9`
- Branch: main (detached worktree at the audited commit; live tree `/home/user/falcon-build` verified identical: HEAD == f5cb7c9, clean)
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:33:09Z
- Auditor: subagent (read-only; live checks read-only)
- Area code: DATA
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/07_data_schema_migration_runtime_validation.md
- Scope limitations: no relational schema/migration system exists (the data contract is the pinned OpenSearch template + ISM + Vector validators). The Wazuh indexer and IRIS estates are partly owner-side; only read-only checks were performed. The falcon-edge control-plane SQLite DB is a separate repository. Cloudflare R2 lifecycle is owner-side.

## Scope

Reviewed the repository's data model (OpenSearch composable template, ISM policies), migrations/template evolution, constraints (validators, DLQ, dynamic:false), indexes, tenant columns, audit fields, retention/reclaim helpers, seeds/fixtures, generated artifacts and evidence binding, runtime validators, env/config validation, migration CI, rollback/drift/backup posture, and the live OpenSearch/Wazuh/IRIS retention and capacity state (read-only). Not reviewed: the falcon-edge control-plane DB schema (edge repo), IRIS Postgres schema (vendored third-party app), and owner-side R2 lifecycle.

## Evidence Reviewed

- `config/opensearch/falcon-eve-template.json`, `config/opensearch/*-ism-policy.json`, `config/opensearch/README.md`
- `bootstrap/61-search-policies.sh`, `bootstrap/60-central-deploy.sh` (watermarks, snapshot repo path), `bootstrap/85-backup-job.sh` (snapshot retention, config archive), `compose/central/docker-compose.yml` (snapshot bind, aggregator memory)
- `config/vector/{aggregator.yaml,edge.yaml}` (validation, DLQ, buffering)
- `automation/validation/{disk_guard.sh,export_monitor_metrics.sh,ism_retention_metrics.sh,edge_spool_metrics.sh,mapping_drift_check.py,consumer_query_check.sh,retention_sweep_check.sh,retention_execution_test.sh,write_rejection_test.sh,index_rename_migration.sh,index_rename_rollback_drill.sh,wazuh_indexer_backup.sh,check_generated_drift.py}`
- `docs/runbooks/{RETENTION_MATRIX.md,SCHEMA_AND_RETENTION.md,CAPACITY_AND_TELEMETRY.md,WAZUH_INDEXER_BACKUP.md,RUNTIME_AND_SCHEDULE.md}`, `docs/phase7/runbooks/RESTORE.md`, `docs/architecture/STORAGE_CAPACITY_MODEL.md`
- `ledgers/decision_log.md` (2026-10-09/10 entries), `ci/validate.py`
- Live (read-only, 2026-10-11 ~04:15-04:35Z): central OpenSearch `_cluster/health`, `_cat/indices`, `_cat/shards`, `_plugins/_ism/policies`, `_snapshot/falcon-backup/_all`, `_cluster/settings`; Wazuh indexer (127.0.0.1:9200) `_plugins/_ism/policies`, `_plugins/_ism/explain/*`, `_settings`, `_cat/indices`; Prometheus `query_range` (disk-guard root free, spool purge counters); `journalctl -u falcon-disk-guard.service`; `/srv/falcon/textfile/*.prom`; `docker inspect`; `du`/`df`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py` on a clean clone of f5cb7c9 | reproduction | Repo's own static validation claim | `validation_failures=0`; 50 shell suites PASS; publication equality PASS; generated-drift PASS |
| Live central OpenSearch cluster/indices | live read-only | Data model + capacity | yellow (45 unassigned = single-node replicas, `CLUSTER_RECOVERED`); `falcon-eve-2026.10.08` docs = 0 (permanent outage hole); 10.11 has 2.59 M docs |
| Live central ISM policies + retention metrics | live read-only | Retention enforcement | 7 policies (5 active + 2 stale exec/mon); `falcon_ism_deleted_indices_24h{falcon-eve-policy}=1`, last delete 2026-10-10T20:05Z; test-cleanup deleted 5 in the retained window |
| Live `_cluster/settings` | live read-only | Watermark posture | transient `{}`; persistent has only ISM migration keys; defaults 85/90/95 in effect (data LV 55% used) |
| Live snapshots `_snapshot/falcon-backup/_all` | live read-only | Backup/rollback state | 3 SUCCESS snapshots (10-09, 10-10, 10-11); 14-16 indices; 0 failed shards |
| Live Wazuh indexer ISM explain/settings | live read-only | Prior DATA-P1-001 reconciliation | 56 managed indices (auditlog 37, states 14, monitoring 2, statistics 2, elastiflow 1); all 15 `wazuh-alerts-4.x-*` NOT managed despite `_settings` naming `wazuh-retention` |
| Live disk-guard journal + metrics | live read-only | Retention/reclaim helper boundary behavior | root LV 20.69 GiB free < 20 GiB threshold; guard exits 1 "still below threshold after reclaim - alert sent" at 03:45/04:00/04:15Z |
| Live `du`/`df` + snapshot repo | live read-only | Root-LV capacity driver | `/var/lib/falcon-snapshots/opensearch` = 69 GiB; root 144 GiB used / 171 GiB (88%) |
| Prometheus `query_range` spool purge counter | live read-only | Ongoing edge data destruction | 1,743,575,365 B (10-09 13:30Z) -> 2,146,154,182 B now: 4 more 134 MiB purges since the prior audit |
| Live Grafana rules (read-only API) | live read-only | Retention/drop alerting | 86 rules; "Disk space low" firing (root >85%); no rule on `falcon_disk_guard_root_free_bytes` |

### Prior-run reconciliation (run falcon-20261009-2117-full-08e20d1; verification run falcon-20261011-0400-verify-main-584e1a3)

- **DATA-P0-001 (41-hour EVE outage, data loss; durable capacity fix absent)** — prior status `open`. Current: **verified-fixed at the current commit and live.** The incident recovered 2026-10-09T17:00Z; the durable fixes are now in the audited tree and live: snapshot repo relocated off the data LV (`compose/central/docker-compose.yml:78` -> `/var/lib/falcon-snapshots/opensearch`; `bootstrap/60-central-deploy.sh:245-255` creates the path + compatibility symlink), aggregator memory 512M -> 1G (`compose/central/docker-compose.yml:149-155`; live `Memory=1073741824`, `RestartCount=0`), disk guard watches both LVs (`disk_guard.sh:22-24`), nightly backup retries 3x + immediate alert (`bootstrap/85-backup-job.sh`), watermarks back to defaults (live settings). The `falcon-eve-2026.10.08` index remains permanently empty (0 docs) — recorded, not re-raised. Residual capacity risk is reported as new finding DATA-P2-002 (root LV).
- **DATA-P1-001 (Wazuh/IRIS retention incomplete; repo statement contradicts live)** — prior status `partially-fixed` / owner-accepted. Current: **still current; kept with the prior ID.** The live Wazuh estate improved (states now managed; elastiflow-flow managed) but the highest-volume class (`wazuh-alerts-4.x-*`, 15 indices) is **not** in ISM's managed set despite its index settings naming `wazuh-retention`, and the newest monitoring/statistics indices are unmanaged. The repository still states no Wazuh retention exists (`RETENTION_MATRIX.md:19-27`), and IRIS remains unbounded.
- Prior DATA-P2-005 (DLQ quota) and DATA-P2-006 (mapping drift): live checks confirm the DLQ is bounded (`falcon_disk_guard_dlq_bytes` 560,799; 30 d/64 MiB quota; today's file protected) and mapping drift is current=0 with the documented legacy residual (3 indices x `dest_ip`/`event_time`/`alert.severity`/`alert.category`). Not re-raised.

## Executive Summary

There is still no relational schema or migration system: the data contract is the pinned `falcon-eve` composable template (`dynamic:false`, ~485 fields), the five active ISM policies, the Vector ingest validators and the file DLQ. The platform's own static validation is green on a clean clone (`ci/validate.py`: 0 failures, 50 suites), the central EVE retention provably deletes (1 delete/24 h, fresh metric), the snapshot set is healthy (3 SUCCESS snapshots), and the 2026-10-07/09 capacity incident has a real, in-tree, live-verified remediation (DATA-P0-001 now closed).

Three current data-lifecycle issues remain. First, the Wazuh estate retention is still incomplete and the repository statement still contradicts the live estate: the 15-index `wazuh-alerts-4.x-*` class is not ISM-managed even though its index settings name the policy (an attachment that never took effect), the newest monitoring/statistics indices are unmanaged, and IRIS case data remains unbounded (DATA-P1-001). Second, the relocation that ended the incident moved the 69 GiB snapshot repository onto the root LV; root free is now 20.7 GiB, below the disk guard's 20 GiB threshold, so the guard fails every 15 minutes, alerts every 15 minutes, and cannot reclaim back above the threshold — the capacity fix is again marginal (DATA-P2-002). Third, the edge control-plane spool keeps destroying ~134 MiB per 10-14 hours (four more purges since the last audit) with no consumer ever removing a spool file and an alert threshold (256 MiB/6 h) that cannot fire at that rate (DATA-P2-003).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| EVE template | `config/opensearch/falcon-eve-template.json` | Index schema | Pinned, `dynamic:false` | Low | live current-index drift 0 |
| ISM policies (central) | `config/opensearch/*-ism-policy.json` | Retention | 5 active + 2 stale definitions | Low | 14 d/30 d/1 d verified live |
| Wazuh indexer retention | Wazuh cluster ISM + `mct/runbooks/index-retention-policy.md` | Retention | Partial: alerts unmanaged, newest mon/stats unmanaged | High | repo doc says "none" |
| IRIS case DB | `docs/phase7/runbooks/RESTORE.md:350` | Case data | Unbounded, OPEN | High | 78 MB today; owner decision |
| Ingest validators | `config/vector/aggregator.yaml:44-114` | Field validation | site_id/sensor_id -> DLQ | Low | sink failures NOT dead-lettered (WH-P1-001) |
| Edge buffer/spool | `config/vector/edge.yaml:249-256`; `automation/validation/edge_spool_metrics.sh` | Backpressure | 2 GiB disk buffer `block`; spool 128 MiB rotation, purges data | High | +402 MB purged since 2026-10-09 |
| Snapshot repository | `/var/lib/falcon-snapshots/opensearch` (root LV) | Rollback/backup | 69 GiB, keep 3, 3 SUCCESS | High | root free below guard threshold |
| Disk guard | `automation/validation/disk_guard.sh` | Reclaim/retention helper | Both LVs watched; failing every 15 min (root below threshold) | High | reclaim keeps 3 snapshots/3 configs |
| Config archive | `bootstrap/85-backup-job.sh:78-84` | Backup | `.enc` created; plaintext `.tar.gz` left in place | Medium | 5.8 MB/day unencrypted |
| Config validation | `ci/validate.py` | Static gates | PASS on clean clone | Low | 50 suites, 0 failures |
| Generated binding | `evidence/MANIFEST.sha256`, `check_generated_drift.py` | Drift | PASS | Low | generated-drift check green |
| Wazuh indexer backup | `automation/validation/wazuh_indexer_backup.sh` + `falcon-wazuh-backup.timer` | Backup | Last success 2026-10-11T03:05Z; keep 14 | Low | new since the prior run |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database schema | 3 | pinned template + drift checks | legacy indices unmapped | owner-gated reindex (documented) |
| Migrations | 3 | file-driven template/ISM; `index_rename_migration.sh` + rollback drill | no change ledger for template edits | record template change history |
| Constraints | 3 | `dynamic:false`, validators, DLQ | sink rejections not dead-lettered | route sink failures to a DLQ (WH-P1-001) |
| Indexes | 3 | 1 shard/0 replicas, keyword pins | legacy mapping drift | documented residual |
| Foreign keys/cascades | N/A | no relational store | - | - |
| RLS | N/A | see domain 37 report | - | - |
| Tenant columns | 3 | `site_id`/`sensor_id` present, validated | not storage-enforced (single tenant) | keep scope documented |
| Soft deletes | N/A | delete-only retention by design | - | - |
| Audit fields | 3 | `ingested_at`/`edge_ingested_at`/`event_time` | partial `event_time` on legacy feeds | documented |
| Retention | 2 | central ISM working; Wazuh partial; IRIS none; docs stale | coverage + statement drift | DATA-P1-001 |
| Seeds/fixtures | 3 | fixture cleanup policy 1 d, deletes verified | - | - |
| Generated DB types | N/A | no generated types | - | - |
| Capacity/reclaim | 2 | relocation + guard live | root LV below threshold; guard failing | DATA-P2-002 |

## Detailed Review

### Item: Central OpenSearch data model and retention

- Evidence: `config/opensearch/falcon-eve-template.json`, `config/opensearch/*-ism-policy.json`, live `_cat/indices`, `_plugins/_ism/policies`, `falcon_retention.prom`.
- What it does: composable template `falcon-eve` (`dynamic:false`, 1 shard/0 replicas) pins consumer fields; ISM deletes EVE at 14 d, top_queries at 14 d, auditlog at 30 d, ISM history at 30 d, fixtures at 1 d.
- Current controls: deletion metrics (`falcon_ism_deleted_indices_24h`, fresh), mapping-drift runner (current 0), consumer-query checker.
- Missing controls: per-class accelerated delete tests beyond fixtures (documented residual); legacy mapping repair is owner-gated.
- Risks: low; deletion provably works.

### Item: Wazuh indexer retention (DATA-P1-001)

- Evidence: live Wazuh indexer `_plugins/_ism/explain/*` (`total_managed_indices=56`), `_settings`, `_cat/indices`; `docs/runbooks/RETENTION_MATRIX.md:19-27`, `docs/runbooks/SCHEMA_AND_RETENTION.md:65`; `mct/runbooks/index-retention-policy.md`.
- What happens: five policies exist; managed set = security-auditlog (37), wazuh-states (14), monitoring (2), statistics (2), elastiflow-flow (1). All 15 `wazuh-alerts-4.x-*` indices (the highest-volume class, 2026.09.27-2026.10.11) are absent from the managed set even though `_settings.index.plugins.index_state_management.policy_id = wazuh-retention` is set on them. `wazuh-monitoring-2026.40w` and `wazuh-statistics-2026.40w` are also unmanaged. The repository still states "no ISM policy exists on the Wazuh indexer cluster".
- Missing controls: attachment verification (setting != enforcement), coverage checker, IRIS lifecycle decision.

### Item: Disk guard / root-LV capacity (DATA-P2-002)

- Evidence: `automation/validation/disk_guard.sh:22-29,110-118,142-159`; live journal; `falcon_disk_guard.prom`; `du -sh /var/lib/falcon-snapshots/opensearch` = 69 GiB; `df` root 88%.
- What happens: the guard reclaim path keeps the newest 3 snapshots and 3 config archives; with exactly 3 snapshots and no other reclaimable class it cannot raise root free above the 20 GiB threshold; it alerts (relay) and exits 1 every 15 minutes.
- Missing controls: no rule on `falcon_disk_guard_root_free_bytes`; no automated re-tune of snapshot keep-count/capacity; the fixed 20 GiB constant does not scale with the volume (cf. PERF-P2-002 class).

### Item: Edge control-plane spool (DATA-P2-003)

- Evidence: `automation/validation/edge_spool_metrics.sh` (semantics: overwrite = dropped bytes), live `falcon_edge_spool.prom`, Prometheus range.
- What happens: 25 spool files (12 rotated) from 2026-09-29 onward, `removed_files_total=0`; `purged_bytes_total` grows by one full 134 MiB rotation every ~10-14 h.
- Missing controls: no drain/consumer visible from the repo; purge-burst rule threshold 256 MiB/6 h cannot fire at the observed rate.

### Item: Backup artifacts (DATA-P3-004/005)

- Evidence: `bootstrap/85-backup-job.sh:78-84`; live `/srv/falcon/backups/`; `docs/runbooks/SCHEMA_AND_RETENTION.md:53`; `docs/runbooks/RETENTION_MATRIX.md:39`.
- What happens: the plaintext config archive is never removed after encryption; the retention docs still describe a 2/day cadence with "keep 7" and omit the new Wazuh indexer backup job.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DATA-001 | Database schema | `falcon-eve-template.json` | pinned, dynamic:false | legacy indices | P3 | owner-gated reindex |
| DATA-002 | Migrations | `bootstrap/61`, rename scripts | file-driven, idempotent, rollback drill | no change ledger | P3 | record template change history |
| DATA-003 | Constraints | validators + DLQ | validation errors captured | sink errors not | P1 | sink DLQ (WH-P1-001) |
| DATA-004 | Indexes | live `_cat/indices` | keyword pins, 1 shard | legacy drift | P3 | documented |
| DATA-005 | Foreign keys/cascades | n/a | n/a | n/a | - | - |
| DATA-006 | RLS | domain 37 | n/a | n/a | - | - |
| DATA-007 | Tenant columns | `site_id`/`sensor_id` | validated | not storage-enforced | P3 | document single tenant |
| DATA-008 | Soft deletes | n/a | delete-only retention | - | - | - |
| DATA-009 | Audit fields | `ingested_at` | present | partial `event_time` legacy | P3 | documented |
| DATA-010 | Retention | ISM + Wazuh + IRIS | partial | alerts unmanaged / IRIS / docs | P1 | DATA-P1-001 |
| DATA-011 | Seeds/fixtures | test-cleanup policy | 1 d delete verified | - | - | - |
| DATA-012 | Generated DB types | n/a | n/a | - | - | - |
| DATA-013 | Capacity/reclaim | guard + snapshot repo | relocation + guard live | root below threshold, guard failing | P2 | DATA-P2-002 |
| DATA-014 | Spool boundary | spool metrics | observable | continuous purges, threshold blind | P2 | DATA-P2-003 |
| DATA-015 | Backup artifacts | 85-backup-job | encrypted archive | plaintext retained | P3 | DATA-P3-004 |

## Findings

### DATA-P1-001 - Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate

- Severity: P1
- Confidence: High (live ISM managed-index list, settings, index list; repo docs)
- Area: DATA
- Evidence:
  - `docs/runbooks/RETENTION_MATRIX.md:19-27` ("none configured (GAP)"; "no ISM policy exists on the Wazuh indexer cluster"); `docs/runbooks/SCHEMA_AND_RETENTION.md:65` ("not managed here", DATA-P1-002).
  - Live Wazuh indexer (127.0.0.1:9200): `_plugins/_ism/explain/*` -> `total_managed_indices=56`; per-class: `security-auditlog-*` 37 managed, `wazuh-states-*` 14 managed, `wazuh-monitoring-2026.38w/39w` + `wazuh-statistics-2026.38w/39w` managed, `elastiflow-flow-...-clean` managed by `elastiflow` (rollover + delete @14d).
  - All 15 `wazuh-alerts-4.x-2026.09.27..2026.10.11` indices are NOT in the managed set (`policy_id: null`, `enabled: null`), while their `_settings` name `wazuh-retention` — the attachment never took effect (setting != enforcement).
  - `wazuh-monitoring-2026.40w` and `wazuh-statistics-2026.40w` are unmanaged (newest period).
  - `docs/phase7/runbooks/RESTORE.md:350` IRIS case DB "unbounded | OPEN"; live `iris-web_db_data` 78 MB with no retention job.
- What is happening: the audit trail's statement about Wazuh retention is stale in both directions (it now overstates the gap for states/auditlog and understates it for alerts), and the highest-volume Wazuh class is effectively unmanaged.
- Why it matters: capacity planning and privacy decisions rely on this matrix; unmanaged alert indices grow unbounded on the shared host.
- User / business impact: disk exhaustion risk on the Wazuh estate; inconsistent auditlog/alert lifecycle (180 d vs none).
- Security / privacy / reliability impact: alert data retained indefinitely; an expected 30 d window is not enforced.
- Recommended fix: correct `RETENTION_MATRIX.md`/`SCHEMA_AND_RETENTION.md` to the live policy set; re-attach `wazuh-retention` to `wazuh-alerts-4.x-*` (and the newest monitoring/statistics) or record the exception; add a read-only checker comparing ISM's managed set against a declared per-class matrix; owner decision on IRIS case-data lifecycle.
- Suggested validation: the checker fails on a class with no managed policy; `_plugins/_ism/explain` shows the alerts class managed; a delete action is recorded in ISM history after the window.
- Owner suggestion: owner (data lifecycle) + ops
- Effort estimate: S (docs) / M (policies/checker) / L (IRIS decision)
- Dependencies: Wazuh stack maintenance window; owner IRIS decision
- Status: partially-fixed (prior ID DATA-P1-001)
- Endpoint / data path: Wazuh indexer `https://127.0.0.1:9200/_plugins/_ism/*`; IRIS Postgres volume
- Attack path: none identified

### DATA-P2-002 - Root LV is below the disk guard's threshold: the guard fails every 15 minutes and cannot reclaim back above it

- Severity: P2
- Confidence: High (live journal, metrics, df/du at audit time)
- Area: DATA
- Evidence:
  - `journalctl -u falcon-disk-guard.service` 2026-10-11T03:45/04:00/04:15Z: `root_free=20720072KB/20710412KB/20693304KB` vs `root_threshold=20971520KB` (20 GiB); "BELOW THRESHOLD: reclaiming"; "free now=... root free now=..."; "still below threshold after reclaim - alert sent"; unit exits 1 (failed).
  - `/srv/falcon/textfile/falcon_disk_guard.prom`: `falcon_disk_guard_root_free_bytes 21189922816` (19.73 GiB); `falcon_disk_guard_reclaims_total 50`.
  - `df`: root 171G total / 144G used (88%); `du -sh /var/lib/falcon-snapshots/opensearch` = 69 GiB (the snapshot repository relocated to root on 2026-10-09).
  - Prometheus range `falcon_disk_guard_root_free_bytes`: 27.9 GiB (10-10 03:00Z, before the nightly backup) -> 20.1 GiB (10-10 04:00Z) -> 26.1 GiB (10-11 03:00Z) -> 19.8 GiB (10-11 04:00Z): each nightly snapshot transiently consumes ~6-8 GiB while prune releases only part.
  - `automation/validation/disk_guard.sh:22-29` (10 GiB data / 20 GiB root constants; `KEEP_SNAPSHOTS=3`); `:142-159` (reclaim = newest 3 snapshots + 3 config archives, then alert+exit 1).
  - Live Grafana: "Disk space low" (root > 85%) firing; no rule exists on `falcon_disk_guard_root_free_bytes` (only the data-volume rule at `bootstrap/90-alerting.sh:539`).
  - Live relay metrics: `falcon_alert_relay_path_success_total{path="lab"}=9` in ~2 h — the guard's 15-minute alert is delivered on both paths.
- What is happening: the post-incident relocation solved the data-LV watermark problem by moving a 69 GiB, ~4.3 GiB/night-growing snapshot repository onto the root LV. The guard now trips on root every run, its reclaim set is already at its keep limits, and the resulting 15-minute alert loop is the steady state.
- Why it matters: the capacity fix is again marginal within 48 hours; if root fills, docker/backup/telemetry-adjacent services on the host are affected. The alert channel is also being consumed by a known, non-actionable repeat.
- User / business impact: operator alert fatigue; latent availability risk on the single host.
- Security / privacy / reliability impact: reliability; no direct security exposure.
- Recommended fix: choose a root-LV capacity policy that restores margin and stops the loop — e.g. reduce local snapshot keep to 2, move the snapshot repo to a dedicated LV/directory with a proportional threshold, raise the volume, and/or make the root threshold proportional; add an alert on `falcon_disk_guard_root_free_bytes` with hysteresis and a distinct "guard cannot reclaim" signal; update `docs/runbooks/CAPACITY_AND_TELEMETRY.md`.
- Suggested validation: run the guard with the new policy and assert root free > threshold with a stable margin across a nightly backup cycle; assert no failed guard unit and no 15-minute alert repeat.
- Owner suggestion: ops/owner (capacity decision)
- Effort estimate: S-M
- Dependencies: disk layout decision; backup retention policy
- Status: open (new; regression of the verified-fixed PERF-P1-002 control at the live state)
- Endpoint / data path: `/var/lib/falcon-snapshots/opensearch` (root LV) -> nightly snapshot -> `falcon-backup` repository
- Attack path: none identified

### DATA-P2-003 - Edge control-plane spool keeps purging ~134 MiB per 10-14 h; nothing consumes it and the purge alert cannot fire at that rate

- Severity: P2
- Confidence: High (Prometheus counter range, spool state file, metric semantics)
- Area: DATA
- Evidence:
  - `automation/validation/edge_spool_metrics.sh:1-40` (a rotation that overwrites the previous `.1` file is counted as dropped bytes; "bytes lost when the 128 MiB rotation overwrites the previous .1 file").
  - Live `falcon_edge_spool.prom`: `purged_bytes_total 2146154182`, `purged_files_total 16`, `rotations_total 26`, `removed_files_total 0`, `files 25`, `rotated_files 12`, `current_fill_ratio 0.088`, `rotated_bytes 134195373`.
  - Prometheus `query_range falcon_edge_spool_purged_bytes_total`: 1,743,575,365 (2026-10-09T13:30Z) -> 1,877,786,881 (10-09T23:30Z) -> 2,011,955,019 (10-10T13:30Z) -> 2,146,154,182 (10-10T23:30Z): four further 134 MiB purges after the incident recovery.
  - Spool state file `/srv/falcon/textfile/.falcon_edge_spool_state` lists per-day `vector-YYYYMMDD.ndjson` + `.1` files from 2026-09-29 to 2026-10-11, all still present.
  - `bootstrap/90-alerting.sh:611-613`: rule `falcon-edge-spool-purge-burst` fires only above 256 MiB per 6 h — the observed rate (~134 MiB/10-14 h) never reaches it.
- What is happening: the edge ingest spool overwrites a full 128 MiB rotated file roughly twice a day; no spool file has ever been removed/consumed per the metric, so the destruction is continuous rather than incident-driven, and the repository does not state whether the lab edge has a standing consumer outage or is intentionally write-only.
- Why it matters: a documented data-loss boundary is active but unowned and unalerted; if this spool is a delivery buffer, telemetry is being silently destroyed every day.
- User / business impact: ongoing (small) telemetry loss; forensics gaps; metric trust erosion.
- Security / privacy / reliability impact: reliability/data-integrity; no direct security exposure.
- Recommended fix: determine the spool's intended lifecycle (drain + delete on acknowledged delivery, or an explicit bounded archive); if purges are not acceptable, fix the consumer; if they are accepted, say so in `SCHEMA_AND_RETENTION.md` and tune the rule (e.g. alert on `increase(...[24h]) > 0` with a documented acceptance, or raise the threshold explicitly).
- Suggested validation: a drill that stops the consumer and asserts the purge alert fires within the documented window; a healthy-consumer test asserts `removed_files_total` increases and `purged_bytes_total` stays flat.
- Owner suggestion: edge maintainer + ops
- Effort estimate: S (rule/decision) / M (consumer fix)
- Dependencies: edge control-plane repository
- Status: open (new)
- Endpoint / data path: edge control plane `/home/user/falcon-edge-secrets/ingest` -> 128 MiB rotation
- Attack path: none identified

### DATA-P3-004 - Nightly backup leaves an unencrypted config archive beside the encrypted one and never removes it

- Severity: P3
- Confidence: High (script + live files)
- Area: DATA
- Evidence:
  - `bootstrap/85-backup-job.sh:79-84`: `tar -czf config-YYYYMMDD.tar.gz ...`; `openssl enc ... -out config-YYYYMMDD.tar.gz.enc`; no removal of the plaintext.
  - Live `/srv/falcon/backups/`: `config-20261011.tar.gz` (5,874,266 B, mode 0644, root) alongside `config-20261011.tar.gz.enc`; `config-20261010.tar.gz.enc` also retained.
  - `docs/runbooks/RETENTION_MATRIX.md:40` describes the class as "Encrypted config archives"; `automation/validation/disk_guard.sh:138-140` treats `config-*.tar.gz*` as reclaimable "old config archives" only under pressure.
- What is happening: the unencrypted copy of the repository-config archive persists daily (the archive contains the repo tree: config/compose/bootstrap/automation/ci/docs/ledgers/pins; no secret files are included, but it duplicates sensitive topology/runbook content in the clear).
- Why it matters: an unencrypted backup artifact with no stated retention accumulates on the host and contradicts the documented "encrypted" class; it is only cleaned by an emergency reclaim.
- User / business impact: small privacy/hygiene exposure; disk growth.
- Security / privacy / reliability impact: low-moderate (config/topology in the clear on a shared host filesystem).
- Recommended fix: `rm -f "$cfg"` (or `shred -u`) after a successful encryption, and state the local archive policy in the runbook.
- Suggested validation: a test asserts the plaintext is absent after the job; a negative test asserts a failed encryption keeps the plaintext.
- Owner suggestion: ops
- Effort estimate: S
- Dependencies: none
- Status: open (new)
- Endpoint / data path: `/srv/falcon/backups/config-YYYYMMDD.tar.gz`
- Attack path: none identified

### DATA-P3-005 - Retention documentation drift: snapshot cadence/keep count and the Wazuh indexer backup job are not reflected in the matrix

- Severity: P3
- Confidence: High
- Area: DATA
- Evidence:
  - `docs/runbooks/SCHEMA_AND_RETENTION.md:53`: "local snapshots (`falcon-backup`, 2/day) | newest 3 kept under pressure; repo keeps more".
  - `bootstrap/85-backup-job.sh:68-75`: routine retention keeps the newest 3 on every run; `config/systemd/falcon-backup.timer` runs daily (03:30Z), not 2/day.
  - `docs/runbooks/RETENTION_MATRIX.md:39`: "Local OpenSearch snapshots | keep 7".
  - `automation/validation/wazuh_indexer_backup.sh` + `falcon-wazuh-backup.timer` (keep 14; last success 2026-10-11T03:05:35Z) are absent from both retention documents.
- What is happening: three statements about snapshot retention disagree (2/day vs 1/day; keep 7 vs keep 3; Wazuh backup unlisted).
- Why it matters: operators and future audits reason from the matrix; the current mismatch caused confusion in the prior run's reconciliation.
- User / business impact: wrong capacity/restore expectations.
- Security / privacy / reliability impact: none direct.
- Recommended fix: update both documents to the as-built cadence/keep counts and add the Wazuh indexer snapshot class with its keep count and offsite path.
- Suggested validation: a doc test or checklist item comparing the matrix rows against `85-backup-job.sh`/`wazuh_indexer_backup.sh` constants.
- Owner suggestion: docs owner
- Effort estimate: S
- Dependencies: none
- Status: open (new)
- Endpoint / data path: n/a
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Root LV fills; backup/services fail | P2 | Medium (below threshold now, ~-0.4 GiB/day net) | Host-wide outage risk | DATA-P2-002 | capacity/keep policy + proportional threshold |
| Wazuh alerts grow unbounded | P1 | High (unmanaged today) | Disk exhaustion; privacy | DATA-P1-001 | attach policy + coverage checker |
| Continuous edge spool destruction | P2 | Certain (4 events since last audit) | Telemetry loss | DATA-P2-003 | fix consumer or record acceptance + rule |
| Unencrypted config archive accumulation | P3 | Certain | Privacy/hygiene | DATA-P3-004 | remove after encryption |
| Repo/live retention statement drift | P2 | Certain | Wrong owner decisions | DATA-P1-001/005 | correct docs + checker |

## Recommendations

### Immediate / Release Blocking
1. DATA-P2-002: stop the root-LV threshold breach (capacity or retention change) and remove the 15-minute alert loop.
2. DATA-P1-001: re-attach the Wazuh alerts policy (or record the exception) and open the IRIS lifecycle decision.

### This Week
3. DATA-P2-003: decide the spool lifecycle; fix the consumer or tune/document the rule.
4. DATA-P3-004: remove the plaintext config archive after encryption.
5. Add a root-free alert rule with hysteresis and a "guard cannot reclaim" signal.

### This Month
6. Retention coverage checker (live ISM managed set vs declared matrix).
7. Correct `RETENTION_MATRIX.md` / `SCHEMA_AND_RETENTION.md` (DATA-P1-001, DATA-P3-005).
8. Per-class accelerated delete tests beyond fixtures.

### Later / Platform Evolution
9. A dedicated volume/partition for the snapshot repository with proportional thresholds.
10. Owner-gated reindex/runtime-field repair of the pre-2026.10.01 mapping drift.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Remove plaintext config archive | Removes clear-text duplicate | `bootstrap/85-backup-job.sh` | file absent after job |
| Correct the retention matrix rows | Stops wrong decisions | `RETENTION_MATRIX.md`, `SCHEMA_AND_RETENTION.md` | diff vs live |
| Alert on any spool purge increase | Makes daily destruction visible | `bootstrap/90-alerting.sh` | forced purge -> firing |
| Root-free rule with hysteresis | Distinguishes real risk from loop | `bootstrap/90-alerting.sh` | live rule present |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Sink-failure DLQ + replay | P1 | ops | M | Vector config (WH-P1-001) |
| Wazuh retention coverage checker | P2 | ops | S | Wazuh creds |
| IRIS case-data lifecycle | P1 | owner | L | owner decision |
| Root-LV capacity policy | P2 | ops/owner | S-M | disk layout |
| Per-class delete tests | P3 | ops | S | ISM access |

## Suggested Tests

- Guard boundary test: mixed fresh/expired snapshots and config archives; assert the newest 3 survive and the guard's exit/alert behavior matches the policy.
- Root-capacity drill: run a nightly-backup cycle in a sandbox and assert root free stays above the (new) threshold and no guard failure occurs.
- Spool boundary test: mixed fresh/expired spool files; assert the purge alert fires at the documented threshold and `removed_files_total` semantics on consumption.
- Retention coverage test: an index class without a managed ISM policy fails the checker.
- Wazuh attachment test: create a scratch `wazuh-alerts-*` index and assert `_plugins/_ism/explain` shows it managed (or fails loudly).
- Backup artifact test: assert no plaintext archive remains after a successful run; a failed encryption keeps it.

## Suggested Documentation Updates

- `docs/runbooks/RETENTION_MATRIX.md`: Wazuh rows to the live managed set + exceptions; snapshot keep 3/1-per-day; add the Wazuh indexer snapshot class; IRIS status.
- `docs/runbooks/SCHEMA_AND_RETENTION.md`: fix line 53 (cadence/keep), line 65 (Wazuh backup job now exists), add the root-LV capacity note.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: record the root-LV threshold breach and the chosen capacity policy.
- `docs/runbooks/WAZUH_INDEXER_BACKUP.md`: link from the retention matrix.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why is `wazuh-alerts-4.x-*` not ISM-managed despite the setting? | Determines the fix (re-attach vs template) | ISM logs / index creation history |
| What is the intended edge spool lifecycle (drain vs archive)? | Bounds ongoing loss | edge repo design doc |
| What is the owner's root-LV capacity decision? | Stops the alert loop | owner decision |
| Is the oldest alerts index retention intentionally 30 d? | Privacy posture | owner decision |

## Appendix

- Central ISM policy list (live): falcon-auditlog-policy, falcon-eve-policy, falcon-ism-history-policy, falcon-test-cleanup-policy, falcon-topqueries-policy + stale falcon-retention-exec-20260922055012, mon-eve-policy.
- Wazuh ISM managed set (live): 56 indices — security-auditlog 37, wazuh-states 14, wazuh-monitoring 2, wazuh-statistics 2, elastiflow 1; unmanaged: wazuh-alerts 15, monitoring-40w, statistics-40w, elastiflow metric/path/telemetry.
- Snapshots (live): snap-20261009-164150, snap-20261010-033013, snap-20261011-033003 — all SUCCESS, 0 failed shards.
- Audit-time disk: root 144G/171G (88%, 20.7 GiB free); data LV 120.5G/230.9G used (55%, 96 GiB free); snapshot repo 69 GiB.
- `ci/validate.py` on a clean clone: `validation_failures=0` (50 suites, publication equality, image lock freshness, event_time consistency).

## Findings

| ID | Severity | Title |
|---|---|---|
| DATA-P1-001 | P1 | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate (alerts class not ISM-managed) |
| DATA-P2-002 | P2 | Root LV is below the disk guard's 20 GiB threshold: the guard fails every 15 minutes and cannot reclaim back above it (69 GiB snapshot repo on root) |
| DATA-P2-003 | P2 | Edge control-plane spool keeps purging ~134 MiB per 10-14 h; nothing consumes it and the purge alert cannot fire at that rate |
| DATA-P3-004 | P3 | Nightly backup leaves an unencrypted config archive beside the encrypted one and never removes it |
| DATA-P3-005 | P3 | Retention documentation drift: snapshot cadence/keep count disagree and the Wazuh indexer backup job is not in the matrix |
