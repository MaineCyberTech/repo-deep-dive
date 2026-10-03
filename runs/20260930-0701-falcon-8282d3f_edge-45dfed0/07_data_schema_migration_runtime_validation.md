# Data, Schema, Migration, and Runtime Validation Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: `/home/user/falcon-build` (central), `/home/user/falcon-edge-build` (edge), live host `falcon`
- Branch/commits: central `main` @ `8282d3f`; edge `main` manifest `45dfed0`, audited HEAD `f1c5def` (`git diff 45dfed0..f1c5def -- src automation/observability` empty)
- Generated at: 2026-09-30T14:05Z · Auditor: audit subagent (read-only; no sudo, Docker, or OpenSearch auth)
- Area code: DATA · Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/07_data_schema_migration_runtime_validation.md`
- Scope limitations: 127.0.0.1:9200 is the Wazuh indexer and returns 401 unauthenticated; central OpenSearch is not host-published; no Docker/root. Index-level facts come from unauth probes, exported metrics, prior-run captures and repo evidence; unobservable items are `unverified`.

## Scope

Reviewed: OpenSearch index template/mappings/guardrails, ISM retention, snapshots/back-ups/restore, migrations, Vector ingest validation and DLQ, edge control-plane SQLite schema and queue, CI static validation, seeds/fixtures. Not reviewed: authenticated OpenSearch/Wazuh APIs, container internals, root-only backup trees, owner-side R2/Spaces buckets, Dashboards UI.

## Evidence Reviewed

- `automation/validation/phase4_data_checks.sh` (template, ISM, fixtures, reader boundary), `retention_execution_test.sh`, `index_rename_migration.sh`, `restore_rehearsal.sh`, `disk_guard.sh`
- `bootstrap/60-central-deploy.sh` (roles, audit REST, watermark, `path.repo`), `bootstrap/80-offsite-backup.sh`, `bootstrap/85-backup-job.sh`, `bootstrap/96-disk-guard.sh`
- `config/vector/aggregator.yaml`, `config/suricata/suricata.yaml`, `compose/central/docker-compose.yml`, `ci/validate.py`
- Evidence `P4-G01` (183 leaf fields), `P4-G03` (retention), `P9-G08` (R2 mount), `REVIEW-FIX/20260929T042028Z` (EVE rotation), `REVIEW-FIX/20260930T035539Z` (offsite fix)
- Edge: `src/falcon_control/store.py`, `src/falcon_agent/queue.py`, `automation/observability/fleet_metrics.py`, `tests/phase3/test_queue.py`, `ci/validate.sh`
- Live: `falcon_metrics.prom` (13:48Z), `falcon_disk_guard.prom` (13:45Z), `df` (13:52Z), read-only SQL on `control-plane.db`, `/opt/wazuh-backups/elasticsearch`, unauth probes 9200/5601/55000
- Prior run `20260930-0320-falcon-794ba31_edge-2b5bc8b` (LIVE-P0-003, LIVE-P2-002, LIVE-P2-003, ND-P2-014, ND-P2-015)

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `curl -sk https://127.0.0.1:9200/` | live | Data-plane boundary | 401; cert `CN=wazuh1.indexer`; central OpenSearch not published |
| `falcon_metrics.prom` 13:48Z | live | Size/growth | 58,458,473 docs; 28,141,120,208 B; cluster yellow; unassigned 33; DLQ 0; backup success 03:34:01Z |
| `df -h` 13:52Z | live | Capacity trend | `/srv/falcon` 71G/46G/61%; root 135G/29G/83% (07:01Z: 70G/47G/60%; root 82%) |
| `disk_guard.prom` 13:45Z | live | Retention helper | free 48,737,333,248 B; `reclaims_total 0` |
| Read-only SQL `control-plane.db` | live | Schema/retention | 15/15 directives unconsumed+expired; audit_log 8,382; tokens 22; events 62; `user_version 0`; no FKs |
| `ls /opt/wazuh-backups/elasticsearch` | live | Wazuh backup | Newest write 2026-09-21T15:17:38Z (`index-482`) |
| `git diff 45dfed0..f1c5def -- src automation/observability` | repo | Prior-finding re-check | empty — queue/directive/export code unchanged |
| `grep bootstrap/*.sh` for template/ISM | repo | Control placement | No `_index_template`/`_plugins/_ism` in deploy path |
| `REVIEW-FIX/20260930T035539Z` evidence | evidence | Backup exercise | exit 0; 1,723 files; 3 SHA-256 read-backs; config round trip; keep 7 |

