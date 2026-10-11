# Multi-Tenant Isolation Attack Simulation

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `/tmp/opencode/mct-audit-target` (MaineCyberTech portal monorepo)
- Branch: `main`
- Commit SHA: `8d299b8d` (short `8d299b8`)
- Generated at: 2026-10-11
- Auditor: automated domain subagent (prompt 25), static/read-only analysis
- Area code: MT
- Output path (pack): `_domains/25_multi_tenant_isolation_attack_simulation_body.md`
- Scope limitations:
  - **No execution.** No requests were sent; no database, Supabase project, Redis, or lab system was touched. All conclusions are static reasoning over source, migrations, tests, and docs.
  - Deployed `RLS_READS_ENABLED` / `RLS_WRITES_ENABLED` values are deployment secrets (`.github/workflows/deploy-do.yml:615-616`); "which modules are RLS-enforced in production" remains `Unknown`.
  - Dynamic confirmation of the cache-collision finding requires two API clients plus Redis; it is marked as static-only.
  - Prior-run continuity used the committed 20261002 corpus in-repo: `docs/audits/repo-deep-dive/20261002-0344-develop-6286137/25_multi_tenant_isolation_attack_simulation.md` plus this run's `follow_up_register.md`.

## Scope

Reviewed (static evidence):

- Tenant resolution and gates: `requireOrgAccess`, `requireOrgAccessByParam`, `requireAdmin`, `requirePermission`, `assertBodyOrgMatches`, `assertOrgScopeMatches`, `assertSharesActiveOrg`, `resolveAdminTenantScope`, `applyOrgScope`, `applyRequestedOrg`, `assertResourceOrg`, `loadOwned`.
- DB client selection: `getSupabaseAdmin`, `getSupabaseUser`, `getScopedClient`, RLS startup check.
- Every API route module (62 files) for by-id handlers, conditional vs mandatory org predicates, router middleware ordering, and routes registered before the org gate.
- Realtime/SSE (`routes/notifications.ts`), storage paths (`documents`, `file-requests`, `profiles`, `organizations`), exports (`csv.ts`), search (`search.ts`, `search-portal.ts`), cache keys (`middleware/cache.ts`), invitations (`memberships.ts`, `organizations.ts`), admin overrides (`users.ts`), platform-admin paths (`admin.ts`, `audit.ts`, `business-os.ts`, `roles.ts`, `analytics.ts`, `store/*`), webhooks, and worker jobs.
- RLS migrations: membership helpers, `storage_path_org_id`, `notifications`, `profiles`, `tickets` policies; `docs/RLS-coverage-matrix.md`.

