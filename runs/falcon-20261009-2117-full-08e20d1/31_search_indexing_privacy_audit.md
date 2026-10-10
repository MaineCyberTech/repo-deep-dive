# 31_search_indexing_privacy_audit — Prompt 31 - Search, Indexing, and Privacy Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `31_search_indexing_privacy_audit.md` (area SEARCH, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon
- Branch: main (origin/main)
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:43:00Z
- Auditor: repo-deep-dive full-domain subagent (read-only, no mutation)
- Area code: SEARCH
- Live vantage: this audit ran on the live lab host. Live tree `/home/user/falcon-build` is at `6e4fccd` (local `main`, 2026-10-09 ops commit); every SEARCH-relevant file (config/opensearch/*, bootstrap/61-search-policies.sh, retention runbooks, retention/metrics scripts) is identical between `6e4fccd` and `08e20d1` (empty diff), so the live observations bind to the audited commit.

## Scope

Reviewed: central OpenSearch 2.19 single node (`falcon-central-opensearch-1`) index classes, the composable template and five repo-managed ISM policies (`config/opensearch/`, `bootstrap/61-search-policies.sh`), retention execution and observability (`automation/validation/ism_retention_metrics.sh`, `retention_execution_test.sh`, `mapping_drift_check.py`, `consumer_query_check.sh`), OpenSearch security (internal users/roles, audit config, index read scope), OpenSearch Dashboards exposure (`config/traefik/dynamic.yml`, live routes), the Wazuh 3-node indexer estate (owner-side at `/opt/wazuh-docker/multi-node`), the IRIS case store (deployed by `compose/mct/iris-web/`), deletion scope (cluster vs snapshots vs Spaces vs R2 cold copies; the former `falcon-eve-2026.09.21-searchable` mount), and tests.

Not reviewed: query/analytics inside third-party OpenSearch Dashboards itself beyond its data scope; the R2 bucket lifecycle (owner-side, not in the repo - SEARCH-P2-004 residual); Wazuh indexer ISM policy source (owner-side files, not in the repo); IRIS application search internals (third-party app, source not in the repo).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `config/opensearch/falcon-eve-template.json`, `bootstrap/61-search-policies.sh` | config/deploy | pinned template (`dynamic: false`, 485 fields) + 5 ISM policy classes | single source of truth; idempotent apply |
| `config/opensearch/*-ism-policy.json` | config | falcon-eve 14d, auditlog 30d, topqueries 14d, ism-history 30d, test-cleanup 1d | live policy list matches + 2 documented stale policies |
| `docs/runbooks/RETENTION_MATRIX.md`, `docs/runbooks/SCHEMA_AND_RETENTION.md` | docs | per-class retention statement, deletion scope, residuals | Wazuh statement is stale vs live |
| `automation/validation/ism_retention_metrics.sh` + live `falcon_retention.prom` | metrics | deletion accounting from ISM history | live: 2 falcon-eve deletes in 24h |
| `automation/validation/mapping_drift_check.py`, `consumer_query_check.sh` | validation | mapping drift/silent-empty detection | live drift quantified |
| live central cluster: `_cat/indices`, `_plugins/_ism/policies`, `_mapping`, `_plugins/_security/api/*` | live | current indexes, policies, mappings, authz | read-only via docker exec |
| live Wazuh indexer: `_cat/indices`, `_plugins/_ism/policies`, `_plugins/_ism/explain/*` | live | Wazuh retention truth | alerts class unmanaged |
| `compose/mct/iris-web/*` + live IRIS volumes | deploy/live | case-file store scope | digest-pinned in repo; no retention |
| `automation/validation/retention_execution_test.sh`, tests | tests | accelerated retention proof on fixtures | fixture class exercised live (5 retained deletes) |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Central retention working | live `_cat/indices` | falcon-eve oldest `2026.09.26` (14d window); security-auditlog oldest `2026.09.20` (30d); top_queries `2026.10.02`-`2026.10.09`; ISM history `2026.09.21`-`2026.10.09` |
| ISM policies live | `GET /_plugins/_ism/policies` | 5 repo-managed policies + 2 documented stale (`falcon-retention-exec-*`, `mon-eve-policy`) |
| Deletion observability | `/srv/falcon/textfile/falcon_retention.prom` | `falcon_ism_delete_metric_ok 1`; `deleted_indices_24h{falcon-eve-policy}=2`; last delete `2026-10-09T16:51Z` |
| Searchable R2 mount dropped | `_cat/indices` | `falcon-eve-2026.09.21-searchable` is gone (aged out with the 14d policy) |
| Dashboards authorization | live users/roles | `falcon-dashboard` -> `kibana_user` + `falcon_reader` (read/search on `falcon-*` only); `top_queries-*` and `security-auditlog-*` are admin-only |
| Public dashboards route | `curl https://falcon.mainecybertech.us/dash` | 302 Cloudflare Access (gated) |
| Audit logging | `GET /_plugins/_security/api/audit` | enabled; compliance enabled; `log_request_body=true`; REST+transport on |
| Query analytics content | sample `top_queries-2026.10.09-59468` | stores full query bodies (`source`), 14d retention, admin-only |
| Wazuh indexer retention | `_plugins/_ism/explain/wazuh-alerts-4.x-2026.10.09` and `...2026.09.28` | `policy: null` - the alerts class is unmanaged |
| Wazuh policy inventory | `GET /_plugins/_ism/policies` | `wazuh-retention` (30d, template null), `wazuh-archives-14d` (template null), `wazuh-states-retention` (90d), `security-auditlog-retention` (180d, template), `elastiflow` (14d); 83 indices total |
| Mapping drift | `GET falcon-eve-2026.09.27/_mapping` vs `...2026.10.09/_mapping` | legacy: `dest_ip` text, `event_time` absent; current: `dest_ip` ip, `event_time` date |
| IRIS store | live volume sizes | downloads 4 KiB, server_data 20 KiB, DB 78 MiB; no retention policy (documented gap) |

## Executive Summary

The central search stack is substantially hardened and its retention now works: five ISM classes are live (EVE 14d, security audit log 30d, top queries 14d, ISM history 30d, test/fixture 1d), deletions are measured and alertable (2 EVE deletes in 24h; last 2026-10-09T16:51Z), the composable template pins mappings with `dynamic: false`, the dashboard user is read-only on `falcon-*` only, the public dashboards route is Access-gated, and audit logging captures REST/transport events. Two gaps remain. First (P2): the prior SEARCH-P2-001 retention gap is only partially fixed - the Wazuh indexer actually has owner-side ISM policies (the repo doc claiming "none configured" is stale), but the primary `wazuh-alerts-4.x-*` class has no policy attached and no `ism_template`, so it is unmanaged going forward; IRIS case data has no retention by design/owner decision. Second (P3): legacy `falcon-eve` indices (09.21-09.30) keep divergent mappings, so consumer queries over that window silently under-return (documented residual with live drift metrics; repair is owner-gated).

## Findings

### SEARCH-P2-001 (prior) - Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale

- Severity: P2, Confidence: High (live cluster), Status: still-open
- What is happening: central classes are covered; Wazuh `wazuh-alerts-4.x-*` has no policy attached and no template (live explain `policy: null`); IRIS has no retention; the repo doc still says the Wazuh indexer has no ISM policy at all.
- Why it matters: the alert class is the fastest-growing Wazuh dataset; unbounded growth is a capacity/retention-compliance risk, and the stale doc misstates the live estate.
- Recommended fix: attach a template-backed ISM policy to `wazuh-alerts-4.x-*` (owner-gated), update `RETENTION_MATRIX.md` to the live policy inventory, and add an unmanaged-index metrics check.
- Owner suggestion: @owner. Validation: `_ism/explain/wazuh-alerts-*` shows a policy on newly created indices; matrix matches `_plugins/_ism/policies`.

### SEARCH-P3-001 (new) - Legacy falcon-eve indices keep divergent mappings; consumer queries silently under-return

- Severity: P3, Confidence: High (live mappings), Effort: M-L (owner-gated reindex)
- What is happening: `falcon-eve-2026.09.27` maps `dest_ip` as text and has no `event_time`; current indices map `dest_ip` as ip and `event_time` as date. The template is only applied to new indices.
- Why it matters: range/term queries over the legacy window return silently empty/partial results, which reads as healthy zeros.
- Recommended fix: schedule the owner-gated reindex or runtime-field repair; keep the legacy window labelled; the drift metric/rule already quantifies it.
- Owner suggestion: @owner. Validation: `mapping_drift_check.py` reports 0 legacy drift; a known query over the window returns the expected counts.

## Prior-Run Comparison (falcon-20261005-full-main-e267ce1)

- Prior `SEARCH-P2-001` ("retention enforced only for falcon-eve; Wazuh/IRIS unbounded", status still-open): partially superseded by live evidence - the central cluster now enforces five classes, and the Wazuh indexer has owner-side policies the prior run did not see. The finding is carried forward with the same ID for the remaining gaps (Wazuh alerts class unmanaged; IRIS no retention; stale doc).
- New this run: the legacy mapping-drift finding (P3) and the live authorization/audit inventory (strengths). The prior report body was empty; this run adds the live verification record.

## Limitations

- Wazuh indexer policy sources live outside the repo (`/opt/wazuh-docker/multi-node`, owner-side); only the live cluster state could be audited, not its change history.
- R2 bucket lifecycle and the Spaces offsite retention windows are owner-side and were not exercised; the former searchable mount is verifiably gone, but R2 lifecycle verification (SEARCH-P2-004) remains an owner item.
- No destructive retention test was run (read-only audit); accelerated retention evidence for the fixture class is from the repo's own recorded test artifacts and live metrics.
- IRIS search/upload internals are third-party code not present in the repo; only the deployment/store were reviewed.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEARCH-P2-001 | P2 | Retention gaps remain on the Wazuh indexer alerts class and IRIS; RETENTION_MATRIX.md is stale vs the live clusters |
| SEARCH-P3-001 | P3 | Legacy falcon-eve indices keep divergent mappings; consumer queries against them silently under-return |