## Executive Summary

The core store is healthy: 58.46 M docs / 28.1 GB at 13:48Z, ~2 s ingest lag, empty DLQ, ISM 14-day deletion, a mapping-guardrail template, a tested restore path, and a successful backup + offsite run today (exit 0, 07:43Z). Structural risks remain: **schema governance and ISM live in a validation script, not bootstrap**; **retention covers one index class**; **Wazuh indexer data has no scheduled backup** (snapshot repo stale since 2026-09-21); and **two lifecycle helpers are wrong** — `purge_expired()` deletes non-expired queue rows (latent, unwired) and recovery directives are never consumed/purged (live: 15/15 expired; active sensor reports 7 pending). Net growth continues at ~4 GB/day against 46 GB free; `reclaims_total 0`. Carry-over: LIVE-P0-003 partially mitigated but still open (EVE rotation 09-29, threshold 10 GiB 09-30, no warning-band alert); LIVE-P2-002/LIVE-P2-003 still open; ND-P2-014/ND-P2-015 still open at the current edge HEAD. Next actions: move schema/policy to bootstrap; add a Wazuh snapshot job + freshness alert; fix/retire the lifecycle helpers with mixed-state tests; publish one retention matrix and decide cold-copy-before-delete.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| falcon-eve template | `phase4_data_checks.sh:60-101` | Mappings + guardrails | Validation script only | High | Not applied by bootstrap |
| ISM `falcon-eve-policy` | `phase4_data_checks.sh:33-56` | Delete after 14d | Validation script only | High | `ism_template` auto-attach |
| Live `falcon-eve-*` | live metrics | Event store | 58.46 M docs / 28.1 GB | Medium | Yellow single node |
| Snapshot repo `falcon-backup` | `bootstrap/60`, `85` | Local snapshots | Daily success | Medium | Two snapshots/day (80+85) |
| Offsite Spaces copy | `bootstrap/80-offsite-backup.sh` | Cold tier | Success 07:43Z | Medium | No offsite freshness alert |
| Wazuh indexer snapshots | `/opt/wazuh-backups/elasticsearch` | Wazuh backup | Stale since 09-21 | High | No host timer found |
| Control DB schema | `store.py:13-111` | Edge state | No versioning/FKs | Medium | 12 tables |
| Agent queue | `queue.py:113-138` | Offline buffer | `purge_expired` over-deletes | High | Unwired but latent |
| Vector validation/DLQ | `aggregator.yaml:39-111` | Ingest safety | site/sensor only; DLQ files | Medium | No expiry/alert |
| CI validation / fixtures | `ci/validate.py`, edge `ci/validate.sh`, `phase4_data_checks.sh` | Static checks; test data | Parse/pins/ledger/secrets; fixtures left in place | Medium | No schema/drift check; no cleanup |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Database schema | 3 | Template + edge store | Template only in script; no versioning | Move to bootstrap; add schema version |
| Migrations | 3 | Rename + Wazuh bundle | Manual count gate; no rollback | Automate verification |
| Constraints | 2 | API validation; field limits | No FK/unique; dynamic mapping open | Add FKs; `dynamic: strict` where safe |
| Indexes | 3 | 1 shard/0 replica; ISM; snapshots | Mapping drift; replicas 0 | Drift checks; document single-node |
| Foreign keys/cascades | 1 | None declared | Orphans possible | Add FKs + `foreign_keys=ON` |
| RLS | 2 | Role ACLs; reader boundary test | No row/site filters | Site-scoped roles if multi-site |
| Tenant columns | 3 | `site_id`/`sensor_id` required at ingest | Not mapped strictly | Keyword mappings |
| Soft deletes | 1 | `consumed_at`/`redeemed_at` flags | No purge/delete policy | Purge jobs |
| Audit fields | 3 | `created_at`/`audit_log` | Unbounded | Retention policy |
| Retention | 2 | ISM 14d; Prom 30d; ntfy 48h | One class; snapshots outlive delete | Retention matrix + cold copy |
| Seeds/fixtures | 3 | phase4 fixtures | Not cleaned | Cleanup step |
| Generated DB types | 2 | Edge OpenAPI model checks | No central schema snapshot | Schema snapshot CI |

## Detailed Review

