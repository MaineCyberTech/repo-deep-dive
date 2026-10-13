# 25_multi_tenant_isolation_attack_simulation — Prompt 25 - Multi-Tenant Isolation Attack Simulation

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `25_multi_tenant_isolation_attack_simulation.md` (area MT, prompt)

## Verification Performed

# Multi-Tenant Isolation Attack Simulation

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon (`MaineCyberTech/falcon`)
- Branch: main
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:35:00Z
- Auditor: subagent (domain 25)
- Area code: MT
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/25_multi_tenant_isolation_attack_simulation.md`
- Scope limitations: the repository is a single-operator infrastructure/security-monitoring stack, not a multi-tenant SaaS. The N/A determination is evidence-based below; live checks were read-only host/container inspection. No destructive or exfiltration actions were performed.

## Scope

Reviewed: tenant/org/workspace IDs, membership checks, DB queries, API routes, server actions, client fetchers, RLS, storage/file access, realtime channels, search/export, admin overrides, invitations, notifications, background jobs, webhooks, audit logs, caching.

Not reviewed: none beyond the N/A determination — the tenant boundary does not exist in this repository.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/architecture/IDENTITY_AND_SECRETS.md` §1 | doc | human identities | exactly one interactive account (`user`) + root break-glass |
| `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §5.1 | doc | known gaps | "No SSO / no per-person identity"; single-operator lab (EX-22) |
| `automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml:6` | config | tenancy setting | `opensearch_security.multitenancy.enabled: false` |
| Live `falcon-central-opensearch-dashboards-1` config | live | central OSD tenancy | `opensearch_security.multitenancy.enabled: true` (Private/Global), but only service + admin accounts exist |
| `bootstrap/60-central-deploy.sh:131-155` | deployment | OpenSearch identities | one admin, one dashboard user, writer/backup/healthcheck services |
| Live OpenSearch security API | live | role scoping | `falcon_reader`/`falcon_writer` scope = `falcon-*` (all sites pooled) |
| `config/opensearch/falcon-eve-template.json:1292` | schema | site attribute | `site_id` is a data label, not an access boundary |
| `grep -rniE 'tenant_id|org_id|workspace_id'` (repo, excluding vendored mct) | search | tenant model existence | no matches |
| Live Grafana `/api/users` | live | console users | one user (`admin`) |
| Live `wg show wg0` + `/etc/wireguard/wg0.conf` | live | fleet "tenant" analogue | 8 peers: site/sensor peers + 3 client endpoint devices, all on 10.99.0.0/24 |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Repo-wide grep for tenant/org/workspace identifiers | reproduction | prove no tenant model | no tenant scoping code in falcon (only vendored Shuffle org IDs under `mct/`) |
| Wazuh dashboard tenancy setting (live) | reproduction | tenancy boundary | disabled; 15-min session TTL |
| Central OSD tenancy (live) | reproduction | tenancy boundary | plugin multitenancy enabled (Private/Global) but no multi-user model; single admin |
| Grafana user enumeration (read-only) | reproduction | multi-user model | single admin; 0 service accounts |
| OpenSearch role bodies (live) | reproduction | data scoping | read/write patterns are `falcon-*`, i.e. all sites share one namespace |
| `wg show wg0` + peer comments | reproduction | fleet separation | site peers and client endpoints share wg0 and one allowlist (see SEC-P3-004) |
| `docker ps` + index inventory | reproduction | shared data plane | all feeds share `falcon-*` indices; role-based (not tenant-based) access |

## Executive Summary

Not applicable: falcon is a single-tenant, single-operator security-monitoring stack by design. There is no tenant/org/workspace model, no membership service, no per-tenant storage namespace, and no multi-user console model. Data from multiple edge sites is deliberately pooled into shared `falcon-*` indices and distinguished only by data labels (`site_id`), which is a routing/analytics attribute, not an isolation boundary. The closest analogue to "tenants" — multiple monitored sites and endpoint agents — has no per-site access separation; that is consistent with the product's single-operator purpose (EX-22) and is recorded as an accepted model in the owner action register.

The one boundary that did change this run is the WireGuard tunnel: the blanket accept is fixed, so peers no longer reach SSH/consoles/enrollment, but site peers and client endpoints still share wg0 and one per-port allowlist (tracked as SEC-P3-004, a defense-in-depth residual, not a tenancy issue). The prior run also classified this domain N/A with no findings; nothing at the audited commit changes that determination.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Tenant/org/workspace IDs | n/a | tenancy | absent | N/A | no tenant model |
| Membership checks | n/a | tenancy | absent | N/A | single operator |
| DB queries | OpenSearch roles | data access | role-scoped, shared indices | N/A | `falcon_writer`/`falcon_reader`/`falcon_backup` |
| API routes | OpenSearch/Wazuh/enroll | API access | service credentials | N/A | no tenant context |
| Server actions | n/a | — | absent | N/A | no web app |
| Client fetchers | n/a | — | absent | N/A | no SPA |
| RLS | n/a | row security | absent | N/A | no SQL app datastore exposed |
| Storage/file access | `/srv/falcon/**` | files | host-local, OS permissions | N/A | not multi-tenant |
| Realtime channels | n/a | — | absent | N/A | SSE in consoles only |
| Search/export | OpenSearch/Dashboards | query/export | role-scoped (`falcon-*`) | N/A | all users single-operator |
| Admin overrides | OpenSearch admin | break-glass | single admin | N/A | EX-19 |
| Invitations | n/a | — | absent | N/A | no invite flow |
| Background jobs | systemd timers, backup | jobs | root-run | N/A | no tenant context |
| Webhooks | Grafana→relay→ntfy | delivery | single shared topic set | N/A | no tenant routing |
| Audit logs | auditd/OpenSearch/Wazuh | accountability | host/estate-wide | N/A | no tenant partitioning |
| Caching | Redis (ntopng), OpenSearch caches | cache | service-scoped | N/A | no tenant keys |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Tenant/org/workspace IDs | 0 (N/A) | grep evidence | no tenant model | none (by design) |
| Membership checks | 0 (N/A) | IDENTITY §1 | single operator | none |
| DB queries | N/A | role-scoped | — | none |
| API routes | N/A | service credentials | — | none |
| Server actions | N/A | — | — | none |
| Client fetchers | N/A | — | — | none |
| RLS | N/A | no SQL datastore | — | none |
| Storage/file access | N/A | host-local | — | none |
| Realtime channels | N/A | — | — | none |
| Search/export | N/A | role-scoped | — | none |
| Admin overrides | N/A | single admin | — | none |
| Invitations | N/A | — | — | none |

## Detailed Review

### Item: Tenant boundary determination

- Evidence: `IDENTITY_AND_SECRETS.md` §1 (one interactive account); `ACCESS_AND_ACCOUNTS.md` §5.1 ("No SSO / no per-person identity"); `OWNER_ACTIONS.md` C6 (single-operator EX-22 accepted); repo grep shows no tenant identifiers; live OpenSearch roles scope `falcon-*`.
- What it does: n/a — no multi-tenancy.
- How it appears to work: all data lands in shared `falcon-*` indices; access is role-based at the OpenSearch layer; console access is single-admin.
- Current controls: OpenSearch least-privilege roles; firewall; Access edge.
- Missing controls: per-site access separation (not required for the single-operator model).
- Risks: if the product ever becomes multi-operator/multi-customer, the shared-index model and single-admin consoles would need tenant scoping; this is future work, not a current issue.
- Recommended improvement: record the assumption explicitly if/when multi-operator work starts.
- Suggested tests: none today; future: per-site scoped read tests if site-scoped roles are introduced.
- Suggested docs: none required now; `EVOLUTION_GUIDE.md` already notes multi-tenant flags only at fleet scale.

### Item: Site data labelling

- Evidence: `config/opensearch/falcon-eve-template.json:1292` (`site_id`).
- What it does: distinguishes event origin for analytics.
- Current controls: query-time filtering, not enforced authorization.
- Risks: none in the single-operator model; data from all sites is intentionally visible to the operator.
- Recommended improvement: if site-scoped roles are ever added, promote `site_id` to a document-level-security field.

### Item: Fleet peer classes on the tunnel (closest isolation analogue)

- Evidence: live `/etc/wireguard/wg0.conf` (3 `client peer:` entries alongside site/sensor peers); `config/nftables/falcon.nft:30-33` (per-port allowlist applies to all peers).
- What it does: carries both monitored-site traffic and owner endpoint devices.
- Current controls: per-port allowlist (no blanket accept); mTLS at the control plane; token at enrollment.
- Missing controls: peer-class separation (see SEC-P3-004).
- Risks: a compromised endpoint device can reach the control-plane API surface (mTLS-gated) and the Wazuh tunnel proxies; not a tenancy boundary, but the nearest thing to cross-"tenant" reachability in this stack.
- Recommended improvement: separate address ranges/interface per peer class; document the accepted model.

## Scenario / Control Matrix

The prompt asks for attack scenarios MT-001..MT-008. Because no tenant boundary exists, each scenario is evaluated as "no boundary to attack" with the closest analogue noted.

| ID | Scenario | Evidence | Current control | Result | Severity | Recommendation |
|---|---|---|---|---|---|---|
| MT-001 | Cross-tenant read via object ID in an API route | repo grep: no tenant IDs; OpenSearch roles `falcon-*` | role-based access | N/A — no tenant boundary; IDs are not tenant-scoped because no tenancy exists | — | none (by design) |
| MT-002 | Cross-site read via search/export (site A vs site B) | shared `falcon-*` indices; `site_id` label only | query-time filtering | Accepted — all sites visible to the single operator by design (EX-22) | — | document assumption |
| MT-003 | Cross-tenant write via ingest credentials | `falcon_writer` write `falcon-*` | shared-secret ingest + role | N/A — single namespace | — | none |
| MT-004 | Tenant traversal via RLS bypass | no RLS datastore | OpenSearch security | N/A | — | none |
| MT-005 | Cross-tenant file access in object storage | host-local files, 0600 root; snapshot repo local/offsite | OS permissions | N/A — no per-tenant storage | — | none |
| MT-006 | Cross-tenant realtime channel subscription | no websocket/realtime multi-tenant channels | console SSE only | N/A | — | none |
| MT-007 | Invitation/membership escalation | no invite flow | n/a | N/A | — | none |
| MT-008 | Admin override crossing tenant lines | single admin (Grafana/OpenSearch/ntfy); break-glass root | single-operator model | Accepted — no tenant lines exist | — | per-service accounts at production (SEC/ADMIN) |
| MT-009 | VPN peer reaches another peer's data/control plane | live nft per-port set; wg0 shared by client endpoints and site peers | per-port allowlist + mTLS | Residual — every peer can reach CP 9443 / Wazuh proxies (SEC-P3-004) | P3 | peer-class separation |
| MT-010 | Search/export scoping | `falcon_reader` `falcon-*` | role-scoped | N/A — single operator | — | none |
| MT-011 | Admin overrides | EX-19; live single admin | break-glass | N/A | — | none |
| MT-012 | Invitations | n/a | — | N/A | — | none |

## Findings

_No findings in this domain._ No tenant boundary exists to attack; the N/A determination is evidence-backed above. The nearest analogue (fleet peer classes on wg0) is tracked as SEC-P3-004 in the SEC domain.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Future multi-operator/multi-tenant evolution on a shared-index, single-admin base | Low (future) | Low | Medium | IDENTITY §1; EVOLUTION_GUIDE note | design tenant scoping before multi-operator rollout |
| Client endpoint peers share the tunnel allowlist with site peers | Low | Low | Medium | live wg0.conf; nft | peer-class separation (SEC-P3-004) |

## Recommendations

### Immediate / Release Blocking

- None.

### This Week

- None.

### This Month

- None.

### Later / Platform Evolution

- If a second operator/customer appears, design per-site/per-operator scoping (OpenSearch document-level security, per-operator identities) before onboarding.
- Separate WireGuard peer classes if endpoint count grows (SEC-P3-004).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Record the single-tenant assumption in the access matrix | avoids future ambiguity | `docs/security/access_control_matrix.md` (proposed) | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Tenant-scoping design (only when multi-operator) | P3 (future) | @owner | L | product decision |
| WG peer-class separation | P3 | @owner | M | device re-enrollment |

## Suggested Tests

- None for the current single-tenant model.
- Future: site-scoped read test asserting a site operator cannot query another site's documents.
- Regression (today): negative probe from a client VPN peer to 9443/15140 after peer-class separation.

## Suggested Documentation Updates

- None required now; the proposed consolidated access matrix should state "single-tenant by design (EX-22)".

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is multi-operator/multi-site isolation on the roadmap? | determines when tenant scoping is needed | owner roadmap |
| Will client endpoints get their own WG address range? | bounds endpoint reachability | owner network plan |

## Prior-Run Comparison

| Prior finding (falcon-20261009-2117-full-08e20d1) | Status now | Notes |
|---|---|---|
| (none — domain N/A) | unchanged | re-verified at `f5cb7c9`: no tenant model; Wazuh tenancy disabled; central OSD tenancy enabled but single-user; single operator; 8 wg peers incl. 3 client devices |

## Limitations

- "Tenant" was interpreted as a product-level tenant/customer boundary. If the intended interpretation is per-site isolation across the edge fleet, the answer is still "no isolation by design": sites share indices and a single operator — documented as the accepted model, not a defect.
- Cloudflare Access and vendor app roles were read via API for existence/policies only; no multi-user behavior was exercised.

## Appendix

- Determination commands: `grep -rniE 'tenant_id|org_id|workspace_id' --include='*.py' --include='*.yml' ...` (no falcon matches); `docker exec falcon-central-opensearch-dashboards-1 grep -iE 'multitenancy|cookie' .../opensearch_dashboards.yml`; Grafana `/api/users`; OpenSearch `_plugins/_security/api/roles/falcon_*`; `wg show wg0`; `/etc/wireguard/wg0.conf` peer comments.
- Findings: none.

## Findings

_No findings in this domain._