Not reviewed here: UI rendering, billing reconciliation (29), notification delivery (30), search indexing internals (31), and the live RLS allow-list values (unknown, see Open Questions).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/middleware/org-access.ts:177-325` | Code | Resolves `req.orgId`/`req.orgScope`, injects `organization_id`, impersonation audit, body/param/share assertions | The gate every other control depends on |
| `apps/api/src/lib/admin-scope.ts:28-99` | Code | `resolveAdminTenantScope` + mandatory `applyOrgScope`/`applyRequestedOrg` predicates | The hardened pattern used by audit/dashboard/exports |
| `apps/api/src/lib/tenant.ts:32-97` | Code | `assertResourceOrg`/`loadOwned` entity→org checks | Mutation paths use this |
| `apps/api/src/middleware/admin.ts:22-64` | Code | Admin gate with org-pinned tightening | Order-dependent (see client-portal finding) |
| `apps/api/src/middleware/cache.ts:154-227` | Code | Response-cache key construction | Key omits resolved scope (new finding) |
| `apps/api/src/routes/notifications.ts:30-394` | Code | SSE stream + REST + admin create | MT-P2-004 fix re-verified |
| `apps/api/src/routes/file-requests.ts:109-448` | Code | Public token upload, storage path, slot claim | MT-P1-003 fix re-verified |
| `apps/api/src/routes/documents.ts:205-1068` | Code | By-id reads, uploads, versions, shares | Storage path aligned; reads conditional |
| `apps/api/src/routes/audit.ts`, `dashboard.ts`, `business-os.ts`, `search.ts` | Code | Former MT-P1/P2 surfaces | All now use the mandatory predicate |
| `apps/api/src/routes/store/quotes.ts:165-440` | Code | store_quotes fixed; quote-requests/leads/proposal-drafts unscoped | New finding evidence |
| `apps/api/src/routes/analytics.ts:26-93` | Code | Platform-wide store analytics to any admin | New finding evidence |
| `apps/api/src/routes/client-portal.ts:113-165` | Code | Entitlement routes with inverted middleware order | New finding evidence |
| `apps/api/src/__tests__/tenant-scoping-guard.test.ts:46-191` | Test | QW-3 static unscoped-handler guard | Allowlist ~58 entries weakens it |
| `apps/api/src/__tests__/{search-tenant-scope,store-tenant-isolation,notifications-sse-scope,middleware-org-access,tenant}.test.ts` | Test | Behavioral cross-tenant coverage | Partial suite (MT-P3-001) |
| `supabase/migrations/5302026_..._v3.sql:799-825,997-1035,2326-2353` | Migration | `storage_path_org_id`, profiles/tickets RLS, documents bucket policies | Path contract matches writers |
| `apps/worker/src/tasks/retention.ts:92-116`, `module-tasks.ts:992-1124,1287-1350` | Code | Service-role global report/purge jobs | MT-P2-006 residual |
| `infra/digitalocean/prometheus.rules.yml:45-56` | Config | Cross-tenant (impersonation) volume alert | MT-P2-005 partial fix |
| `docs/audits/repo-deep-dive/20261002-0344-develop-6286137/25_...md` | Prior report | Original MT finding text (in-repo) | Basis for verification duty |

## Verification Performed

| Command / check | Result |
|---|---|
| `git log --oneline -5` in the target | HEAD = `8d299b8d Merge PR #168`; clean read-only worktree |
| `grep -n "MT-" runs/mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md` | 10 MT rows recovered (3 P1 verified-fixed, 6 P2, 1 P3) |
| In-repo prior report `docs/audits/.../20261002-0344/25_...md` read in full | Recovered original MT-P1/P2/P3 evidence and intent |
| `grep -rn "applyOrgScope\|resolveAdminTenantScope\|applyRequestedOrg" apps/api/src` | 11 route files now use the mandatory predicate (audit, dashboard, business-os, search, findings, tickets, projects, approvals, assets, proposals, domain-monitors, edu-automation, store/*) |
| `grep -n "CROSS_TENANT_KEYS" apps/api/src/lib/roles.ts` | `['super_admin','admin']` — cross-tenant reach is role-key based (MT-P2-005 residual) |
| `git show 1fb034bd` (PR #145) | SSE org assertion (`notificationInScope`, scoped initial query) present; notifications.ts has no later commits |
| `grep -n "notificationInScope" apps/api/src/routes/notifications.ts` | Lines 36-44 (definition), 120/135 (handlers), 154-155 (initial query) |
| `grep -n "storagePath = " apps/api/src/routes/documents.ts apps/api/src/routes/file-requests.ts` | `documents.ts:352` and `file-requests.ts:156,408` all start with the raw org UUID (MT-P2-003 verified) |
| Python scan: unscoped `:param` handlers per route file (heuristic) | After treating `loadOwned` as a scope marker: only intentionally public/token or user-scoped handlers remain (documents `/shares/:token`, file-requests `/public/:token`, notifications `/:id/read|delete`, profiles self, roles global, users self/admin, webhook dead-letters via `loadDeadLetterOwned`) |
| Python scan: handlers registered before `router.use(requireOrgAccess)` | Only intended public routes: `batch /status/public`, `documents /shares/:token`, `file-requests /public/:token(/upload)`, `status-page /public/:orgId` |
| Python scan: route files using `getSupabaseAdmin` with no org-scope marker anywhere | `admin.ts`, `analytics.ts`, `auth.ts`, `bulk.ts` (router-gated), `health.ts`, `public.ts`, `roles.ts`, `webhooks.ts`, `store/visual-assets.ts` — confirmed global/platform/user-scoped except analytics (finding) |
| `grep -n "requireAdmin, requireOrgAccess" apps/api/src/routes/*.ts` | Inverted order only in `client-portal.ts:113,137`; audit/bulk are correct (`requireOrgAccess, requireAdmin`) |
| `grep -n "applyOrgScope\|scope.allTenants" apps/api/src/routes/business-os.ts` | `/snapshots` gated on `allTenants`; all aggregates scoped |
| `grep -n "organization_id" supabase/migrations/5302408_store_tenant_scoping.sql` | store_quotes/catalog/promotions got `organization_id`; `store_quote_requests`/`store_leads`/`store_proposal_drafts` did not |
| `grep -n "buildCacheKey\|:org=\|:user=" apps/api/src/middleware/cache.ts` | Key = path+query+`:org=<req.orgId>` (or `:user=<uid>` only when org absent) |

## Executive Summary

The isolation posture has improved materially since the original MT report (`6286137`, 2026-10-02). All three former P1s are fixed and re-verified at `8d299b8d`: audit list/export are tenant-pinned (`applyOrgScope`/`applyRequestedOrg`), dashboard/business-os aggregates are scoped to the caller's approved orgs (platform-wide views require `is_super_admin` + a cross-tenant role), and the public file-request upload derives its org from the token row end to end. Search fails closed, storage paths match the `storage_path_org_id` RLS contract, and the SSE notification stream now asserts the resolved org (PR #145, unit-tested). The `loadOwned`/`assertResourceOrg` entity→org pattern covers most mutation paths, and a static "unscoped `:param`" guard plus four behavioral cross-tenant suites now exist.

Three residual gaps matter:

1. **Cache keys omit the resolved tenant scope** (`middleware/cache.ts:154-168`). Responses that vary with the caller's membership set — the organizations list, dashboard counts, business-os summaries/org-health — are cached under `:org=<activeOrg>` only. Within the 30-60s TTL, an all-tenant response produced for a cross-tenant/platform admin can be served to a regular member of that org, and two admins with different membership sets collide. This is the only new P1.
2. **Conditional `if (orgId)` by-id filters remain the dominant idiom** (findings, qbr, tickets, documents reads, and others) and are safe only because `requireOrgAccess` injects the org. The static guard allowlists ~58 files, so the footgun is not enforced. A concrete residual is `client-portal.ts:113,137`, where `requireAdmin` runs *before* `requireOrgAccess` and therefore skips the org-pinned admin check, letting a tenant `admin` read/write another tenant's entitlements (P2).
3. **Platform-wide admin surfaces are inconsistent.** `store/quotes.ts:200-232,350-390` and `analytics.ts:64-91` expose global intake PII, the sales pipeline, and visitor IP analytics to any tenant admin with no `allTenants` gate, while the analogous `store_quotes` and `business_os_snapshots` paths *are* gated (P2).

Cross-tenant platform-admin access is now logged (`impersonation_log`), metered and volume-alerted, but the log write is fire-and-forget and `admin` remains a blanket cross-tenant key (MT-P2-005 partially fixed). Background report/purge jobs still accept payload overrides with no tenant guard, though no user-facing enqueue path was found (MT-P2-006 still open, latent).

**Domain score: 4/5** — functional and now meaningfully hardened at the application layer, with a small number of concrete residuals and RLS still an opt-in backstop.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Org scope resolution | `middleware/org-access.ts` | Resolve tenant, inject org, audit impersonation | Implemented | Low | Injected org is what makes conditional filters safe |
| Mandatory predicates | `lib/admin-scope.ts` `applyOrgScope`/`applyRequestedOrg` | Fail-closed org predicates | Implemented, partial adoption | Low | Adopted by audit/dashboard/business-os/search/exports |
| Entity→org helpers | `lib/tenant.ts` `loadOwned`/`assertResourceOrg` | Verify row org before use | Implemented, broad adoption | Low | Used by mutations across modules |
| SSE notifications | `routes/notifications.ts:36-156` | Realtime stream | Org-asserted + tested | Low | MT-P2-004 verified-fixed |
| Storage paths | `documents.ts:352`, `file-requests.ts:156,408` | Object key contract | Aligned to `<orgId>/…` | Low | MT-P2-003 verified-fixed |
| Response cache | `middleware/cache.ts:154-168` | GET response cache | Org-keyed only | High | New P1 finding |
| By-id reads | findings/qbr/tickets/documents/approvals | Conditional `if (orgId)` | Works via injection | Medium | MT-P2-002 partially fixed |
| Client-portal entitlements | `routes/client-portal.ts:113-165` | Per-tenant module provisioning | Middleware order inverted | Medium | New P2 finding |
| Store intake | `routes/store/quotes.ts:200-390` | Quote requests, leads, drafts | No tenant/allTenants gate | Medium | New P2 finding |
| Analytics | `routes/analytics.ts:64-91` | Store event list/summary | No tenant/allTenants gate | Medium | Global table, IPs exposed |
| Admin gate | `middleware/admin.ts:22-64` | Admin + pinned-org check | Order-dependent | Medium | See client-portal finding |
| Cross-tenant roles | `lib/roles.ts:27` | `admin`/`super_admin` keys | Role-key based | Medium | Logged + alerted, broad by design |
| Worker jobs | `worker/src/tasks/*` | Global report/purge | Service role, payload overrides | Medium (latent) | MT-P2-006 still open |
| RLS backstop | `services/supabase.ts:198-226` | `getScopedClient` selector | Allow-list (deployment secret) | Medium | Default remains service role |
| Regression tests | `__tests__/tenant-scoping-guard`, search/store/SSE suites | Isolation tests | Partial | Medium | Guard allowlist stale |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Tenant/org/workspace IDs | 4 | `org-access.ts:177-325`; `orgScope` on every request | Conditional reads depend on injection | Migrate to mandatory predicates |
| Membership checks | 4 | `checkOrgAccess`, `assertSharesActiveOrg`, `assertOrgScopeMatches` | `admin` key is blanket cross-tenant | Split tiers / time-box grants |
| DB queries | 4 | `applyOrgScope` adoption; `loadOwned` | Conditional `if (orgId)` still dominant | Unconditional predicate helper |
| API routes | 4 | 62 route files scanned; only intended public routes pre-gate | Inverted middleware order in client-portal | Reorder + test |
| Server actions | 3 | Web is API-only (`apps/web/lib/api.ts`, `module-actions.ts`) | None in-repo | None |
| Client fetchers | 4 | SDK sends `X-Active-Org`; API re-validates membership | None beyond conditional filters | None |
| RLS | 3 | `storage_path_org_id` + bucket policies aligned; profiles/tickets/notifications member-scoped | Allow-list is deployment secret; default service role | Publish non-secret readiness manifest |
| Storage/file access | 4 | Path contract fixed; token-bound uploads; bucket pinned | None found | Add path-contract unit test |
| Realtime channels | 4 | `notificationInScope` + scoped initial query + tests | REST list not org-filtered (P3) | Align REST with stream |
| Search/export | 4 | `search.ts` fails closed; exports use `applyOrgScope`; CSV formula guard | None found | Keep as reference |
| Admin overrides | 3 | `users.ts` uses `assertOrgScopeMatches`; impersonation logged/alerted | Fire-and-forget log; broad roles | Durable audit + first-seen alert |
| Invitations | 4 | `memberships.ts` org-gated; invite resolves body org through `requireOrgAccess` | `admin` can invite cross-tenant (audited) | Policy decision |

## Detailed Review

### Item: Tenant resolution and the conditional-filter contract

- Evidence: `apps/api/src/middleware/org-access.ts:177-325`; `apps/api/src/routes/findings.ts:80-82`; `apps/api/src/routes/qbr.ts:25-50`.
- What it does: resolves the org from query → body → `X-Active-Org` → cookie; verifies an approved membership; grants cross-tenant access to `admin`/`super_admin` keys (audited); injects `organization_id` into `req.query` and sets `req.orgId` when no explicit org was given.
- Current controls: injection + `assertBodyOrgMatches` + mandatory predicates on the hardened surfaces.
- Missing controls: by-id/list reads still use `if (orgId)` in many files; a route mounted without `requireOrgAccess` (or reordered middleware) fails open.
- Risks: MT-P2-002 residual; see the client-portal ordering finding.
- Recommended improvement: `tenantQuery(req, table)` helper that throws when a non-platform caller has no resolved org; shrink the static guard allowlist.

### Item: Platform-admin cross-tenant access (MT-P2-005)

- Evidence: `apps/api/src/lib/roles.ts:27`; `apps/api/src/services/impersonation.ts:28-47`; `apps/api/src/lib/metrics.ts:253-255`; `infra/digitalocean/prometheus.rules.yml:45-56`; `apps/api/src/routes/audit.ts:122-153`.
- What it does: any approved membership with `admin`/`super_admin` may enter any tenant; each entry writes `impersonation_log` (reason, IP, UA) and increments a metric; a Prometheus rule alerts above 0.5 events/s and points at the review endpoint.
- Missing controls: log write is `void` (best-effort); volume threshold means a single cross-tenant read never alerts; `admin` vs `super_admin` reach is inconsistent across gates (client-portal finding).
- Recommended improvement: durable/queued audit writes, first-seen actor→org alert, and one explicit policy for `admin` cross-tenant reach.

### Item: Store intake and analytics (new)

- Evidence: `apps/api/src/routes/store/quotes.ts:200-232,350-390`; `apps/api/src/routes/analytics.ts:64-91`; `supabase/migrations/5302114_store_conversion_modules.sql:6-17`; `supabase/migrations/5302408_store_tenant_scoping.sql:43-52`; `apps/api/src/routes/business-os.ts:264-266`.
- What it does: exposes global `store_quote_requests` (customer PII), `store_leads`, `store_proposal_drafts`, and `store_analytics_events` (anonymous_id, ip_address, user_agent) to any `admin` with no tenant scope, while the sibling `store_quotes` and `business_os_snapshots` surfaces are gated on `allTenants`.
- Recommended improvement: gate on `resolveAdminTenantScope().allTenants`, or add `organization_id` + RLS to the intake tables and scope by it.

### Item: Response cache scope (new)

- Evidence: `apps/api/src/middleware/cache.ts:154-168`; `apps/api/src/routes/organizations.ts:153-182`; `apps/api/src/routes/dashboard.ts:16-50`; `apps/api/src/routes/business-os.ts:35-143,193-257`.
- What it does: keys authenticated responses by `:org=<req.orgId>`; the response body is computed from `resolveAdminTenantScope(req)` (which depends on the caller's memberships and super-admin flag), so two callers with the same active org but different scopes share an entry.
- Recommended improvement: include `allTenants`/sorted `orgIds` (or a scope hash) in the key; never let an org-keyed entry serve an all-tenants body; unit-test two membership sets with the same active org.

### Item: Background jobs (MT-P2-006)

- Evidence: `apps/worker/src/tasks/retention.ts:92-116`; `apps/worker/src/tasks/module-tasks.ts:992-1124,1287-1350`; `apps/api/src/lib/task-producer.ts:76-104`.
- What it does: service-role global report/purge jobs; per-row `organization_id` fan-out is correct; retention merges caller payload over defaults with a numeric sanity guard but no tenant guard.
- Missing controls: no payload tenant validation at the registry boundary; no user-facing enqueue path found (notify, webhook dispatcher, webhook retry only).
- Recommended improvement: validate org fields per task type; keep destructive tasks scheduled-only.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| MT-001 | Tenant/org/workspace IDs | `org-access.ts:177-325` | Resolved + injected; membership verified | Conditional reads rely on injection | P2 | Mandatory predicate helper |
| MT-002 | Membership checks | `org-access.ts:22-64`; `tenant.ts:66-97` | Approved membership + entity→org checks | Blanket `admin` cross-tenant | P2 | Split role tiers |
| MT-003 | DB queries | `admin-scope.ts:70-99`; `loadOwned` | Mandatory predicates on hardened surfaces | `if (orgId)` elsewhere | P2 | Migrate + lint gate |
| MT-004 | API routes | app route scan; `client-portal.ts:113,137` | Per-router middleware | Inverted order bypasses pinned admin check | P2 | Reorder middleware |
| MT-005 | Server actions | `apps/web/lib/api.ts`, `module-actions.ts` | Web is an API client only | None in-repo | — | None |
| MT-006 | Client fetchers | `packages/sdk/src/client.ts:155-168` | `X-Active-Org` re-validated server-side | Cookie is client-settable (re-validated) | P3 | None |
| MT-007 | RLS | `services/supabase.ts:198-226`; storage policies | Aligned storage contract; member policies | Allow-list unknown/default bypass | P2 | Publish readiness manifest |
| MT-008 | Storage/file access | `documents.ts:352`; `file-requests.ts:156` | Org-UUID-prefixed paths; token-bound uploads | None found | — | Add contract test |
| MT-009 | Realtime channels | `notifications.ts:36-156` | Org assertion + scoped initial query | REST list not org-filtered | P3 | Align REST |
| MT-010 | Search/export | `search.ts:77-163`; export predicates | Fail-closed, mandatory predicates | None found | — | Keep as reference |
| MT-011 | Admin overrides | `users.ts:390-568`; `impersonation.ts` | `assertOrgScopeMatches`; impersonation logged/alerted | Fire-and-forget audit; broad keys | P2 | Durable audit + alert |
| MT-012 | Invitations | `memberships.ts:62-121`; `organizations.ts:59-151` | Org gate + body-org assertion | `admin` can invite cross-tenant (audited) | P3 | Policy decision |

## Findings

IDs are assigned by the aggregator; titles below match `25_multi_tenant_isolation_attack_simulation.json`.

### Verified-fixed (re-verified at 8d299b8d)

- **Audit log list and export are not org-scoped by default** (P1, verified-fixed) — `audit.ts:22,34-35,77-78,125,171`; `admin-scope.ts:70-99`.
- **Platform dashboards expose all-tenant aggregates to any single-org admin** (P1, verified-fixed) — `dashboard.ts:16-50`; `business-os.ts:24-33,41-94,148-201,264-266`.
- **Public file-request upload authorizes with a permission unioned across all orgs** (P1, verified-fixed) — `file-requests.ts:109-156,184-218,408`.
- **Admin global search lists all organizations and can fall through unscoped** (P2, verified-fixed) — `search.ts:77-163`; `search-tenant-scope.test.ts`.
- **Storage writer path and RLS org-derivation disagree** (P2, verified-fixed) — `documents.ts:352`; `file-requests.ts:156,408`; migration `5302026:799-825,2326-2353`.
- **Realtime/SSE notification channel is scoped by user only, with no org assertion** (P2, verified-fixed) — `notifications.ts:36-44,120,135,154-155`; `notifications-sse-scope.test.ts`; PR #145 (`1fb034bd`).

### Partially-fixed / still-open

- **By-id org filters are conditional, so they fail open if the org gate is not reached** (P2, partially-fixed) — `findings.ts:80-82,108-110,137-139`; `qbr.ts:25-50,214-245`; `documents.ts:218-250`; `tickets.ts:104-113`; guard allowlist `tenant-scoping-guard.test.ts:46-111`.
- **Platform-admin cross-tenant access is role-key based, broad, and unalerted** (P2, partially-fixed) — `roles.ts:27`; `impersonation.ts:28-47`; `prometheus.rules.yml:45-56`; `org-access.ts:52,197`; `tenant.ts:46`.
- **Platform-wide report generators run as service role with no tenant guard on scope inputs** (P2, still-open) — `retention.ts:92-116`; `module-tasks.ts:992-1124,1287-1350`; `task-producer.ts:76-104`.
- **No automated cross-tenant isolation regression suite for application-layer scoping** (P3, partially-fixed) — `tenant-scoping-guard.test.ts:140-191`; search/store/SSE suites.

### New (open)

- **Response cache keys omit the caller's tenant scope, so all-tenant responses can be served to single-org members** (P1, open) — `cache.ts:154-168`; `organizations.ts:169-182`; `dashboard.ts:21-50`; `business-os.ts:41-94`; `admin-scope.ts:55-57`.
  - Endpoint/data path: `GET /api/v1/organizations`, `GET /api/v1/dashboard/summary`, `GET /api/v1/business-os/{summary,org-health,recent-activity}` → cached by `:org=<activeOrg>` → Redis/memory.
- **Client-portal entitlement routes order requireAdmin before requireOrgAccess, bypassing the org-pinned admin check** (P2, open) — `client-portal.ts:113,137`; `admin.ts:46-58`; `org-access.ts:22,234-247`; correct order in `audit.ts:22`/`bulk.ts:11`.
  - Endpoint/data path: `GET|PUT /api/v1/client-portal/entitlements?organization_id=<victim>` → `client_portal_entitlements` upsert.
- **Platform-wide store intake and analytics endpoints are readable by any tenant admin with no cross-tenant gate** (P2, open) — `store/quotes.ts:200-232,350-390`; `analytics.ts:64-91`; global tables per migrations `5302114:6-17`, `5302115:6-28`, `5302106:1-25`; contrast `store/quotes.ts:165-197` and `business-os.ts:264-266`.
- **Admin notification create accepts an arbitrary recipient and org-less rows bypass the SSE scope assertion** (P3, open) — `notifications.ts:292-320,194-218`; `notify.ts:90-105`; contrast `notifications.ts:36-44`.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Cross-tenant org list/aggregates served from cache | P1 | Medium (needs shared active org + TTL window) | Medium-High | Cache finding | Scope-aware cache key |
| Conditional by-id filter regression | P2 | Medium | High (service-role default) | MT-P2-002 | Mandatory predicates + shrink guard allowlist |
| Cross-tenant entitlement write via middleware order | P2 | Medium | Medium | client-portal finding | Reorder `requireOrgAccess, requireAdmin` |
| Platform-wide intake PII / analytics to tenant admins | P2 | High (any admin can call) | Medium | store/analytics finding | `allTenants` gate |
| Cross-tenant traversal by `admin` key | P2 | Medium | High | MT-P2-005 | Role split; durable audit; first-seen alert |
| Latent payload-driven global jobs | P2 | Low (no user trigger today) | High | MT-P2-006 | Validate payloads at registry |
| Notification content injection across tenants | P3 | Low | Low | notifications finding | Recipient shared-org check |

## Recommendations

### Immediate / Release Blocking

1. Include the resolved tenant scope in `buildCacheKey` (`cache.ts:154-168`) and add a two-membership-sets unit test. (P1)
2. Reorder `client-portal.ts:113,137` to `requireOrgAccess, requireAdmin` (or assert the pinned org in-handler) and add a cross-tenant 403 test. (P2)

### This Week

3. Gate `store/quote-requests`, `store/leads`, `store/proposal-drafts` and `analytics` list/summary on `resolveAdminTenantScope().allTenants` (or add org columns + RLS). (P2)
4. Add a `tenantQuery`-style mandatory predicate (or `assertResourceOrg`) to the remaining conditional by-id reads and reduce `KNOWN_UNSCOPED` to genuinely global modules. (P2)
5. Make `logImpersonation` durable for cross-tenant requests (await or queue with retry) and add a first-seen actor→org alert. (P2)

### This Month

6. Decide and document one policy for `admin` cross-tenant reach; align `requireAdmin` ordering semantics everywhere. (P2)
7. Validate worker task payloads at the registry boundary; keep destructive tasks scheduled-only. (P2)
8. Extend the cross-tenant regression suite per route module (org A → org B ids). (P3)
9. Publish a non-secret RLS module-readiness manifest (which modules are in the allow-lists per environment). (P2)

### Later / Platform Evolution

10. Replace role-key cross-tenant trust with explicit, time-boxed platform grants and break-glass review.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Scope-aware cache key | Closes the new P1 | `middleware/cache.ts` | Two callers, same org, different scopes → different entries |
| Swap client-portal middleware order | Restores the pinned admin check | `routes/client-portal.ts` | Tenant admin of A → 403 on org B entitlements |
| `allTenants` gate on store intake/analytics | Removes platform PII exposure | `routes/store/quotes.ts`, `routes/analytics.ts` | Single-org admin gets 403/empty |
| Shared-org check on notification create | Stops cross-tenant content injection | `routes/notifications.ts` | Org A admin cannot notify org B user |
| Trim `KNOWN_UNSCOPED` | Gives the static guard teeth | `__tests__/tenant-scoping-guard.test.ts` | Removing a remediated file keeps tests green |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Scope-aware cache key | P1 | API principal engineer | S | None |
| Client-portal middleware order | P2 | API principal engineer | S | None |
| Platform-wide intake/analytics gate | P2 | API platform / product | S-M | Product decision on store ownership |
| Mandatory predicates for by-id reads | P2 | API team | M | `req.orgId` contract |
| Durable impersonation audit + first-seen alert | P2 | Platform lead / observability | M | Alert routing |
| Worker payload tenant validation | P2 | Worker/queue owner | S-M | Task registry contract |
| Per-route cross-tenant regression suite | P3 | QA/API | M | Two-org seed data |
| RLS readiness manifest | P2 | DB owner + platform | S | Deployment env access |

## Suggested Tests

- **Unit:** cache key includes `allTenants`/`orgIds` hash; `storage_path_org_id('<uuid>/x')` returns the UUID; `notificationInScope` cases (already present).
- **Integration:** per route module, authenticate as org A and request org B ids → 403/404 (`tickets`, `documents`, `findings`, `qbr`, `approvals`, `api-keys`, `client-portal` entitlements); list endpoints without `?organization_id` return only org A rows.
- **Integration (platform surfaces):** single-org admin → `store/quote-requests`, `store/leads`, `store/proposal-drafts`, `analytics` are 403/empty; super_admin+cross-tenant role succeeds.
- **Cache:** two users with the same active org but different membership sets must not share a cache entry; an allTenants response must not be served to a non-allTenants caller.
- **SSE/REST consistency:** a notification created with no org is not listed for a caller with a resolved org (or is scoped on insert).
- **CI:** keep the static guard, but fail on new `if (orgId)` around `organization_id` in files removed from the allowlist; assert every router handling tenant tables mounts `requireOrgAccess` or documents why not.
- **Manual (assumed):** confirm deployed `RLS_READS_ENABLED`/`RLS_WRITES_ENABLED` values; run one cross-tenant probe in staging.

## Suggested Documentation Updates

- `docs/TENANT-ISOLATION.md` (new): end-to-end model (resolution → injection → predicate → cache → storage → realtime) plus the "no `requireOrgAccess` ⇒ no `req.orgId` ⇒ conditional `if (orgId)` is unsafe" rule.
- `docs/RLS-rollout.md`: non-secret per-module readiness manifest and the `<orgId>/...` storage-path contract.
- `docs/API_ENDPOINT_INVENTORY.md`: mark platform-wide admin endpoints (`analytics`, store intake) as platform-staff-only or tenant-scoped.
- `apps/api/src/middleware/cache.ts` header: document the cache-key scope contract.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which modules are in `RLS_READS_ENABLED`/`RLS_WRITES_ENABLED` per environment? | Determines whether RLS is an active backstop for the residuals | Deployment secret values or a manifest |
| Is a tenant-level `admin` intended to be cross-tenant everywhere? | Bounds MT-P2-005 and the client-portal finding | Product/role taxonomy decision |
| Are `store/quote-requests`, `leads`, `proposal-drafts`, `analytics` intended for platform staff only? | Determines the correct fix (gate vs org column) | Product ownership decision |
| Does any future path let callers enqueue tasks with payloads? | Bounds MT-P2-006 | `lib/task-producer.ts` call sites + queue policy |
| Was the previous register's MT-P2-002 scoped to reads only, or writes too? | Verification completeness | Prior register intent (titles only were carried) |

## Appendix

### A1. Attack surface inventory (current commit)

- **Org gates:** `requireOrgAccess` (most routers), `requireOrgAccessByParam` (organizations, domains), none (admin/analytics/roles/public/webhooks/auth/health/store sub-routers use per-route gates).
- **Mandatory-predicate surfaces:** audit, dashboard, business-os, search, findings/tickets/projects/approvals/assets/domain-monitors exports, store admin lists.
- **Conditional-predicate surfaces:** findings, qbr, tickets, documents, approvals, api-keys, billing, cab, device-profiles, dmarc-coach, edu-automation, governance, webhook-management lists.
- **Entity→org (`loadOwned`/`assertResourceOrg`) surfaces:** approvals, memberships, findings, ai, api-keys, cab, client-onboarding, compliance, device-profiles, domain-monitors, network-diagrams, proposals, security-ops, security-suite, staging, training-hub, webhook-management.
- **Public/token surfaces:** `documents /shares/:token`, `file-requests /public/:token(/upload)`, `status-page /public/:orgId` (opt-in, allowlisted projection), `batch /status/public`.
- **Platform-wide admin surfaces (no tenant gate):** `admin /organizations` (is_super_admin), `analytics GET /` + `/summary`, `store/quote-requests|leads|proposal-drafts`, `roles` catalog.
- **Realtime:** SSE `GET /notifications/stream` (org-asserted); no direct browser Supabase realtime usage found.

### A2. Tenant isolation checklist

| Check | Status | Evidence |
|---|---|---|
| Cross-org by-id reads denied | Partial (mandatory on hardened; conditional elsewhere) | MT-P2-002 finding |
| Cross-org writes denied | Yes via `loadOwned`/`assertOrgScopeMatches` | `tenant.ts:66-97`, `users.ts:390-568` |
| Body/query org mismatch rejected | Yes | `org-access.ts:162-175` |
| Exports never default to all tenants | Yes | `audit.ts:34-35,77-78`; findings/tickets/approvals exports |
| Platform-wide reads require genuine cross-tenant admin | Partial | dashboard/audit/business-os yes; analytics/store intake no |
| SSE scoped to resolved org | Yes | `notifications.ts:36-156` |
| Storage paths derive org for RLS | Yes | `documents.ts:352`; `file-requests.ts:156` |
| Cache keys isolate tenant scope | No | cache finding |
| Cross-tenant access audited + alerted | Partial (best-effort log, volume alert) | `impersonation.ts:28-47`; rules `:45-56` |
| Cross-tenant regression tests in CI | Partial | guard + 4 suites; stale allowlist |

### A3. Scenario results (MT-001..MT-012)

| Scenario | Simulated attacker action | Result at 8d299b8d |
|---|---|---|
| MT-001 tenant IDs | Supply `?organization_id=<other>` | 403 unless cross-tenant key; audited |
| MT-002 membership | Org B id with org A membership | Denied for non-cross-tenant; `admin` key allowed (audited) |
| MT-003 DB queries | Guess org B resource id on hardened routes | 404 via predicate/`loadOwned`; conditional routes rely on injection |
| MT-004 API routes | Call admin routes with org B | Dashboard/audit scoped; client-portal entitlements bypass (finding) |
| MT-005 server actions | Craft form `organizationId` | API re-validates; no bypass |
| MT-006 client fetchers | Set `X-Active-Org` / cookie to org B | Membership re-checked server-side |
| MT-007 RLS | Query with anon key | Unknown deployed allow-list; policies member-scoped for key tables |
| MT-008 storage | Upload into org B prefix | Paths derived server-side; token-bound |
| MT-009 realtime | Subscribe to another user's channel | Filter user_id + org assertion drop |
| MT-010 search/export | Search org B substring | No rows; allTenants audited |
| MT-011 admin overrides | Grant permission in org B | `assertOrgScopeMatches` blocks non-platform |
| MT-012 invitations | Invite user into org B | Org gate + audited impersonation |

### A4. Cross-references (not duplicated here)

- Domain 06 (`SEC-*`): service-role default client, anon grants, MSP role trust.
- Domain 24 (`ACM-*`): role catalog and permission matrix.
- Domain 26 (`ADMIN-*`): admin console abuse cases (client-portal ordering is cross-referenced there).
- Domain 37 (`RLS-*`): policy-level review and `storage_path_org_id` trust.
- Domain 45 (`CHAIN-*`): low-trust MSP cross-tenant pivot composition.