- **OpenSearch schema controls:** `phase4_data_checks.sh:33-101` creates the `falcon-eve` template (`timestamp` date; `event_type`/`site_id`/`sensor_id` keyword; `src_ip`/`dest_ip` ip; 500-field/100-char limits; ISM `policy_id`) and the 14d policy, but only when the validation script runs; `grep` finds no `_index_template` in `bootstrap/`; no drift check; dynamic mapping open to the writer role — DATA-P1-001.
- **Snapshots/offsite/restore:** `bootstrap/80`, `bootstrap/85`, `restore_rehearsal.sh`, P6-G09, `REVIEW-FIX/20260930T035539Z` — daily local snapshot (`indices:"falcon-*"`), encrypted config archive, Spaces upload with SHA-256 read-back, remote keep-7, two snapshots/day; no offsite success metric/alert (only "Backup stale" ≥36 h, `bootstrap/90-alerting.sh:223`).
- **Wazuh indexer data:** snapshot repo newest write 2026-09-21T15:17Z; `backup_new_services.sh` covers config/registry only; no Wazuh timer/cron; `WAZUH_INTEGRATION.md` (stack under `/opt/wazuh-docker`, path only); `.security`, `wazuh-alerts-*`, dashboard state unbacked — DATA-P1-002.
- **Edge control DB/queue/runtime validation:** `store.py:13-111`, `queue.py:126-138`, live DB counts, `fleet_metrics.py:61-64`, `aggregator.yaml:42-49,106-111` — no migrations/FKs/retention; `purge_expired` deletes fresh rows; the pending-directive metric counts expired rows; inbound validation is shallow; DLQ unmanaged — DATA-P1-003/004/005.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DATA-001 | Database schema | template/script | PUT + validation | Not in bootstrap | P1 | Move to bootstrap |
| DATA-002 | Migrations | `index_rename_migration.sh` | Reindex + printed counts | No abort/rollback | P3 | Automate gate |
| DATA-003 | Constraints | Vector/OS limits | 500-field cap | No strict/FK | P2 | Tighten where safe |
| DATA-004 | Indexes | live metrics | 1/0 shards, ISM | Drift unchecked | P2 | Drift check |
| DATA-005 | FKs/cascades | `store.py` | None | Orphans possible | P3 | Add FKs |
| DATA-006 | RLS | roles + phase4 test | Index-pattern ACL | No row filters | P3 | Revisit if multi-site |
| DATA-007 | Tenant columns | `aggregator.yaml` | Required at ingest | Not mapped strictly | P2 | Keyword mapping |
| DATA-008 | Soft deletes | `consumed_at` | Flags only | No purge | P2 | Purge jobs |
| DATA-009 | Audit fields | `audit_log` | Present | Unbounded | P2 | Retention |
| DATA-010 | Retention | ISM/Prom/ntfy | falcon-eve 14d | One class; cold copies | P2 | Retention matrix |
| DATA-011 | Seeds/fixtures | phase4 script | Fixtures | Leftovers | P3 | Cleanup step |
| DATA-012 | Generated DB types | edge `generate_models` | CI checks | No central snapshot | P2 | Snapshot check |

## Findings
### Finding ID: DATA-P1-001 - Schema and retention controls exist only in validation scripts, not in deployment

- Severity: P1 · Confidence: High · Area: DATA · Status: open
- Evidence: `automation/validation/phase4_data_checks.sh:33-101`; `bootstrap/60-central-deploy.sh` has no `_index_template`/`_plugins/_ism` calls; `grep` confirms the deploy path is silent
- What is happening: the `falcon-eve` template (mappings, 500-field guardrail, ISM `policy_id`) and `falcon-eve-policy` are created by a phase-4 script, not by any deploy/bootstrap step.
- Why it matters: a clean-host rebuild or config reset leaves dynamically mapped indices with no retention; disk growth and unschedulable fields follow.
- User / business impact: retention claims become untrue; rebuild not reproducible. · Security / privacy / reliability impact: telemetry over-retention; mapping-explosion risk.
- Recommended fix: add `bootstrap/61-opensearch-schema.sh` (idempotent template + policy + attach), call from `60-central-deploy.sh`/`run-all.sh`; keep phase4 as verification.
- Suggested validation: scratch deploy asserts template/policy exist and a new index inherits the `policy_id`; over-long field rejected.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: none
- Status: open
### Finding ID: DATA-P1-002 - Wazuh indexer data has no scheduled backup; repository stale since 2026-09-21

