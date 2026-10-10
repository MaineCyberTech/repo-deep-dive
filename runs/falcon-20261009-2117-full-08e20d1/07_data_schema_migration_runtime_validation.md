# 07_data_schema_migration_runtime_validation — Prompt 07 - Data, Schema, Migration, and Runtime Validation Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `07_data_schema_migration_runtime_validation.md` (area DATA, prompt)

## Verification Performed

# Data, Schema, Migration, and Runtime Validation Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: `falcon` @ `/tmp/opencode/falcon-audit-08e20d1`
- Branch: main (worktree detached at the audited commit)
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:50:50Z
- Auditor: subagent (read-only; live checks read-only)
- Area code: DATA
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/07_data_schema_migration_runtime_validation.md
- Scope limitations: the live host (`falcon`) currently runs the deploy tree `/home/user/falcon-build` at `main` = `6e4fccd` (two post-audit ops commits ahead of the audited `08e20d1`); live observations are timestamped and attributed. Wazuh indexer and IRIS estates are partly owner-side; only read-only checks were performed.

## Scope

Reviewed the repository's data model, index templates, ISM/retention policies, ingest validators, config validation, seeds/fixtures, generated artifacts and evidence binding, migration/reversibility posture, and the live OpenSearch/Wazuh/IRIS retention state (read-only). Not reviewed: application-level ORMs (none exist), the falcon-edge control-plane SQLite DB (edge repo), and owner-side Cloudflare R2 lifecycle.

## Evidence Reviewed

