# Search, Indexing, and Privacy Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: `/home/user/falcon-build` (central), `/home/user/falcon-edge-build` (edge), live host `falcon`
- Branch/commits: central `main` @ `8282d3f`; edge `main` manifest `45dfed0`, audited HEAD `f1c5def`
- Generated at: 2026-09-30T14:10Z · Auditor: audit subagent (read-only; no OpenSearch auth, Docker, or root)
- Area code: SEARCH · Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/31_search_indexing_privacy_audit.md`
- Scope limitations: search backends could not be queried (127.0.0.1:9200 is the Wazuh indexer, 401 unauth; central OpenSearch not host-published; Dashboards/Wazuh/IRIS require login). Index-level live facts come from exported metrics, prior-run capture (06 §3.3) and repo code; unobservable items are `unverified`.

## Scope

Reviewed: index template/mappings and indexed fields, ISM retention and deletion paths, OSD saved objects and index pattern, role-based index access, Wazuh dashboard surface, audit/query logging, DLQ storage, edge control-plane event storage, R2 searchable cold tier. Not reviewed: authenticated query behaviour, Wazuh console internals, container internals, owner-side Cloudflare/R2 configuration, UI accessibility.

## Evidence Reviewed

- `automation/validation/phase4_data_checks.sh` (template/mappings, ISM, fixtures, reader/site boundary test)
- `bootstrap/60-central-deploy.sh:113-215` (roles `falcon_writer`/`falcon_reader`, dashboard identity, REST audit)
- `bootstrap/91-dashboards.sh`, `config/dashboards/index-patterns.json`, `saved-searches.json`, `dashboards.json`
- `config/vector/aggregator.yaml` (indexed fields, validation, DLQ); `config/traefik/dynamic.yml:44-98`
- `automation/validation/retention_execution_test.sh`, `index_rename_migration.sh`, `restore_rehearsal.sh`
- Evidence `P9-G08` (R2 searchable mount, `_count`/`_search` ~11–13 ms); prior `P4-G03`
- Live: `falcon_metrics.prom` 13:48Z; unauth probes 9200/5601/55000; `/srv/falcon/vector/dlq/` listing
- Prior run `20260930-0320-falcon-794ba31_edge-2b5bc8b` (LIVE-P2-002, LIVE-P2-003); `OPERATOR_START_HERE.md`; `WAZUH_INTEGRATION.md`; `mct/runbooks/index-retention-policy.md`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Unauth probes 9200/5601/55000 | live | Exposure boundary | All 401; 9200 cert `CN=wazuh1.indexer`; central OpenSearch not host-published |
| `falcon_metrics.prom` 13:48Z | live | Index volume | `falcon-eve-*` 58,458,473 docs / 28.1 GB; eve age 2 s; DLQ 0 |
| `config/dashboards/*.json` vs `bootstrap/91-dashboards.sh` | repo | Search surface | 1 index pattern (`falcon-eve-*`/`timestamp`), 8 saved searches, 2 dashboards |
| `bootstrap/60-central-deploy.sh` role definitions | repo | Server-side authz | `falcon_reader` read/search on `falcon-*`; aliases get on `*` |
| `phase4_data_checks.sh:148-171` | repo | Authorization test | reader 403 on `other-site-index` and `_cat/indices`; 200 on `falcon-canary` |
| `grep` for client-side filter/autocomplete code | repo | Filter placement | None found; KuQuery filters are server-side; autocomplete is OSD default |
| Prior 06 §3.3 | prior live | Index-level state | 11 `security-auditlog-*`; `top_queries-*`; drift `event_type`, `host`; leftovers |
| `/srv/falcon/vector/dlq/` listing | live | Rejected-payload retention | Only 0-byte files dated 2026-09-22; no expiry |
| `P9-G08` evidence | prior live | External searchable copy | `falcon-eve-2026.09.21-searchable` mounted from R2; not ISM-managed |

## Executive Summary

Search is narrow and access-controlled: one OSD surface (`dash.falcon.lab`, `falcon.mainecytech.us/dash`) with 8 provisioned saved searches over a single index pattern `falcon-eve-*`, a read-only `falcon_reader` role scoped to `falcon-*`, a passing reader/site boundary test, TLS everywhere, least-privilege identities, and no anonymous UI. Filters are server-side; there is no custom autocomplete or external search provider. Risks are lifecycle and correctness: **deletion does not reach cold copies** (snapshots, R2 searchable mount) so “deleted” telemetry stays searchable; **audit/query logs have no retention** and performance-analyzer data stores query text; **mapping drift silently empties keyword aggregations** (`event_type`, `host`); **fixture indices sit inside the reader's index pattern**; and the R2 cold tier is configured manually, outside bootstrap. Exposure still depends on application logins; no repo evidence of a Cloudflare Access policy (`unverified`). Prior LIVE-P2-002/LIVE-P2-003 remain open at the current commits. Audit opinion: **GO WITH CONDITIONS** once deletion scope is documented and the cold-tier deletion path defined.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| OSD index pattern | `config/dashboards/index-patterns.json` | Search scope | `falcon-eve-*`, time `timestamp` | Medium | Includes fixtures/leftovers |
| Saved searches | `config/dashboards/saved-searches.json` | Triage queries | 8 searches, KuQuery | Low | Server-side filters |
| OSD exposure | `config/traefik/dynamic.yml:44-98` | UI routing | `dash` route without BasicAuth; OSD login | Medium | Cloudflare policy `unverified` |
| Reader role | `bootstrap/60-central-deploy.sh:122-126` | Authorization | read/search on `falcon-*`; alias get on `*` | Low | `*` is metadata-only |
| Audit REST logs | `bootstrap/60-central-deploy.sh:204-215` | Query/security audit | Enabled, no retention | High | `security-auditlog-*` growth |
| Query analytics | performance analyzer (`top_queries-*`) | Query analytics | Present per prior 06 | Medium | Query text retained |
| ISM deletion | `phase4_data_checks.sh:33-56` | Delete `falcon-eve-*` 14d | Validation script only | High | Not in bootstrap |
| Cold-tier mount | `falcon-eve-2026.09.21-searchable` (`P9-G08`) | R2 searchable copy | Mounted; not ISM-managed | Medium | Persists after local delete |
| DLQ store | `config/vector/aggregator.yaml:106-111` | Rejected events | Files, no expiry/alert | Medium | 0-byte files since 09-22 |
| Wazuh dashboard | `soc.mainecytech.us` via Traefik | Wazuh search UI | Running, own login | Medium | Auth path `unverified` |
| Edge event store | `src/falcon_control/store.py:79-110` | Control-plane events/audit | 62 events; 8,382 audit rows; no cleanup | Medium | Reached via mTLS API only |
| Fixtures | `phase4_data_checks.sh` | Tests | `falcon-canary`, `falcon-eve-fixture-test`, `other-site-index` | Low | Reader sees `falcon-*` ones |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Search routes/UI | 3 | Traefik routes; OSD login | Edge access policy unverified | Verify Cloudflare Access |
| Indexes | 3 | ISM + template | Template only in validation script | Move to bootstrap |
| Indexing jobs | 3 | Vector bulk sink | Shallow schema checks | Tighten validation |
| Indexed fields | 2 | Template; prior drift | `event_type`/`host` drift | Repair + drift check |
| Tenant filters | 3 | `site_id`/`sensor_id`; single tenant | No row filters | Site filters if multi-site |
| Permission filters | 3 | `falcon_reader` falcon-* | Shared dashboard identity | Per-operator identity later |
| Document/ticket/project/message search | N/A | No such entities | — | — |
| Admin/global search | 3 | OSD Discover; Wazuh dashboard | Scope undocumented | Document index scopes |
| Autocomplete | 1 | No custom code | Not implemented | Accept/document |
| Search logs | 2 | Audit REST + top_queries | No retention; query text | ISM + access review |
| Query analytics | 2 | `top_queries-*` | No retention | ISM policy |
| Deleted data removal | 2 | ISM test; snapshots | Deletion stops at the cluster edge | Define deletion scope |

## Detailed Review

- **Surfaces/filters/authz:** `dynamic.yml:44-98` routes OSD, Grafana, ntopng, Wazuh dashboard; `bootstrap/91` provisions 8 saved searches over `falcon-eve-*`; all filters are server-side KuQuery; the reader boundary test passes (403 non-`falcon-*` and `_cat/indices`; 200 `falcon-*`); gaps: edge access policy not in repo, one shared dashboard identity, no row/site filters.
- **Indexed data/privacy:** `aggregator.yaml` requires `site_id`/`sensor_id` and only regex-redacts `OSSEC PASS`/`K:`; indexed content includes flow 5-tuples, Suricata alerts/flows/TLS/DNS/HTTP metadata, raw device syslog, Wazuh alerts, inventory; no field classification in mappings; OD-14 legal basis still pending (cross-ref 18).
- **Retention/deletion:** ISM deletes local `falcon-eve-*` at 14d (`phase4_data_checks.sh:33-56`); snapshots keep the same docs (`bootstrap/80:139` keep 7; `disk_guard.sh:15` keep 3); the 09.21 index stays mounted searchable from R2; audit/query/ISM-history indices and DLQ have no policy — SEARCH-P2-001/003.
- **Correctness/external:** mixed mappings break `.keyword` aggregations/sorts (prior 06 §3.3; template `phase4_data_checks.sh:68-90`); R2 repository registration/mount are manual (`P9-G08`; decision log 2026-09-27T21:25Z); credentials referenced in `/home/user/.env` (owner file; types: R2/S3 keys, API tokens — values redacted).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SEARCH-001 | Search routes/UI | Traefik/OSD | Login + TLS | Edge access policy unverified | P3 | Verify CF Access |
| SEARCH-002 | Indexes | ISM/template | 14d falcon-eve | Only in validation script | P2 | Bootstrap apply |
| SEARCH-003 | Indexing jobs | Vector | Validation + DLQ | Shallow, unmonitored | P2 | Schema checks |
| SEARCH-004 | Indexed fields | template | Explicit core fields | Drift; no classification | P2 | Repair + classify |
| SEARCH-005 | Tenant filters | `site_id`/`sensor_id` | Ingest-required | No row filters | P3 | Revisit if multi-site |
| SEARCH-006 | Permission filters | `falcon_reader` | Index-pattern ACL | Shared identity | P3 | Per-operator later |
| SEARCH-007 | Document search | N/A | No such entities | — | — | — |
| SEARCH-008 | Admin/global search | OSD/Wazuh | Role-scoped | Scope undocumented | P3 | Document scopes |
| SEARCH-009 | Autocomplete | none found | None | Not implemented | P3 | Accept/document |
| SEARCH-010 | Search logs | audit REST/top_queries | Enabled | No retention | P2 | ISM policies |
| SEARCH-011 | Query analytics | top_queries | Enabled | Query text retained | P2 | ISM + access review |
| SEARCH-012 | Deleted data removal | ISM test/snapshots | Local delete | Cold copies persist | P2 | Deletion runbook |

## Findings

### Finding ID: SEARCH-P2-001 - ISM deletion does not remove searchable cold copies; deletion scope undefined
- Severity: P2 (raise to P1 if the dataset is classified personal or a deletion obligation applies) · Confidence: High for repo/prior evidence, Medium for current mount state (`unverified`) · Area: SEARCH · Status: open
- Evidence: `automation/validation/phase4_data_checks.sh:33-56` (local 14d delete); `bootstrap/80-offsite-backup.sh:139` (keep 7); `P9-G08` (`falcon-eve-2026.09.21-searchable` mounted from R2, full `_search`); prior 06 §3.3 (mount not ISM-managed)
- What is happening: when ISM deletes an index, identical documents persist in local/Spaces snapshots and (for 09.21) in a live searchable index; deletion covers only the cluster copy.
- Why it matters: search and restores can expose data the operator believes deleted; retention statements are incomplete.
- User / business impact: false confidence in deletion; compliance exposure · Security / privacy / reliability impact: monitoring data (IPs, device logs) queryable beyond the stated window.
- Recommended fix: define a store-by-store deletion matrix (cluster, mounts, local/offsite snapshots, R2 lifecycle) and a runbook step that drops mounts with/before ISM deletion; state that backups are retention copies with their own window.
- Suggested validation: delete a disposable index and assert absence from `_cat/indices`, mounts and a sampled restore; test R2 lifecycle rules.
- Owner suggestion: falcon maintainer + owner · Effort: M · Dependencies: OD-14/classification decision
- Status: open

### Finding ID: SEARCH-P2-002 - Mapping drift silently breaks keyword search/aggregations
- Severity: P2 · Confidence: Medium (live mappings not re-read unauthenticated) · Area: SEARCH · Status: still-open (LIVE-P2-003)
- Evidence: prior 06 §3.3 (`event_type` keyword since 09.23 vs text(+keyword) on 09.21/09.22; `host` text-only on 09.29/09.30); `config/dashboards/saved-searches.json` uses `event_type`/`host`; `phase4_data_checks.sh:68-71`
- What is happening: mixed mappings across index generations; `.keyword` aggregations against older indices and sorts on `host` fail or return empty silently.
- Why it matters: silent query breakage can under-report security events during triage.
- User / business impact: missed events; wrong dashboard conclusions · Security / privacy / reliability impact: detection/visibility correctness.
- Recommended fix: normalise mappings (reindex or runtime fields), ensure `host.keyword`/`event_type.keyword`, add a per-index mapping-drift check/metric.
- Suggested validation: daily aggregation assertion on `event_type.keyword` and `host.keyword`; run after mapping changes.
- Owner suggestion: falcon maintainer · Effort: M · Dependencies: reindex window
- Status: still-open

### Finding ID: SEARCH-P2-003 - Search/audit logs have no retention and store query text
- Severity: P2 · Confidence: High for repo, Medium for live counts (`unverified`) · Area: SEARCH · Status: still-open (LIVE-P2-002 / DATA-P2-005)
- Evidence: `bootstrap/60-central-deploy.sh:204-215` (REST audit enabled, no retention); prior 06 §3.3 (11 `security-auditlog-*`, daily `top_queries-*`, `.opendistro-ism-managed-index-history-*`); `phase4_data_checks.sh:33-56` covers only `falcon-eve-*`
- What is happening: audit events and performance-analyzer top queries accumulate indefinitely; `top_queries-*` can include operator search terms.
- Why it matters: unbounded growth and privacy exposure of query text; the “search logs” control is absent.
- User / business impact: disk pressure; query patterns visible to admin readers · Security / privacy / reliability impact: data minimisation/retention gap.
- Recommended fix: ISM templates (audit 30d, top_queries 14d, ISM history 30d), restrict admin reading, document access; verify `falcon_reader` stays 403.
- Suggested validation: accelerated-delete test per policy; access check for the reader role.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: retention decision
- Status: still-open

### Finding ID: SEARCH-P2-004 - Cold-tier searchable copy and R2 registration are manual, outside repo configuration
- Severity: P2 · Confidence: High (repo/decision log); R2 bucket state `unverified` · Area: SEARCH · Status: open
- Evidence: `compose/central/docker-compose.yml:56-80`; decision log 2026-09-27T21:25Z (mount created ad-hoc); `P9-G08`; no `falcon-r2` registration/mount step in `bootstrap/*.sh`; credentials referenced in `/home/user/.env` (types only)
- What is happening: a rebuilt cluster would not recreate the R2 repository or the mounted searchable index; no repo-defined bucket lifecycle.
- Why it matters: cold-tier search silently disappears on rebuild; the only recreation record is a decision-log entry.
- User / business impact: unexpected loss of searchable history; manual recovery · Security / privacy / reliability impact: unmanaged external copy of telemetry.
- Recommended fix: script idempotent R2 registration + mount as a bootstrap step (or document manual ownership), and define bucket lifecycle/retention.
- Suggested validation: on a scratch node, register + mount and run `_count`/`_search`; rebuild test.
- Owner suggestion: falcon maintainer + owner · Effort: M · Dependencies: R2 credentials/lifecycle
- Status: open

### Finding ID: SEARCH-P3-005 - Leftover fixture indices are inside the searchable index pattern
- Severity: P3 · Confidence: High (repo); Medium for current live presence · Area: SEARCH · Status: still-open (part of LIVE-P2-002)
- Evidence: `phase4_data_checks.sh:148-171` creates `falcon-canary`, `falcon-eve-fixture-test`, `other-site-index`; prior 06 §3.3 lists `falcon-test` and a retention-test index; `bootstrap/60:122-126` grants reader `falcon-*`; OSD pattern `falcon-eve-*`
- What is happening: test documents remain in the cluster and appear in search/dashboards; `other-site-index` is intentionally unreadable to the reader.
- Why it matters: synthetic results can mislead triage and add noise.
- User / business impact: minor confusion/noise · Security / privacy / reliability impact: low.
- Recommended fix: cleanup traps after validation runs; keep fixtures outside the dashboard pattern; assert cleanup.
- Suggested validation: post-run assertion that only expected indices match `falcon-eve-*`.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: still-open

### Finding ID: SEARCH-P3-006 - Search-surface hardening gaps: edge access evidence, shared identity, scope docs
- Severity: P3 · Confidence: High (repo); exposure item `unverified` · Area: SEARCH · Status: open · exposure item `unverified`
- Evidence: `config/traefik/dynamic.yml:57-98` (`dash`, `falcon-dash`, `soc-wazuh` routes without BasicAuth); `bootstrap/95-cloudflared.sh:65` (hostnames managed remotely); `bootstrap/60:128-138` (one `falcon-dashboard` user; no per-site filters); no autocomplete code; `OPERATOR_START_HERE.md` describes undirected Discover use
- What is happening: authentication relies on OSD/Wazuh logins; the Cloudflare tunnel policy is not in the repo; all operators share one identity with no `site_id` row scoping; autocomplete scope is undocumented.
- Why it matters: exposure depends on a control outside the audit; no search attribution; onboarding friction.
- User / business impact: low today (single owner/tenant EX-22); future multi-operator risk · Security / privacy / reliability impact: potential internet-facing login pages if no edge policy; brute-force surface.
- Recommended fix: verify/record the Cloudflare Access policy (or add BasicAuth in Traefik); document search scopes per role; when a second operator/site appears, add per-user identities and site-scoped roles.
- Suggested validation: external probe of the published hostnames expecting a challenge before login; role-to-index matrix review.
- Owner suggestion: owner + falcon maintainer · Effort: S (M for future identities) · Dependencies: dashboard/Cloudflare access
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| “Deleted” data remains searchable via cold copies | P2 | Medium | Compliance/trust | `P9-G08`; keep 7/3 | SEARCH-P2-001 |
| Mapping drift gives silent wrong results | P2 | Medium | Missed detections | prior 06; template | SEARCH-P2-002 |
| Audit/query logs grow; query text retained | P2 | High | Disk/privacy | no ISM; top_queries | SEARCH-P2-003 |
| Cold tier unreproducible on rebuild | P2 | Medium | Lost search history | manual registration | SEARCH-P2-004 |
| Test data inside production search | P3 | High | Noise | fixtures | SEARCH-P3-005 |
| Dashboard exposure without edge policy | P3 | Low | Brute force | tunnel config | SEARCH-P3-006 |

## Recommendations

### Immediate / Release Blocking
1. Record the Cloudflare access policy (or add BasicAuth) for the published dashboards (SEARCH-P3-006). 2. Define/execute deletion for cold copies when an index is deleted; document the window (SEARCH-P2-001).
### This Week
3. ISM for `security-auditlog-*`, `top_queries-*`, ISM history (SEARCH-P2-003). 4. Clean fixtures and exclude `falcon-test-*` from the dashboard pattern (SEARCH-P3-005).
### This Month
5. Mapping repair + drift check (SEARCH-P2-002). 6. Script R2 registration/mount; define bucket lifecycle (SEARCH-P2-004). 7. Document search scopes/retention per role (SEARCH-P3-006).
### Later / Platform Evolution
8. Per-operator identities and site-scoped roles if the lab grows (SEARCH-P3-006).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| ISM template for audit/query indices | Bounds growth and query-text exposure | bootstrap/ISM script | accelerated delete test |
| Remove fixture indices after phase4 runs | Clean search results | `phase4_data_checks.sh` | `_cat/indices` check |
| Add `host.keyword` on new indices | Fixes aggregations/sorts | template + reindex | aggregation assertion |
| Verify Cloudflare Access | Closes unknown exposure | owner Cloudflare config | external probe |
| Add DLQ age metric | Rejected-data visibility | `export_monitor_metrics.sh` | metric on injected reject |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Deletion matrix incl. cold copies | P2 | falcon maintainer + owner | M | OD-14/classification |
| Audit/query ISM policies | P2 | falcon maintainer | S | retention decision |
| Mapping drift checker | P2 | falcon maintainer | M | reindex window |
| R2 bootstrap/lifecycle | P2 | falcon maintainer + owner | M | R2 credentials |
| Per-operator search identities | P3 | falcon maintainer | M | multi-operator need |

## Suggested Tests

- Security: unauth probes of all search surfaces (expect 401/challenge); reader 403 on audit/other-site indices; per-site negative test when added.
- Privacy: deletion drill (ISM + mount + snapshot) proving the document is not retrievable after the documented window; DLQ age-out.
- Correctness: daily aggregation assertions on `event_type.keyword`/`host.keyword`; saved-search smoke test after mapping changes.
- Regression/manual: re-run `phase4_data_checks.sh` boundary checks with fixture cleanup; quarterly search-scope and R2 lifecycle review.

## Suggested Documentation Updates

- `docs/runbooks/OPERATOR_START_HERE.md`: which indices each role can search; retention per class.
- New `docs/runbooks/DATA_DELETION.md`: store-by-store deletion (cluster, mounts, snapshots, R2, DLQ).
- `docs/runbooks/WAZUH_INTEGRATION.md`: Wazuh indexer retention and search scope.
- `docs/runbooks/CAPACITY_AND_TELEMETRY.md`: query/audit log growth line item.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there a Cloudflare Access policy on the dashboard hostnames? | Determines public exposure | Owner Cloudflare config / external probe |
| Are `security-auditlog-*`/`top_queries-*` still present and how large? | Retention priority | Authenticated `_cat/indices` |
| Does the searchable mount auto-expire via ISM or persist? | Deletion correctness | `_plugins/_ism/explain/falcon-eve-*` |
| Which identities can read the Wazuh indexer; is OD-14 still REQUESTED? | Privacy scope/legal basis | Wazuh security config (path only); owner record |

## Appendix

Live 2026-09-30: unauth `https://127.0.0.1:9200` → 401 (`CN=wazuh1.indexer`); `:5601`/`:55000` → 401; central OpenSearch not host-published. `falcon_metrics.prom` 13:48Z — `falcon-eve-*` 58,458,473 docs / 28,141,120,208 B; DLQ 0; eve age 2 s. `/srv/falcon/vector/dlq/` holds only 0-byte files dated 2026-09-22. Provisioned search objects: 1 index pattern, 8 saved searches, 2 dashboards. Prior-run carry-over: LIVE-P2-002 and LIVE-P2-003 still open; PRIV-P2-002 is the privacy counterpart of SEARCH-P2-001/003.