- Severity: P1 · Confidence: Medium-High (owner-side jobs not visible) · Area: DATA · Status: open
- Evidence: `/opt/wazuh-backups/elasticsearch/index-482` + `index.latest` mtime 2026-09-21T15:17:38Z; `automation/wazuh/migration/docker-compose.lab.yml` mounts it on all three indexers; `backup_new_services.sh:1-8` claims separate coverage; `bootstrap/85-backup-job.sh:19` snapshots `falcon-*` only; no Wazuh timer/cron found
- What is happening: the VM 101 snapshot schedule appears not to have been migrated; the mount is retained but writes nothing.
- Why it matters: `.security` (users/roles), `wazuh-alerts-*`, `wazuh-states-*` and dashboard state are unrecoverable on host loss; reported coverage contradicts the snapshot filter.
- User / business impact: loss of alert/forensic history and identity config. · Security / privacy / reliability impact: restore/DR claims overstated.
- Recommended fix: lab-side snapshots against 127.0.0.1:9200 (credentials in `/opt/wazuh-docker/multi-node/.env`, path only) + offsite copy + freshness metric/alert; or document an owner-accepted gap.
- Suggested validation: create + verify a snapshot, restore one index to scratch, assert the freshness metric moves.
- Owner suggestion: falcon maintainer + owner · Effort: M · Dependencies: Wazuh credentials access
- Status: open
### Finding ID: DATA-P1-003 - `purge_expired()` deletes non-expired queue items (latent data loss)

- Severity: P1 · Confidence: High · Area: DATA · Status: still-open (ND-P2-014)
- Evidence: `src/falcon_agent/queue.py:126-138` — count uses `enqueued_at < now - max_age` but `DELETE` uses `cutoff = iso_now()`; `tests/phase3/test_queue.py:73-85` tests only the all-expired case; no caller found (`grep -rn purge_expired src/`)
- What is happening: if wired, the helper deletes the whole queue instead of the expired slice; the test cannot detect it because every row is expired.
- Why it matters: the queue is the sensor's loss-accounted buffer; mass deletion silently drops fresh security events.
- User / business impact: missed detections after offline periods. · Security / privacy / reliability impact: telemetry data loss.
- Recommended fix: reuse the computed cutoff in both statements; add a mixed fresh/expired test; wire the helper into the runner or delete it and document `max_age_seconds` eviction as the only age path.
- Suggested validation: enqueue 1 fresh + 2 expired; assert only 2 purged and the fresh item remains readable.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none
- Status: still-open — code unchanged at `f1c5def`
### Finding ID: DATA-P2-004 - Directives never consumed/purged; control DB lacks migrations, FKs and retention

- Severity: P2 · Confidence: High · Area: DATA · Status: still-open (ND-P2-015)
- Evidence: `store.py:13-111` (`CREATE TABLE IF NOT EXISTS` only; live `user_version 0`), `store.py:316-327`, `service.py:657` (serves, never marks consumed), `fleet_metrics.py:61-62` (counts `consumed_at IS NULL` without expiry); live: 15/15 directives unconsumed+expired, tokens 22, audit_log 8,382, idempotency 1,189, no DELETE/prune statements
- What is happening: expired directives remain and are reported as pending forever (active sensor metric = 7); schema evolves by editing `SCHEMA`; expired tokens and logs accumulate.
- Why it matters: operators cannot trust the recovery metric; future schema changes silently miss existing DBs; unbounded growth.
- User / business impact: misleading operations signal; manual DB surgery risk. · Security / privacy / reliability impact: stale tokens; unversioned state.
- Recommended fix: expiry-aware metric + prune job; `consume_directive` ack path or documented fire-and-forget; `user_version` migrations; FKs with `foreign_keys=ON`; retention jobs.
- Suggested validation: TTL test returns metric to 0 and prunes the row; v0→v1 migration test on a copied DB; FK violation rejected.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: none
- Status: still-open — code unchanged at `f1c5def`
### Finding ID: DATA-P2-005 - Retention covers one class; deletion outruns recoverability; DLQ/fixtures unmanaged

