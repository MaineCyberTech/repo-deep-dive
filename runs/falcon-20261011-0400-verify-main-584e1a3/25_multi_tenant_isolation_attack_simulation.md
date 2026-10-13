# 25_multi_tenant_isolation_attack_simulation — Prompt 25 - Multi-Tenant Isolation Attack Simulation

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `25_multi_tenant_isolation_attack_simulation.md` (area MT, prompt)

## Verification Performed

# Multi-Tenant Isolation Attack Simulation

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon (`MaineCyberTech/falcon`)
- Branch: main
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65`
- Generated at: 2026-10-09T21:45:00Z
- Auditor: subagent (domain 25)
- Area code: MT
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/25_multi_tenant_isolation_attack_simulation.md`
- Scope limitations: the repository is a single-operator infrastructure/security-monitoring stack, not a multi-tenant SaaS. The N/A determination is evidence-based below; live checks were limited to read-only host/container inspection.

## Scope

Reviewed: tenant/org/workspace IDs, membership checks, DB queries, API routes, server actions, client fetchers, RLS, storage/file access, realtime channels, search/export, admin overrides, invitations, notifications, background jobs, webhooks, audit logs, caching.

Not reviewed: none beyond the N/A determination — the tenant boundary does not exist in this repository.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/architecture/IDENTITY_AND_SECRETS.md` §1 | doc | human identities | exactly one interactive account (`user`) + root break-glass |
| `docs/runbooks/ACCESS_AND_ACCOUNTS.md` §5.1, §6 | doc | known gaps | "No SSO / no per-person identity"; single-operator lab (EX-22) |
| `docs/phase9/OWNER_ACTIONS.md` C6 | doc | operator model | "accept the single-operator lab model (EX-22)" |
| `automation/wazuh/multi-node/config/wazuh_dashboard/opensearch_dashboards.yml:6` | config | tenancy setting | `opensearch_security.multitenancy.enabled: false` |
| Live `falcon-central-opensearch-dashboards-1` config | live | central OSD tenancy | plugin default enabled (`Private, Global`) but no multi-user model |
| `bootstrap/60-central-deploy.sh:131-155` | deployment | OpenSearch identities | one admin (break-glass), one dashboard user, writer/backup/healthcheck services |
| `config/opensearch/falcon-eve-template.json:1292` | schema | site attribute | `site_id` is a data label, not an access boundary |
| `grep -rni 'tenant_id|org_id|workspace_id'` (repo) | search | tenant model existence | only Shuffle org IDs in vendored MCT configs; no tenant model in falcon |
| Live Grafana `/api/users` | live | console users | one user (`admin`) |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Repo-wide grep for tenant/org/workspace identifiers | reproduction | prove no tenant model | no tenant scoping code; `SHUFFLE_ORG_ID` in vendored MCT only |
| Wazuh dashboard tenancy setting | reproduction | tenancy boundary | disabled |
| Central OSD tenancy live config | reproduction | tenancy boundary | plugin default enabled, but only service + admin accounts exist; no tenant users |
| Grafana user enumeration (read-only) | reproduction | multi-user model | single admin |
| `docker ps` + index/role inventory | reproduction | shared data plane | all feeds share `falcon-*` indices with role-based (not tenant-based) access |

## Executive Summary

Not applicable: falcon is a single-tenant, single-operator security-monitoring stack by design. There is no tenant/org/workspace model, no membership service, no per-tenant storage namespace, and no multi-user console model. Data from multiple edge sites is deliberately pooled into shared `falcon-*` indices and distinguished only by data labels (`site_id`), which is a routing/analytics attribute, not an isolation boundary. The closest analogue to "tenants" — multiple monitored sites and endpoint agents — has no per-site access separation; that is consistent with the product's single-operator purpose (EX-22) and is recorded as an accepted model in the owner action register.

The prior run also classified this domain N/A with no findings; nothing in the audited commit changes that determination.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Tenant/org/workspace IDs | n/a | tenancy | absent | N/A | no tenant model |
| Membership checks | n/a | tenancy | absent | N/A | single operator |
| DB queries | OpenSearch roles | data access | role-scoped, shared indices | N/A | `falcon_writer`/`falcon_reader` |
| API routes | OpenSearch/Wazuh/enroll | API access | service credentials | N/A | no tenant context |
| Server actions | n/a | — | absent | N/A | no web app |
| Client fetchers | n/a | — | absent | N/A | no SPA |
| RLS | n/a | row security | absent | N/A | no SQL app datastore exposed |
| Storage/file access | `/srv/falcon/**` | files | host-local, OS permissions | N/A | not multi-tenant |
| Realtime channels | n/a | — | absent | N/A | no websockets (SSE in consoles only) |
| Search/export | OpenSearch/Dashboards | query/export | role-scoped | N/A | all users single-operator |
| Admin overrides | OpenSearch admin | break-glass | single admin | N/A | EX-19 |
| Invitations | n/a | — | absent | N/A | no invite flow |

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

- Evidence: `IDENTITY_AND_SECRETS.md` §1 (one interactive account); `ACCESS_AND_ACCOUNTS.md` §5.1 ("No SSO / no per-person identity"); `OWNER_ACTIONS.md` C6 (single-operator EX-22 accepted); grep shows no tenant identifiers.
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

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| MT-001 | Tenant/org/workspace IDs | grep evidence | none (N/A) | — | — | — |
| MT-002 | Membership checks | IDENTITY §1 | single operator | — | — | — |
| MT-003 | DB queries | OpenSearch roles | role-scoped | — | — | — |
| MT-004 | API routes | service credentials | token/password | — | — | — |
| MT-005 | Server actions | n/a | — | — | — | — |
| MT-006 | Client fetchers | n/a | — | — | — | — |
| MT-007 | RLS | n/a | — | — | — | — |
| MT-008 | Storage/file access | host permissions | OS-level | — | — | — |
| MT-009 | Realtime channels | n/a | — | — | — | — |
| MT-010 | Search/export | role-scoped | OpenSearch roles | — | — | — |
| MT-011 | Admin overrides | EX-19 | single admin | — | — | — |
| MT-012 | Invitations | n/a | — | — | — | — |

## Findings

_No findings in this domain._ No tenant boundary exists to attack; the N/A determination is evidence-backed above.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Future multi-operator/multi-tenant evolution on a shared-index, single-admin base | Low (future) | Low | Medium | IDENTITY §1; EVOLUTION_GUIDE note | design tenant scoping before multi-operator rollout |

## Recommendations

### Immediate / Release Blocking

- None.

### This Week

- None.

### This Month

- None.

### Later / Platform Evolution

- If a second operator/customer appears, design per-site/per-operator scoping (OpenSearch document-level security, per-operator identities) before onboarding.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Record the single-tenant assumption in the access matrix | avoids future ambiguity | `docs/security/access_control_matrix.md` (proposed) | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Tenant-scoping design (only when multi-operator) | P3 (future) | @owner | L | product decision |

## Suggested Tests

- None for the current single-tenant model.
- Future: site-scoped read test asserting a site operator cannot query another site's documents.

## Suggested Documentation Updates

- None required now; the proposed consolidated access matrix should state "single-tenant by design (EX-22)".

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is multi-operator/multi-site isolation on the roadmap? | determines when tenant scoping is needed | owner roadmap |

## Prior-Run Comparison

| Prior finding (falcon-20261005-full-main-e267ce1) | Status now | Notes |
|---|---|---|
| (none — domain N/A) | unchanged | re-verified: no tenant model at `08e20d1`; Wazuh dashboard tenancy disabled; single operator |

## Limitations

- "Tenant" was interpreted as a product-level tenant/customer boundary. If the intended interpretation is per-site isolation across the edge fleet, the answer is still "no isolation by design": sites share indices and a single operator — documented as the accepted model, not a defect.
- Cloudflare Access and vendor app roles were not enumerated via API (read-only host checks only).

## Appendix

- Determination commands: `grep -rni 'tenant_id|org_id|workspace_id' --include='*.py' --include='*.yml' ...` (only vendored Shuffle IDs); `docker exec falcon-central-opensearch-dashboards-1 sh -c 'grep -i tenancy /usr/share/opensearch-dashboards/config/opensearch_dashboards.yml'` (plugin default enabled; no multi-user model); Grafana `/api/users` (single admin).

## Findings

_No findings in this domain._
