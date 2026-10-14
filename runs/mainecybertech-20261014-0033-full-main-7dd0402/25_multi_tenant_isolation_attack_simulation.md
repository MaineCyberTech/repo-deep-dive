# Multi-Tenant Isolation Attack Simulation — re-audit verification (main @ 7dd0402)

## Audit Metadata

- Audit name: mainecybertech
- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Repository: `github.com/MaineCyberTech/mainecybertech`
- Branch: `main` (audited ref `origin/main`)
- Commit SHA: `7dd040234e8dfa40dd2d2b6fe1ca7379f2fba097`
- Generated at: 2026-10-14
- Auditor: subagent (full-domain verification re-audit, group 1)
- Area code: MT
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261014-0033-full-main-7dd0402/25_multi_tenant_isolation_attack_simulation.md`
- Scope limitations: code-level simulation only (no destructive actions, no data access). Cross-tenant
  conclusions are based on middleware ordering, mandatory-predicate helpers and the migration chain.

## Scope

Re-verification of the 14 MT findings from the previous full run, plus an isolation sweep of the code added
since. Reviewed: tenant resolution and scope injection (`org-access`, `admin-scope`, `tenant`), API routes
and handlers, response caching, storage paths, SSE/realtime, search/export, admin overrides, notifications,
background jobs, and webhooks.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/middleware/org-access.ts` | Source | Resolve + inject + body-match + param gate | Injects `organization_id` for non-platform admins |
| `apps/api/src/lib/admin-scope.ts` | Source | `allTenants` + `applyOrgScope`/`applyResolvedOrg`/`applyRequestedOrg` | Fail-closed helper |
| `apps/api/src/middleware/cache.ts:169-201` | Source | Scope-aware cache key | `scopeFingerprint` |
| `apps/api/src/routes/{audit,dashboard,search,store/quotes,analytics,notifications,client-portal}.ts` | Source | Previously-fixed surfaces | All scoped |
| `apps/api/src/__tests__/{tenant-scoping-guard,search-tenant-scope,store-tenant-isolation,notifications-sse-scope,admin-scope-resolved-org,client-portal-entitlements-org-pin}.test.ts` | Test | Isolation regression suite | Allowlist still large |
| `supabase/migrations/5302026:799-825` | Migration | `storage_path_org_id` org derivation | UUID prefix contract |

## Verification Performed

- Re-checked every previously-fixed surface at the current commit (audit log scoping, dashboards, cache
  keys, storage paths, SSE scope, search, store intake, client-portal ordering, notification create).
- Enumerated remaining conditional `if (orgId)` filters to size the MT-P2-002 residual.
- Checked the impersonation logging path (durability + alerting) and the Prometheus rules.
- Checked the static tenant-scoping guard's allowlist size against the previous run.

## Executive Summary

Eleven of the 14 findings are verified fixed and three remain partially fixed; no regressions. The
isolation architecture now has a mandatory-predicate helper (`applyResolvedOrg`), a scope-aware response
cache key, a per-org SSE filter, platform-admin gating on store/analytics surfaces, and org-pinned
client-portal entitlements. Storage writers and `storage_path_org_id` agree on the `<org-uuid>/...` contract.

Residuals: conditional `if (orgId)` filters still exist in many modules (safe today only because
`requireOrgAccess` injects the org), the impersonation audit write is still fire-and-forget with an
org-less metric label, and the static isolation guard's allowlist still carries 11 not-yet-remediated
modules.

## Findings