- Severity: P2 · Confidence: High (repo/prior live); Wazuh ISM `unverified` · Area: DATA · Status: still-open (LIVE-P2-002)
- Evidence: `phase4_data_checks.sh:33-56` (falcon-eve only); `bootstrap/60:204-215` (audit REST, no retention); `aggregator.yaml:106-111` (DLQ, no expiry); `bootstrap/80:139` keep 7; `disk_guard.sh:15` keep 3; prior LIVE-P2-002 (11 `security-auditlog-*`, `top_queries-*`, ISM history, fixtures); `mct/runbooks/index-retention-policy.md` (Wazuh ISM docs, live `unverified`)
- What is happening: after ISM deletes at 14d, snapshots cover only ~7 more days and the R2 searchable mount for 09.21 persists; audit/query/DLQ stores grow forever; fixtures remain.
- Why it matters: forensic data older than ~3 weeks is lost while audit/query data is kept too long; disk pressure is the backstop (`reclaims_total 0`).
- User / business impact: irreversible investigation-data loss; compliance/disk risk. · Security / privacy / reliability impact: over-retention of logs/query text (cross-ref SEARCH-P2-003); under-retention of forensics.
- Recommended fix: one retention matrix (class, store, window, owner); ISM for audit/query/ISM-history; DLQ age quota; cold-copy or explicitly accept the deletion window; define snapshot/mount deletion coverage.
- Suggested validation: per-class accelerated delete test; restore drill proving the documented window; DLQ age-out test.
- Owner suggestion: falcon maintainer + owner · Effort: M · Dependencies: retention/OD-14 decision
- Status: still-open
### Finding ID: DATA-P2-006 - Mapping drift breaks keyword aggregations/sorts silently; dynamic mapping open to writers

- Severity: P2 · Confidence: Medium (live mappings unverified) · Area: DATA · Status: still-open (LIVE-P2-003)
- Evidence: prior LIVE-P2-003 (`event_type` keyword since 09.23, text(+keyword) on 09.21/09.22; `host` text-only on 09.29/09.30); `phase4_data_checks.sh:68-90` (intended mapping); `bootstrap/60:113-116` grants writer `indices:admin/mapping/put`; `P4-G01` (183 leaf fields; 8 rejections near the 500 cap)
- What is happening: historical and new indices disagree on field types; `.keyword` aggregations silently return nothing rather than erroring.
- Why it matters: dashboards/saved searches can under-report with no failure signal; repairs need reindexing.
- User / business impact: wrong triage conclusions. · Security / privacy / reliability impact: search correctness/visibility.
- Recommended fix: repair mappings (reindex or runtime fields), ensure `host.keyword`/`event_type.keyword`, add a mapping-drift check per new index, narrow dynamic mapping where safe.
- Suggested validation: per-day assertion that `event_type.keyword`/`host.keyword` aggregations are non-zero; drift check fails on type mismatch.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: reindex window
- Status: still-open
### Finding ID: DATA-P3-007 - Fixture indices and migration-safety gaps remain

- Severity: P3 · Confidence: High (repo; prior live) · Area: DATA · Status: still-open (part of LIVE-P2-002)
- Evidence: `phase4_data_checks.sh:148-171` creates `falcon-canary`, `falcon-eve-fixture-test`, `other-site-index`; prior LIVE-P2-002 lists `falcon-test` and a retention-test index; `index_rename_migration.sh:40-53` deletes `mon-*` after only printing counts; `/home/user/falcon-edge-secrets/control.db` is 0 bytes
- What is happening: test artifacts persist in the cluster; the rename migration has no automated count gate or rollback.
- Why it matters: search noise/confusion; a partial reindex rerun could delete a source index.
- User / business impact: minor operational confusion; low-probability migration data loss. · Security / privacy / reliability impact: low.
- Recommended fix: cleanup traps in validation scripts; remove the stray DB; add a `_count` equality gate that aborts before deletion and document rollback.
- Suggested validation: re-run phase4 and assert cleaned indices; simulate a short destination count and assert non-zero exit without deletion.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: still-open / open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Clean rebuild loses mappings/retention | P1 | Medium | Data growth, unmapped indices | no template in bootstrap | DATA-P1-001 |
| Wazuh indexer data loss | P1 | Low-Medium | Loss of `.security`/alerts | snapshot stale 09-21 | DATA-P1-002 |
| Queue over-deletion | P1 | Low (unwired) | Missed security events | `queue.py:126-138` | DATA-P1-003 |
| Retention/lifecycle gaps (audit/DLQ/fixture growth; deletion outruns recoverability) | P2 | High | Disk/compliance; forensic loss | no policies; keep 7/3 | DATA-P2-005 |
| Mapping drift gives silent wrong results | P2 | Medium | Triage errors | LIVE-P2-003 | DATA-P2-006 |
| Directives metric misleading | P2 | High | Bad recovery decisions | live 15/15 expired | DATA-P2-004 |