- `config/opensearch/falcon-eve-template.json`, `config/opensearch/*-ism-policy.json`, `config/opensearch/README.md`
- `bootstrap/61-search-policies.sh`, `bootstrap/60-central-deploy.sh` (watermarks, identities, snapshot repo)
- `config/vector/{aggregator.yaml,edge.yaml}` (ingest validation, DLQ, buffering)
- `automation/validation/{export_monitor_metrics.sh,mapping_drift_check.py,ism_retention_metrics.sh,consumer_query_check.sh,phase4_data_checks.sh,retention_execution_test.sh,retention_sweep_check.sh,disk_guard.sh,check_generated_drift.py}`
- `automation/evidence/manifest.sh`, `ci/validate.py`, `docs/runbooks/{SCHEMA_AND_RETENTION.md,RETENTION_MATRIX.md,CAPACITY_AND_TELEMETRY.md,WAZUH_INDEXER_BACKUP.md}`, `docs/phase7/runbooks/RESTORE.md`
- Live (read-only, 2026-10-09 ~21:20-21:45Z): central OpenSearch `_cat/indices`, `_plugins/_ism/policies`, `_cluster/settings`, `_cat/shards`; Wazuh indexer `_plugins/_ism/policies` + `_settings`; Prometheus `query_range`; docker logs (aggregator, probe vector-edge); `/srv/falcon/textfile/*.prom`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py` on a clean clone of `08e20d1` | reproduction | Repo's own static validation claim | `validation_failures=0`; generated-drift PASS; evidence-integrity PASS (1127 captures); event_time template/Vector consistency PASS |
| `python3 ci/validate.py --only generated-drift` | reproduction | Generated-artifact binding | PASS (evidence tree matches `evidence/MANIFEST.sha256`) |
| Live central OpenSearch ISM/index state | live read-only | Retention claims | 7 policies; `falcon-eve-*` 14d working (2 deletes/24h, metric fresh); oldest live index 2026.09.26 |
| Live Wazuh indexer ISM/`_settings` | live read-only | Prior DATA-P1-001 reconciliation | 5 policies exist; policy attached only to `wazuh-alerts-*` (30d) and `security-auditlog-*` (180d); monitoring/statistics/states/elastiflow unmanaged |
| Prometheus `query_range` (cluster status, EVE age, sink counters) | live read-only | Runtime validation of the ingest path | Cluster RED 2026-10-07T19:20Z -> 2026-10-09T17:00Z; EVE age peaked 143,946 s; sink sent counter flat ~38 h |
| `falcon-eve-2026.10.08` / `2026.10.09` searches | live read-only | Data-loss check | 10.08 docs = 0; 10.09 earliest `event_time` = 2026-10-08T03:15:01Z; delayed `ingested_at` 10-09T16:50Z |
| Edge spool + aggregator logs | live read-only | Data-loss quantification | `falcon_edge_spool_purged_bytes_total` 1,743,575,365 B; 13 purged rotations; "Not retriable; dropping the request" |

### Prior-run reconciliation (run falcon-20261005-full-main-e267ce1)

- **DATA-P1-001 (Wazuh and IRIS data have no retention)** — prior status `owner-accepted` / `still-open`. Current: **partially fixed in the live estate, but the repository statement is stale and coverage is incomplete.** The Wazuh indexer now carries five ISM policies (alerts 30d attached; auditlog 180d attached), which the repo's `RETENTION_MATRIX.md:19-27` still describes as "no ISM policy exists". `wazuh-monitoring-*`, `wazuh-statistics-*`, `wazuh-states-*` and `elastiflow-flow-*` still have no `policy_id` in authoritative `_settings`, and IRIS remains unbounded (`RESTORE.md:350` OPEN). Kept as current finding with the prior ID (partially-fixed).
- Prior 2026-10-02 findings DATA-P2-005 (DLQ quota) and DATA-P2-006/SEARCH drift checks: the DLQ quota is implemented (`disk_guard.sh:42-58`, today's file protected), and mapping-drift/consumer-query runners are live (current indices drift 0; legacy `dest_ip`/`event_time` residual 5 each). Not re-raised.

## Executive Summary

There is still no relational schema or migration system: the data contract is the pinned `falcon-eve` composable template (`dynamic:false`, 271 leaf paths), the ISM policies, the Vector ingest validators and the DLQ. The strongest points are real: `ci/validate.py` is green on a clean clone, the evidence manifest is drift-checked, the falcon-eve retention actually deletes, and the mapping-drift/consumer-query validators work.

The dominant risk is **runtime capacity/data-lifecycle failure**. Live evidence shows the OpenSearch cluster went RED on 2026-10-07 ~19:20Z and stayed red for ~45.5 hours; EVE ingestion stalled ~41 hours, the `falcon-eve-2026.10.08` index is permanently empty, the edge spool dropped ~1.74 GB across 13 purged rotations, and the aggregator logged non-retriable batch drops ("Not retriable; dropping the request") because the sink has no dead-letter path. The durable capacity fixes (snapshot repo moved off the data LV, watermark margin) exist only on post-audit `main` (`6e4fccd`), not at the audited `08e20d1`. Second, the Wazuh/IRIS retention statement in the repository contradicts the live estate and leaves several index classes unmanaged.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| EVE template | `config/opensearch/falcon-eve-template.json` | Index schema | Pinned, `dynamic:false` | Low | live drift 0 on current indices |
| ISM policies (central) | `config/opensearch/*-ism-policy.json` | Retention | 5 definitions applied + 2 stale | Low | 14d/30d/1d verified live |
| Wazuh indexer retention | `/opt/wazuh-docker` + `mct/runbooks/index-retention-policy.md` | Retention | Partial (alerts 30d, auditlog 180d; others none) | High | repo doc says "none" |
| IRIS case DB | `docs/phase7/runbooks/RESTORE.md:350` | Case data | Unbounded, OPEN | High | owner decision |
| Ingest validators | `config/vector/aggregator.yaml:44-114` | Field validation | site_id/sensor_id -> DLQ | Low | sink failures NOT dead-lettered |
| Edge buffer/spool | `config/vector/edge.yaml:249-256`; spool metrics | Backpressure | 2 GiB disk buffer `block`; spool 128 MiB rotation, purges data | High | 1.74 GB purged live |
| Config validation | `ci/validate.py` | Static gates | PASS on clean clone | Low | 50 test suites + checks |
| Generated binding | `evidence/MANIFEST.sha256`, `check_generated_drift.py` | Drift | PASS | Low | 1127 captures verified |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database schema | 3 | pinned template + drift checks | legacy indices unmapped | owner-gated reindex (documented) |
| Migrations | 3 | no SQL; template/ISM versioned by files + `bootstrap/61` | no migration ledger for template changes | add template-change history note |
| Constraints | 3 | `dynamic:false`, validators, DLQ | sink rejections not dead-lettered | route sink failures to a DLQ |
| Indexes | 3 | 1 shard/0 replicas, keyword pins | legacy mapping drift | documented residual |
| Foreign keys/cascades | N/A | no relational store | - | - |
| RLS | N/A | see domain 37 report | - | - |
| Tenant columns | 3 | `site_id`/`sensor_id` present, validated | not enforced at storage layer | keep single-tenant scope documented |
| Soft deletes | N/A | retention is delete-only by design | - | - |
| Audit fields | 3 | `ingested_at`/`edge_ingested_at`/`event_time` | event_time only on some feeds (documented) | - |
| Retention | 2 | central ISM working; Wazuh partial; IRIS none | coverage + stale docs | fix docs, attach remaining policies, owner IRIS decision |
| Seeds/fixtures | 3 | fixture cleanup policy 1d | - | - |
| Generated DB types | N/A | no generated types | - | - |

## Detailed Review

### Item: Central OpenSearch retention

- Evidence: `config/opensearch/*-ism-policy.json`, `bootstrap/61-search-policies.sh`, live `_plugins/_ism/policies`, `falcon_retention.prom`.
- Current controls: 14d EVE, 14d top_queries, 30d auditlog, 30d ISM history, 1d fixture cleanup; deletion metrics + proposed rules.
- Missing controls: per-class accelerated delete tests beyond fixtures (documented residual); no retention for the Wazuh estate beyond the classes noted.
- Risks: capacity pressure already materialised (P0 finding below).

### Item: Ingest sink delivery and buffering

- Evidence: `config/vector/aggregator.yaml:116-138`, `config/vector/edge.yaml:234-256`, live aggregator logs.
- What happens: validation rejects go to a file DLQ; sink write failures are dropped by Vector ("Not retriable") and are not dead-lettered; the only recovery is the bounded edge disk buffer (2 GiB, `when_full: block`) plus `ignore_older_secs: 86400`.
- Missing controls: sink-failure DLQ/replay; sink failure counters that actually increment (see WH-P1-001); a capacity guard tied to the data LV watermark domain.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DATA-001 | Database schema | `falcon-eve-template.json` | pinned, dynamic:false | legacy indices | P3 | owner-gated reindex |
| DATA-002 | Migrations | `bootstrap/61` | file-driven, idempotent | no change ledger | P3 | record template change history |
| DATA-003 | Constraints | validators + DLQ | validation errors captured | sink errors not | P1 | sink DLQ |
| DATA-004 | Indexes | live `_cat/indices` | keyword pins | legacy drift | P3 | documented |
| DATA-005 | Foreign keys/cascades | n/a | n/a | n/a | - | - |
| DATA-006 | RLS | domain 37 | n/a | n/a | - | - |
| DATA-007 | Tenant columns | `site_id`/`sensor_id` | validated | not storage-enforced | P3 | document single-tenant |
| DATA-008 | Soft deletes | n/a | delete-only retention | - | - | - |
| DATA-009 | Audit fields | `ingested_at` | present | partial `event_time` | P3 | documented |
| DATA-010 | Retention | ISM + Wazuh + IRIS | partial | Wazuh classes / IRIS / stale docs | P1 | see DATA-P1-001 |
| DATA-011 | Seeds/fixtures | test-cleanup policy | 1d delete | - | - | - |
| DATA-012 | Generated DB types | n/a | n/a | - | - | - |
| DATA-013 | Runtime capacity | live metrics/logs | single node, data LV | RED 45 h, data loss | P0 | capacity fix (already on main) |

## Findings

### DATA-P0-001 - 41-hour EVE ingestion outage with confirmed data loss; durable capacity fix absent from the audited tree

- Severity: P0
- Confidence: High (live metrics, logs, index state captured at audit time)
- Area: DATA
- Evidence:
  - Live Prometheus: `falcon_opensearch_cluster_status` = 2 (RED per the exporter mapping at `automation/validation/export_monitor_metrics.sh:103-107`) from 2026-10-07T19:20Z to 2026-10-09T17:00Z.
  - Live Prometheus: `falcon_eve_last_event_age_seconds` 1 s (10-08 00:00Z) -> 143,946 s (10-09 16:00Z) -> 1,126 s (10-09 17:00Z).
  - Live Prometheus: `falcon_pipeline_sink_sent_events_total` flat at 45,848,415 from 10-08T02:00Z to 10-09T16:00Z.
  - Live aggregator log `falcon-central-vector-aggregator-1` 2026-10-08T00:05:02Z: `unavailable_shards_exception: [falcon-eve-2026.10.08][0] primary shard is not active`, `Not retriable; dropping the request`, `component_events_dropped ... count=62/1227/13310`.
  - Live index state: `falcon-eve-2026.10.08` docs = 0 (shard STARTED); `falcon-eve-2026.10.09` earliest `event_time` = 2026-10-08T03:15:01Z; sample doc `edge_ingested_at` 2026-10-08T05:55Z vs `ingested_at` 2026-10-09T16:50Z.
  - Live edge spool: `falcon_edge_spool_purged_bytes_total` = 1,743,575,365 (~1.74 GB), `falcon_edge_spool_purged_files_total` = 13, active spool 113,057,370/134,217,728 (84%).
  - `config/vector/edge.yaml:15` (`ignore_older_secs: 86400`), `:249-256` (retry_attempts 10 / retry_max_duration_secs 300; disk buffer 2 GiB `when_full: block`); `config/vector/aggregator.yaml:116-138` (no sink DLQ).
  - Audited tree has no durable fix: `compose/central/docker-compose.yml:78` keeps the snapshot repo inside the data LV; `bootstrap/60-central-deploy.sh:232-245` sets only `enable_for_single_data_node`. `main`@`6e4fccd` (post-audit) relocates the repo to `/var/lib/falcon-snapshots/opensearch` and live watermarks are 93/96/98 persistent.
- What is happening: the single-node OpenSearch went red (capacity/watermark domain) and the write path failed for ~41 hours. Vector classified the `unavailable_shards_exception` responses as non-retriable and dropped whole batches; the bounded edge buffer and the control-plane spool evicted under pressure, so the events are gone, not merely delayed. The daily index for 2026-10-08 is permanently empty.
- Why it matters: this is the platform's core product (security telemetry). A capacity event silently converts an availability incident into data loss; detection relied on freshness, not on the drop counters (see WH-P1-001).
- User / business impact: 41 hours of IDS/flow/syslog telemetry absent; DFIR/IRIS cases built on that window have no raw evidence.
- Security / privacy / reliability impact: blind window in monitoring; forensic gaps; capacity risk remains structural at the audited commit.
- Recommended fix: land the capacity work from `main`@`6e4fccd` into the audited line (snapshot repo off the data LV; persistent watermark margin); add a sink-failure DLQ/replay path; make the edge spool/quota alert authoritative; add a data-loss drill that asserts "zero dropped events" during a bounded OpenSearch block.
- Suggested validation: bounded drill that blocks OpenSearch writes and asserts (a) no `component_events_dropped` at the sink, (b) DLQ/replay captures failures, (c) `falcon_eve_last_event_age_seconds` returns < 60 s after recovery with no index gap.
- Owner suggestion: ops/owner
- Effort estimate: M (apply existing main changes) + M (DLQ)
- Dependencies: OpenSearch maintenance window; disk layout
- Status: open (incident recovered 2026-10-09; durable controls not in the audited tree)
- Endpoint / data path: probe Vector edge -> `http://vector-aggregator:6000/` (basic auth) -> `falcon-eve-%Y.%m.%d` via `https://opensearch:9200`
- Attack path: none identified (availability/capacity, not adversarial)

### DATA-P1-001 - Wazuh and IRIS retention coverage is incomplete and the repository statement contradicts the live estate

- Severity: P1
- Confidence: High (live `_settings`/policy reads; repo docs)
- Area: DATA
- Evidence:
  - `docs/runbooks/RETENTION_MATRIX.md:19-27` ("none configured (GAP)"; "no ISM policy exists on the Wazuh indexer cluster") and `docs/runbooks/SCHEMA_AND_RETENTION.md:65-67` ("not managed here", DATA-P1-002).
  - `mct/runbooks/index-retention-policy.md:8-13` documents `wazuh-retention` (30d), `wazuh-archives-14d`, `elastiflow` (14d) — contradicting the falcon matrix.
  - Live Wazuh indexer: 5 ISM policies; authoritative `_settings.index.plugins.index_state_management.policy_id` attached for `wazuh-alerts-*` (wazuh-retention) and `security-auditlog-*` (security-auditlog-retention, 180d); `wazuh-monitoring-*`, `wazuh-statistics-*`, `wazuh-states-*`, `elastiflow-flow-*` have no attached policy.
  - Live: `wazuh-alerts` oldest index 2026.09.27 (~13 d) while the attached policy is 30 d (unexplained; possible manual cleanup — unverified); `security-auditlog` oldest 2026.08.31 (~39 d within 180 d); elastiflow-flow 13.5 M docs / 3.8 GB unmanaged.
  - `docs/phase7/runbooks/RESTORE.md:350` IRIS case DB "unbounded | OPEN"; live `iris-web_db_data` volume 80.82 MB, no retention job.
- What is happening: the repo (the falcon audit trail) claims no Wazuh retention exists; the live estate has partial retention; several high-volume classes remain unmanaged, and IRIS case data has no lifecycle.
- Why it matters: capacity planning and owner decisions are made from a statement that is both stale (Wazuh) and incomplete (unmanaged classes); the next capacity incident is harder to predict.
- User / business impact: disk exhaustion risk on the Wazuh estate (the C7/data-LV work already had to absorb it); IRIS case data grows forever.
- Security / privacy / reliability impact: auditlog kept 180 d on the Wazuh cluster vs 30 d centrally — an inconsistent privacy posture; unmanaged elastiflow/flow data grows without an owner.
- Recommended fix: correct `RETENTION_MATRIX.md`/`SCHEMA_AND_RETENTION.md` to the live policy set; attach `wazuh-states-retention` and an elastiflow/rollover policy to the uncovered indices (or record the explicit exception); owner decision on IRIS case-data lifecycle; add a read-only checker that compares live `_settings` policy_id against a declared per-class matrix.
- Suggested validation: the checker fails on a class with no `policy_id`; re-run after attaching.
- Owner suggestion: owner (data lifecycle) + ops
- Effort estimate: S (docs) / M (policies) / L (IRIS decision)
- Dependencies: Wazuh stack maintenance; owner IRIS decision
- Status: partially-fixed (prior ID DATA-P1-001; prior status owner-accepted/still-open)
- Endpoint / data path: Wazuh indexer `https://127.0.0.1:9200/_plugins/_ism/*`; IRIS Postgres volume

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Capacity event -> telemetry data loss | P0 | High (occurred 10-07/10-09) | Blind forensic window | DATA-P0-001 | apply main capacity fix; sink DLQ; drills |
| Wazuh/IRIS unbounded growth | P1 | High | Disk exhaustion | DATA-P1-001 | attach policies; IRIS decision |
| Repo/live retention statement drift | P2 | Certain | Wrong owner decisions | DATA-P1-001 | correct docs + checker |

## Recommendations

### Immediate / Release Blocking
1. DATA-P0-001: land the `6e4fccd` capacity fixes (snapshot repo relocation + watermark margin) in the audited line and add a data-loss drill.

### This Week
2. DATA-P1-001: correct the retention docs and attach the missing Wazuh policies; open the IRIS lifecycle decision.
3. Add sink-failure DLQ/replay (cross-ref WH-P1-001).

### This Month
4. Retention checker comparing live `policy_id` vs a declared matrix.
5. Per-class accelerated delete tests beyond fixtures.

### Later / Platform Evolution
6. Consider a second OpenSearch node or a hardened single-node capacity envelope with pre-emptive reclaim.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Correct retention docs | Stops wrong owner decisions | `RETENTION_MATRIX.md`, `SCHEMA_AND_RETENTION.md` | diff vs live policy list |
| Attach `wazuh-states-retention` | Bounds states indices | Wazuh indexer ISM | `_settings` shows policy_id |
| Document the 10.08 gap in the audit trail | Forensics honesty | decision log / runbook | record present |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Sink-failure DLQ + replay | P1 | ops | M | Vector config change |
| Retention coverage checker | P2 | ops | S | Wazuh creds |
| IRIS case-data lifecycle | P1 | owner | L | owner decision |
| Per-class delete tests | P3 | ops | S | ISM access |

## Suggested Tests

- Bounded write-block drill asserting zero dropped sink events and a DLQ capture.
- Retention checker negative test: an index class without `policy_id` fails.
- Edge spool boundary test: mixed fresh/expired spool files; today's file never removed (already covered by `disk_guard.sh:42-58`, extend for the edge spool).

## Suggested Documentation Updates

- `docs/runbooks/RETENTION_MATRIX.md`: replace the Wazuh/IRIS rows with the live policy set + explicit exceptions.
- `docs/runbooks/SCHEMA_AND_RETENTION.md`: link the Wazuh policy runbook (`mct/runbooks/index-retention-policy.md`).
- Incident record for the 2026-10-08/09 data gap (audited line currently has none).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why is the oldest `wazuh-alerts` index only 13 d under a 30 d policy? | Validates whether deletion is over-firing | Wazuh ISM history / deletion logs |
| What is the owner's IRIS case-data lifecycle? | Bounds the last unmanaged store | Owner decision |
| Was the aggregator restarted manually during recovery? | Explains counter resets | ops notes / decision log |

## Appendix

- Live ISM policy list (central): falcon-auditlog-policy, falcon-eve-policy, falcon-ism-history-policy, falcon-test-cleanup-policy, falcon-topqueries-policy, + stale falcon-retention-exec-20260922055012, mon-eve-policy.
- Live Wazuh policies: wazuh-retention, security-auditlog-retention, wazuh-archives-14d, wazuh-states-retention, elastiflow.
- Audit-time disk: data LV 221G 115G used (55%); root LV 171G 136G used (83%) after the post-audit snapshot relocation.

## Findings

| ID | Severity | Title |
|---|---|---|
| DATA-P0-001 | P0 | 41-hour EVE ingestion outage with confirmed data loss (empty 10.08 index, ~1.74 GB spool purge, non-retriable sink drops); durable capacity fix absent from the audited tree |
| DATA-P1-001 | P1 | Wazuh/IRIS retention coverage is incomplete and the repository statement contradicts the live estate |