| ID | Sev | Status | Title | Re-verification evidence |
|---|---|---|---|---|
| MT-P1-001 | P1 | verified-fixed | Audit log list/export not org-scoped | `audit.ts:22-50` `applyRequestedOrg` + `applyOrgScope` |
| MT-P1-002 | P1 | verified-fixed | Platform dashboards expose all-tenant aggregates | `dashboard.ts:16-50`; `business-os.ts` apply scope |
| MT-P1-003 | P1 | verified-fixed | Public file-request upload permission union | `file-requests.ts:114-160,197-275` token/org bound |
| MT-P1-004 | P1 | verified-fixed | Cache keys omit tenant scope | `cache.ts:169-201` scopeFingerprint; 7 scope resolvers |
| MT-P2-001 | P2 | verified-fixed | Admin global search unscoped fall-through | `search.ts:107-252`; search-tenant-scope + search-org-pin tests |
| MT-P2-002 | P2 | partially-fixed | By-id org filters conditional / fail open | `applyResolvedOrg` used in findings/qbr/documents/tickets/notifications; conditional `if (orgId)` remains in ai, api-keys, approvals, assets, cab, device-profiles, dmarc-coach, documents (gate-reliant) |
| MT-P2-003 | P2 | verified-fixed | Storage path vs RLS org derivation disagree | `documents.ts:387`; `file-requests.ts:160`; `5302026:799-825` |
| MT-P2-004 | P2 | verified-fixed | SSE channel scoped by user only | `notifications.ts:181-196,231,303`; SSE scope test |
| MT-P2-005 | P2 | partially-fixed | Platform-admin cross-tenant access broad + unalerted | Role split + impersonation log + metric + Prometheus alerts (`prometheus.rules.yml:98-120`). Residual: fire-and-forget write (`org-access.ts:52,197`), metric has no org label |
| MT-P2-006 | P2 | verified-fixed | Platform-wide report generators unguarded | `module-tasks.ts:1062-1124,1300-1345` per-org; `task-producer.ts:76-104` scheduled-only guard |
| MT-P2-007 | P2 | verified-fixed | Client-portal entitlement middleware order | `client-portal.ts:121,145` requireOrgAccess before requireAdmin |
| MT-P2-008 | P2 | verified-fixed | Store intake/analytics readable by any admin | `store/quotes.ts:36-37,216-219`; `analytics.ts:78-106`; isolation test |
| MT-P3-001 | P3 | partially-fixed | No automated cross-tenant isolation suite | Suites added (tenant-scoping-guard, search, store, SSE, admin-scope, client-portal). Residual: allowlist lists 11 not-yet-remediated modules; no per-module org-A→org-B matrix |
| MT-P3-002 | P3 | verified-fixed | Admin notification create arbitrary recipient | `notifications.ts:449-470` `assertSharesActiveOrg` + `assertOrgScopeMatches` + resolved-org stamp; list/SSE use `applyResolvedOrg` |

New findings: none. The isolation sweep of `final/*` reads found no cross-tenant path (requireOrgAccess
pins/injects the org); the missing permission gate is tracked as ACM-P3-008 / SEC-P3-013.

## Attack scenario results (MT-001..MT-012)

| Scenario | Surface | Result at 7dd04023 |
|---|---|---|
| MT-001/002 | Admin reads by id / org traversal | Blocked: org pinning + `applyOrgScope`/`applyRequestedOrg` |
| MT-003 | Store intake / analytics | Blocked: `allTenants` gates |
| MT-004 | Response cache cross-scope | Blocked: scope fingerprint in key |
| MT-005 | Client-portal entitlement write | Blocked: middleware reordered + org pin |
| MT-006 | Storage path traversal | Blocked: writers use `<org-uuid>/`; policy parses same |
| MT-007 | SSE notification cross-org | Blocked: per-row org filter + scoped initial query |
| MT-008 | Notification content injection | Blocked: recipient/org assertions |
| MT-009 | Conditional by-id filters | Partial: gate-reliant in several modules (MT-P2-002) |
| MT-010 | Impersonation trail | Logged + alerting; write is fire-and-forget (MT-P2-005) |
| MT-011 | Background report generators | Scoped per org from DB rows |
| MT-012 | `final/*` module reads | No cross-tenant path; missing `view` permission gate (ACM-P3-008) |

## Recommendations

### This Week

1. Convert the remaining conditional `if (orgId)` handlers to `applyResolvedOrg` (or `loadOwned`) and shrink
   the static guard allowlist (MT-P2-002 / MT-P3-001).

### This Month

2. Make the impersonation audit write durable (await or queue with retry) and add an organization label to
   `portal_impersonation_events_total` so a first-seen actor→org alert is possible (MT-P2-005).
3. Add a per-module org-A→org-B integration matrix for the representative read/write route of each module
   (MT-P3-001).

## Suggested Tests

- Integration: for each module, authenticate as org A and request org B ids → 403/404; list without
  `?organization_id` returns only the caller's org rows.
- Cache: two callers sharing an active org but with different membership sets must not share entries.
- SSE/REST: an org-less notification is not listed for a scoped caller (covered).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which remaining modules are planned for `applyResolvedOrg`? | Sizes MT-P2-002 | Remediation plan |
| Is fire-and-forget acceptable for the impersonation trail? | Audit durability | Platform decision |