## Recommendations

### Immediate / Release Blocking
1. Fix `purge_expired()` + mixed-state test before it is ever wired (DATA-P1-003). 2. Add the Wazuh indexer snapshot job/alert or owner-document the accepted gap (DATA-P1-002).

### This Week
3. Move template + ISM into bootstrap (DATA-P1-001). 4. Expiry-aware directive metric + control DB retention (DATA-P2-004). 5. Publish the retention matrix and audit/query/DLQ policies (DATA-P2-005).

### This Month
6. Control DB migrations/FKs (DATA-P2-004); mapping repair + drift check (DATA-P2-006); cold-copy decision (DATA-P2-005).

### Later / Platform Evolution
7. Schema snapshot CI, migration framework, per-class deletion drills, fixture cleanup (DATA-P3-007).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix the queue cutoff line | Removes latent data loss | `src/falcon_agent/queue.py` | mixed-state unit test |
| Expiry-aware directive count | Honest operator metric | `automation/observability/fleet_metrics.py` | metric 0 after TTL |
| Delete stray `control.db` | Hygiene | `/home/user/falcon-edge-secrets/` | `ls` |
| ISM template for `security-auditlog-*` | Bounds audit growth | bootstrap/ISM script | accelerated delete test |
| Offsite freshness metric/alert | Silent-failure detection | `bootstrap/90-alerting.sh` | kill offsite run; alert fires |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Bootstrap schema apply | P1 | falcon maintainer | M | none |
| Wazuh snapshot job + alert | P1 | falcon maintainer | M | credentials |
| Control DB migrations/retention | P2 | edge maintainer | M | none |
| Mapping drift checker | P2 | falcon maintainer | M | reindex window |
| Retention matrix + cold copy | P2 | falcon maintainer | M/L | owner decision |
| Schema snapshot CI | P2 | falcon maintainer | S | none |

## Suggested Tests

- Unit: `purge_expired` mixed fresh/expired; directive TTL metric; `_evict` age boundary.
- Integration: scratch deploy asserts template/policy/attach; accelerated ISM deletion per class; Wazuh snapshot create + restore.
- CI: mapping-drift check per daily index; schema `user_version` migration test; rename-script abort test.
- Security/privacy: DLQ age-out; reader-role boundary re-run with fixture cleanup.
- Manual: quarterly Wazuh restore drill; disk-guard threshold walk (10→5 GiB) with reclaim counter.

## Suggested Documentation Updates

- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: retention matrix, cold-copy decision, snapshot window.
- `docs/runbooks/RESTORE.md`: Wazuh indexer restore; scope of `falcon-backup` vs new-services backup.
- New `docs/runbooks/SCHEMA_AND_RETENTION.md`: templates, ISM, drift checks, ownership.
- `docs/runbooks/OPERATOR_START_HERE.md`: pointer to the retention matrix.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is any owner-side job snapshotting the Wazuh indexer? | P1 vs accepted risk | owner confirmation/job config |
| Are Wazuh ISM policies live on the migrated cluster? | Retention correctness | authenticated `_plugins/_ism/explain` |
| Is R2/Spaces content covered by any lifecycle rule? | Deletion/compliance | owner-side policy |

## Appendix

Live 2026-09-30: metrics 13:48Z — 58,458,473 docs / 28,141,120,208 B; cluster yellow; unassigned 33; DLQ 0; eve age 2 s; backup success 03:34:01Z. `df` 13:52Z — `/srv/falcon` 71G/46G (61%); `/` 135G/29G (83%). Unauth `https://127.0.0.1:9200` → 401 (`CN=wazuh1.indexer`). Edge DB: directives 15/15/15, tokens 22, audit_log 8,382, idempotency 1,189, events 62, state_reports 19, sensors 9, `user_version` 0. Prior-run carry-over: LIVE-P0-003 partially mitigated (rotation fix; 10 GiB threshold; `reclaims_total 0`); LIVE-P2-002, LIVE-P2-003, ND-P2-014, ND-P2-015 still open.
