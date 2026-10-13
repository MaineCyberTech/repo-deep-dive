# 31_search_indexing_privacy_audit — Prompt 31 - Search, Indexing, and Privacy Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `31_search_indexing_privacy_audit.md` (area SEARCH, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon
- Branch: main (origin/main)
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:45:00Z
- Auditor: repo-deep-dive full-domain subagent (read-only; live lab host vantage)
- Area code: SEARCH
- Live vantage: this audit ran on the live lab host; live tree `/home/user/falcon-build` == `f5cb7c9` (clean). All OpenSearch/Wazuh observations are read-only live cluster reads; repo files (config/opensearch/*, bootstrap/61, retention docs) are identical to the live deployed artifacts for this domain.

## Scope

Reviewed: central OpenSearch 2.19 single node index classes, the composable template and five repo-managed ISM policies (`config/opensearch/`, `bootstrap/61-search-policies.sh`), retention execution and observability (`automation/validation/ism_retention_metrics.sh`, `mapping_drift_check.py`, `consumer_query_check.sh`), the **snapshot repository location and its retention** (`bootstrap/85-backup-job.sh`, `80-offsite-backup.sh`, `automation/validation/disk_guard.sh`, live `path.repo`/bind mounts), the Wazuh 3-node indexer estate, the IRIS case store, deletion scope (cluster vs snapshots vs Spaces vs R2 cold copies), search authorization/audit (internal users/roles, audit config), OpenSearch Dashboards exposure, and the retention documentation (`docs/runbooks/RETENTION_MATRIX.md`, `SCHEMA_AND_RETENTION.md`, `CAPACITY_AND_TELEMETRY.md`).

Not reviewed: query/analytics inside third-party OpenSearch Dashboards beyond its data scope; the R2 bucket lifecycle (owner-side, not in the repo); Wazuh indexer ISM policy sources (owner-side, not in the repo); IRIS application search internals (third-party code, not in the repo).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/opensearch/falcon-eve-template.json`, `bootstrap/61-search-policies.sh` | config/deploy | pinned template (`dynamic:false`, 75 top-level props) + 5 ISM classes | live policies match, all with `ism_template` |
| `config/opensearch/*-ism-policy.json` | config | falcon-eve 14d, auditlog 30d, topqueries 14d, ism-history 30d, test-cleanup 1d | live: 5 managed + 2 documented stale (`falcon-retention-exec-*`, `mon-eve-policy`) |
| `docs/runbooks/RETENTION_MATRIX.md`, `SCHEMA_AND_RETENTION.md`, `CAPACITY_AND_TELEMETRY.md` | docs | per-class retention statement, deletion scope, snapshot relocation record | Wazuh statement stale; snapshot keep-count stale; relocation documented |
| `automation/validation/ism_retention_metrics.sh` + live `falcon_retention.prom` | metrics | deletion accounting | live: 1 falcon-eve delete/24h; last delete 2026-10-11T00:05:16Z |
| `automation/validation/mapping_drift_check.py` + live `falcon_mapping_drift.prom` | validation | mapping drift/silent-empty detection | current 0; legacy drift on 3 indices |
| `bootstrap/85-backup-job.sh:50-76`, `80-offsite-backup.sh:55-67` | backup | local snapshot create/retention + offsite delta (real repo path after #51) | keep newest 3 local snapshots; offsite state = `/var/lib/falcon-snapshots/opensearch` |
| `automation/validation/disk_guard.sh:22-24,110-160` | capacity | watches `/srv/falcon` (10 GiB) and `/` (20 GiB); reclaims snapshots >3 | live: root below threshold; guard exits 1 after alerting |
| live central cluster (`_cat/indices`, `_plugins/_ism/*`, `_snapshot/*`, `_cluster/settings`, security APIs) | live | current retention/mapping/authz/audit truth | read-only via docker exec |
| live Wazuh indexer (`_plugins/_ism/policies`, `_plugins/_ism/explain/*`, `_cat/indices`) | live | Wazuh retention truth | alerts class unmanaged |
| `compose/mct/iris-web/*` + live IRIS volumes | deploy/live | case-file store scope | digest-pinned; no retention; volumes 4K/20K/78M/4K |
| `automation/validation/r2_cold_copy.sh` + `falcon-r2` repo | cold tier | pre-delete cold copies | 8 cold snapshots; last copy 2026-10-10 (09.28) |
| live Cloudflare DNS/Access + public probes | live | Dashboards/IRIS exposure | `/dash` 302 -> Cloudflare Access; IRIS app has owner-IP bypass |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Central ISM policies | `GET /_plugins/_ism/policies` | 5 managed (`falcon-eve-policy`, `falcon-auditlog-policy`, `falcon-topqueries-policy`, `falcon-ism-history-policy`, `falcon-test-cleanup-policy`), all with `ism_template`; + 2 stale documented |
| Retention working (EVE) | `_cat/indices`; `falcon_retention.prom` | oldest `falcon-eve-2026.09.28` (14d window); 1 delete/24h; last delete 2026-10-11T00:05:16Z; metric ok=1 |
| Retention working (auditlog/top_queries/ISM history) | `_cat/indices` | security-auditlog oldest 2026.09.20 (30d); top_queries 7 indices (14d); ISM history hidden indices 30d |
| Template pinned | `GET /_index_template/falcon-eve` | `dynamic:false`, 75 top-level properties, pattern `falcon-eve-*`, priority 100 |
| Mapping drift | `falcon_mapping_drift.prom` | current 0; legacy `dest_ip`=3, `event_time`=3, `alert.severity`=3, `alert.category`=3 of 14 indices |
| **Snapshot repo location** | live `path.repo`, container binds, `readlink` | `path.repo: ["/srv/falcon/backups/opensearch"]`; host symlink -> `/var/lib/falcon-snapshots/opensearch`; container bind `Source=/var/lib/falcon-snapshots/opensearch -> /srv/falcon/backups/opensearch`; repo size **69 GB** on the root LV |
| Snapshot inventory | `_snapshot/falcon-backup/_all` | 3 SUCCESS snapshots (10-09, 10-10, 10-11); retention keeps newest 3 (`85-backup-job.sh:72`) |
| **Root LV state** | `df -h`; disk-guard journal; `falcon_disk_guard.prom` | root 171G/144G used/**20G avail (88%)**; `root_free=20693304KB` < threshold `20971520KB`; guard `BELOW THRESHOLD` -> `still below threshold after reclaim - alert sent` -> exit 1 at 03:45/04:00/04:15; 47 root alerts since 2026-10-10 10:00 |
| Root reclaim candidates | `du -x` | `/var/tmp/wz-migration/wazuh-stack.tar` 22 GB (2026-09-27); `/var/lib/containerd` 22 GB; `/var/lib/falcon-snapshots` 69 GB |
| Offsite backup | `85/80` journal + `offsite.log` + stamps | Oct 11 run still uploading at 04:28 (1981 files, upload state reset after the Oct 10 failure); `.offsite-last-success` = 2026-10-09T19:01:37Z; local `.last_backup_epoch` = 2026-10-11T03:37:41Z |
| Wazuh indexer policies | `GET /_plugins/_ism/policies` (admin) | 5 policies: `security-auditlog-retention` (template), `elastiflow`, `wazuh-retention`, `wazuh-archives-14d`, `wazuh-states-retention` - only the first has an `ism_template` |
| Wazuh alerts class | `_plugins/_ism/explain/wazuh-alerts-4.x-*` | `policy_id: null` on all 15 indices (oldest 2026.09.27); class ~430 MB; cluster total 7.1 GB / 87 indices |
| Wazuh monitoring/statistics | explain | `policy_id: null` (unmanaged); states-* managed |
| IRIS store | live volumes | downloads 4.0K / server_data 20K / db_data 78M / user_templates 4.0K; no retention mechanism |
| Search authorization | live `falcon_reader` role + `falcon-dashboard` user | read/search only on `falcon-*` (+ aliases-get on `*`); `top_queries-*`/`security-auditlog-*` not readable by the dashboard user |
| Audit logging | `GET /_plugins/_security/api/audit` | enabled, compliance enabled, `log_request_body: true`, REST+transport enabled |
| Dashboards exposure | `curl https://falcon.mainecybertech.us/dash` | 302 to Cloudflare Access login (gated); internal `dash.falcon.lab` route has no Traefik auth (internal-only) |
| Deleted-data removal | `_cat/indices`; `_snapshot/*` | no searchable mounts remain (`falcon-eve-2026.09.21-searchable` gone); ISM deletes cluster copy only; snapshots (3), Spaces (7 inventories), R2 (8 cold snapshots) keep their own windows |
| Watermarks | `_cluster/settings?include_defaults` | persistent/transient empty; defaults 85/90/95 with single-node enable (register DR-P2-001 confirmed) |
| R2 cold copy | `falcon-r2` repo + journal | 8 `cold-*` snapshots; last success 2026-10-10T04:52:25Z (09.28); next eligible 09.29 at 04:40Z 10-11 |

## Executive Summary

The central search stack remains substantially hardened: five ISM classes are live with templates (EVE 14d, security auditlog 30d, top queries 14d, ISM history 30d, test cleanup 1d), deletions are measured and alertable (last EVE delete 2026-10-11T00:05:16Z), the template pins mappings with `dynamic:false`, dashboard access is read-only on `falcon-*`, audit logging captures request bodies, the public dashboards route is Access-gated, watermarks are back to defaults, and the R2 cold-copy tier is running daily. Three gaps remain. **P2 (prior SEARCH-P2-001):** the Wazuh `wazuh-alerts-4.x-*` class (15 indices, oldest 2026-09.27) still has **no ISM policy and no template**, the Wazuh monitoring/statistics classes are unmanaged, IRIS has no retention, and `RETENTION_MATRIX.md` is stale (it says the Wazuh indexer has no ISM policies at all; it also says local snapshots keep 7 while the script keeps 3). **P2 (new):** the OpenSearch snapshot repository (69 GB, keep-3) still lives on the **root LV**; root free is below the disk guard's 20 GiB threshold (19.74 GiB) and the guard now fails every 15 minutes (47 alerts since 2026-10-10 10:00), with 22 GB of stale `/var/tmp/wz-migration` and 22 GB of containerd data as obvious reclaim candidates; the nightly snapshot (~5 GB) crosses the threshold each night. **P3 (prior SEARCH-P3-001):** the legacy `falcon-eve` 09.2x-09.30 indices keep divergent mappings, so consumer queries over that window silently under-return.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Template | `config/opensearch/falcon-eve-template.json` | pin EVE mappings | live, `dynamic:false`, 75 props | low | legacy indices not repaired |
| ISM classes (central) | `config/opensearch/*-ism-policy.json` | retention | 5 live with templates | low | 2 stale policies match nothing |
| Deletion metrics | `automation/validation/ism_retention_metrics.sh` | observability | live, ok=1 | low | last EVE delete 10-11 00:05Z |
| Drift metrics | `mapping_drift_check.py` | silent-empty guard | live | medium (legacy) | 3 legacy indices drift |
| Snapshot repo | `/var/lib/falcon-snapshots/opensearch` (bind) | local backups | 69 GB on root LV; keep 3 | **high (capacity)** | root below guard threshold; guard failing |
| Snapshot job | `bootstrap/85-backup-job.sh` | nightly snapshot | Oct 11 SUCCESS 03:37Z; prunes keep-3 | low | offsite still uploading |
| Offsite uploader | `bootstrap/80-offsite-backup.sh` | Spaces delta + verify | Oct 11 run in progress (1981 files) | medium | upload state reset; stamp 10-09 |
| Cold copy | `automation/validation/r2_cold_copy.sh` | R2 pre-delete copy | 8 cold snapshots; last 10-10 | low | lifecycle owner-side |
| Wazuh indexer | `/opt/wazuh-docker/multi-node` | SOC store | 5 policies; alerts unmanaged | **medium** | see SEARCH-P2-001 |
| IRIS store | `compose/mct/iris-web/` | case store | no retention | medium | documented gap |
| Dashboards authz | `falcon_reader` role | search UI scope | read/search `falcon-*` only | low | admin-only analytics |
| Audit log | OpenSearch security audit | search audit trail | enabled + request bodies | low | admin-only index |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Search routes/UI | 4 | Dashboards internal + Access-gated public /dash | none | none |
| Indexes | 4 | 5 ISM classes, template pinned | 2 stale policies | retire stale policies |
| Indexing jobs | 4 | edge/central vector pipelines; ISM delete history | none | none |
| Indexed fields | 4 | template dynamic:false, 75 props | legacy window drift | reindex/runtime fields (SEARCH-P3-001) |
| Tenant filters | N/A | single-tenant lab | none | none |
| Permission filters | 4 | falcon_reader falcon-* only; admin-only analytics | none | none |
| Document/ticket/project/message search | N/A | no first-party app search | none | none |
| Admin/global search | 4 | Dashboards; Wazuh dashboard internal | none | none |
| Autocomplete | N/A | no first-party autocomplete | none | none |
| Search logs | 4 | top_queries 14d, admin-only | none | none |
| Query analytics | 4 | top_queries full bodies, 14d | none | none |
| Deleted data removal | 3 | cluster delete + snapshots/cold tiers | Wazuh alerts + IRIS unmanaged | SEARCH-P2-001 |

## Findings

### SEARCH-P2-001 (prior) - Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale

- Severity: P2, Confidence: High (live clusters + repo), Status: still-open
- What is happening: central classes are covered, but on the Wazuh 3-node indexer the primary `wazuh-alerts-4.x-*` class (15 indices, oldest 2026-09.27, ~430 MB, fastest-growing SOC dataset) has `policy_id: null` and no `ism_template`; `wazuh-monitoring-*`/`wazuh-statistics-*` are also unmanaged; of the five Wazuh policies only `security-auditlog-retention` carries a template (`wazuh-retention`, `wazuh-archives-14d`, `wazuh-states-retention` do not, so new indices do not inherit them). IRIS case data has no retention at all (documented owner gap). `docs/runbooks/RETENTION_MATRIX.md:23` still states "no ISM policy exists on the Wazuh indexer cluster", which is stale; `:39` says local snapshots keep 7 while `bootstrap/85-backup-job.sh:72` keeps 3.
- Why it matters: unbounded alert-class growth is a capacity/retention-compliance risk on the consolidated SOC host, and the stale matrix misstates the live estate for operators and reviewers.
- Recommended fix: attach a template-backed ISM policy to `wazuh-alerts-4.x-*` (owner-gated), add templates to the existing Wazuh policies or retire them, decide the IRIS retention window, and refresh `RETENTION_MATRIX.md` to the live policy inventory + the keep-3 snapshot policy.
- Evidence: live `_plugins/_ism/explain/wazuh-alerts-4.x-*` (all null); `_plugins/_ism/policies` (5, one template); `docs/runbooks/RETENTION_MATRIX.md:23,39`; `bootstrap/85-backup-job.sh:68-76`; live IRIS volumes.

### SEARCH-P2-002 (new) - OpenSearch snapshot repository still on the root LV; root free is below the guard threshold and the guard now fails every 15 minutes

- Severity: P2, Confidence: High (live mounts, guard journal, metrics), Status: open (supersedes the register's PERF-P1-002 verified-fixed note - see comparison)
- What is happening: the snapshot repository (69 GB, keep-newest-3) is bound into the OpenSearch container from `/var/lib/falcon-snapshots/opensearch` on the **root LV** (container path `/srv/falcon/backups/opensearch`; `path.repo` unchanged). Root free is 19.74 GiB against the disk guard's 20 GiB threshold (`disk_guard.sh:24`), so every 15-minute run logs `BELOW THRESHOLD`, cannot reclaim (only 3 snapshots exist; config archives already pruned), alerts `Falcon disk guard: root still below threshold`, and exits 1. The guard has fired that alert 47 times since 2026-10-10 10:00 (segments 10-10 10:00-13:00, 10-10 16:15-23:45, 10-11 03:45-ongoing). The 2026-10-11 02:24 reboot temporarily raised root free to 27.4 GiB, but the 03:30 nightly snapshot (~5 GB) pushed it back to 19.76 GiB by 03:45. Obvious reclaim candidates are not touched by the guard: `/var/tmp/wz-migration/wazuh-stack.tar` 22 GB (stale, 2026-09-27) and `/var/lib/containerd` 22 GB. Root is 88% used (144G/171G); the data LV is healthy (96G free). The Oct 11 offsite run is still uploading (1981 files; `.offsite-last-success` = 2026-10-09T19:01:37Z).
- Why it matters: this is the capacity root cause behind the top notification-noise source (NOTIF-P2-002); if root fills, local snapshot creation fails and the host itself (docker/logs) degrades. The guard's purpose is defeated: it detects the condition but cannot reclaim it and now permanently reports failed.
- Recommended fix: reclaim the stale `/var/tmp/wz-migration` tar and review containerd image/volume usage; then either (a) move the snapshot repo back to the data LV with headroom (the data LV is at 55%), (b) lower the snapshot keep to 2, (c) raise root capacity, or (d) re-tune the guard threshold to the nightly swing (~5 GB) while adding root-side retention; add a root-LV-specific reclaim path and stop the guard from exit-failing on a condition it cannot fix.
- Evidence: `docker inspect falcon-central-opensearch-1` mounts (`/var/lib/falcon-snapshots/opensearch -> /srv/falcon/backups/opensearch`); `compose/central/docker-compose.yml:78`; `bootstrap/60-central-deploy.sh:248-254`; `automation/validation/disk_guard.sh:22-24,115-118,152-155`; guard journal 03:45/04:00/04:15 (`root_free=20693304KB < 20971520KB`, exit 1); `falcon_disk_guard.prom`; `df -h`; `du -x`; 48h topic export (47 alerts); `offsite.log` + stamps.

### SEARCH-P3-001 (prior) - Legacy falcon-eve indices keep divergent mappings; consumer queries silently under-return

- Severity: P3, Confidence: High (live mappings/metrics), Status: still-open (owner-gated reindex)
- What is happening: `falcon_mapping_drift.prom` reports legacy drift on 3 of 14 falcon-eve indices (`dest_ip`, `event_time`, `alert.severity`, `alert.category`), while current indices are clean (0). The template only applies to new indices; pre-2026.10.01 indices keep older mappings (e.g. `dest_ip` as text, no `event_time`).
- Why it matters: range/term queries over the legacy window return silently empty/partial results, which reads as healthy zeros.
- Recommended fix: schedule the owner-gated reindex or runtime-field repair; keep the legacy window labelled; the drift metric already quantifies it.
- Evidence: `falcon_mapping_drift.prom`; `mapping_drift_check.py`; `docs/runbooks/SCHEMA_AND_RETENTION.md:25-28,127-135`; prior run SEARCH-P3-001.

## Prior-Run Comparison (falcon-20261009-2117-full-08e20d1 + falcon-20261011-0400-verify-main-584e1a3)

- **SEARCH-P2-001: still-open**, now with live precision: the Wazuh alerts class remains unmanaged; additionally, 4 of the 5 Wazuh policies lack `ism_template`, and the matrix's snapshot keep-count line is stale. IRIS retention still absent.
- **SEARCH-P3-001: still-open** (legacy drift unchanged: dest_ip/event_time on 3 indices; alert.severity/alert.category also flagged).
- **New SEARCH-P2-002** (snapshot repo on root LV; guard failing). This supersedes the register's `PERF-P1-002 verified-fixed` note: that verification captured root free 26.1 GiB at 2026-10-11T02:45Z (post-reboot), but the 03:30 snapshot pushed root to 19.76 GiB by 03:45Z and the guard has been failing since; the underlying issue (root-side snapshot growth without a reclaim path) is the same class of problem PERF-P1-002 described.
- Strengths re-confirmed at this commit: 5 central ISM classes with templates; deletion metrics live (last delete 10-11 00:05Z); current mapping drift 0; dashboards authz read-only; audit logging with request bodies; watermarks default; no searchable mounts; R2 cold copies running.

## Limitations

- Wazuh indexer policy sources live outside the repo (`/opt/wazuh-docker/multi-node`, owner-side); only live cluster state could be audited, not change history. The Wazuh admin credential used is the live one from `multi-node/.env` (the stale `ops/creds.env` value fails auth - a SECRET-domain observation).
- R2 bucket lifecycle and Spaces offsite windows are owner-side; not exercised here.
- No destructive retention test was run (read-only audit); the accelerated fixture test was not re-run.
- IRIS search internals are third-party code not in the repo.
- The Oct 11 offsite backup was mid-upload at capture time; its success stamp had not advanced (see SEARCH-P2-002 / DR reconciliation).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Owner decision on Wazuh alerts retention window? | unbounded growth on the SOC host | owner statement |
| IRIS case-data retention window? | privacy/deletion obligations | owner statement |
| Where should the snapshot repo live long-term? | root vs data LV capacity trade-off | owner decision + capacity model |

## Suggested Tests

- Add a "no unmanaged daily index class" check: fail/warn when a `wazuh-*` daily index exists without a policy or when a policy lacks `ism_template`.
- Add a root-LV reclaim-path test (fixture file) proving the guard can actually free root space.
- Keep the mapping-drift rule green; add a known-query regression over the legacy window.

## Suggested Documentation Updates

- `docs/runbooks/RETENTION_MATRIX.md`: refresh the Wazuh section to the live 5-policy inventory; fix the local-snapshot keep count (3, not 7); record the root-LV snapshot repo + guard state.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: update the relocation section ("the disk guard watches /srv/falcon only" -> both LVs) and add the reclaim candidates (wz-migration tar, containerd).

## Findings

| ID | Severity | Title |
|---|---|---|
| SEARCH-P2-001 | P2 | Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale |
| SEARCH-P2-002 | P2 | OpenSearch snapshot repository still on the root LV; root free is below the guard threshold and the guard now fails every 15 minutes |
| SEARCH-P3-001 | P3 | Legacy falcon-eve indices keep divergent mappings; consumer queries silently under-return |
