# 24_access_control_matrix_audit — Prompt 24 - Access Control Matrix Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `24_access_control_matrix_audit.md` (area ACM, prompt)

## Verification Performed

# Access Control Matrix Audit

## Audit Metadata

- Audit name: repo-deep-dive (full hardening rerun)
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: mainecybertech portal monorepo
- Branch: `main`
- Commit SHA: `8d299b8d` ("Merge PR #168: promote develop to main (metrics scrape fixes + register sync)")
- Generated at: 2026-10-11
- Auditor: domain subagent (prompt 24, area ACM)
- Area code: ACM
- Output path: `docs/audits/repo-deep-dive/{run}/24_access_control_matrix_audit.md`
- Companion artifacts: role inventory, permission inventory, route access matrix and sensitive action matrix are embedded in this report (the run instructions limit this domain to two output files).
- Scope limitations:
  - Static review only: no hosted Supabase project, no running API, no database. RLS behavior under `auth.uid()` and the deployed `RLS_*_ENABLED` allow-list are `Unknown`/`not reproducible` from the repository alone.
  - The seeded catalog was read from migrations; the deployed catalog could differ (`Unknown`).
  - No changes to ACM-relevant files exist between the previous run's commit `9c0b88c` and `8d299b8d` (`git log 9c0b88c..8d299b8d -- <files>` is empty), so previous verifications were re-checked in place and re-bound to `8d299b8d`.

## Scope

Reviewed at `8d299b8d`:

- Roles: `apps/api/src/lib/roles.ts`, `apps/web/lib/roles.ts`, role catalog migrations (`5302026`, `5302128`).
- Permissions: `apps/api/src/lib/permissions.ts`, `apps/api/src/middleware/permissions.ts`, catalog/grants migrations (`5302118`, `5302128`, `5302131`, `5302424`, `5302426`, `5302423`).
- Org/tenant/workspace membership: `middleware/org-access.ts`, `lib/tenant.ts`, `lib/admin-scope.ts`, `middleware/admin.ts`, `routes/memberships.ts`, `routes/organizations.ts`, `routes/users.ts`.
- Project/ticket/document/billing/API-key/webhook permission: all 60 files in `apps/api/src/routes/**` (442 route definitions) plus the 182 `requirePermission` call sites.
- Admin console: `routes/{admin,audit,analytics,business-os,dashboard,roles,users,bulk,search}.ts`; web `lib/auth/admin.ts`, `lib/auth/permissions.ts`, `components/{HasPermission,RouteGuard}.tsx`.
- Public/authenticated/internal routes: `apps/api/src/app.ts` mount table; `routes/{auth,public,docs,health,webhooks}.ts`; inline public blocks in `file-requests.ts`, `status-page.ts`, `batch.ts`, `store/*`, `analytics.ts`.
- Server actions / client-side hiding: `apps/web/app/(admin|portal)/**/actions.ts` sample; `apps/web/lib/auth/*`.
- API endpoints: route matrix (Appendix A).
- Background jobs: `apps/worker/src/tasks/*` identity model (service role, no user identity).
- DB helpers: `is_super_admin`, `is_org_member`, `is_org_approved_member`, `user_has_role`, `user_has_permission`, `can_read_document`, `approve_project_task`/`add_project_task_comment`.
- Middleware: `auth.ts`, `admin.ts`, `permissions.ts`, `org-access.ts`, `api-key.ts`, `entitlement.ts`, `csrf.ts`, `rate-limit.ts`.
- Audit logs: `services/audit.ts`, `services/impersonation.ts`, `routes/audit.ts`.
- Authz tests: `apps/api/src/__tests__` (133 files; 18 files assert 403/FORBIDDEN).

Not reviewed / out of scope: live RLS behavior, deployed env config, non-API clients (Terraform/CI covered by sibling domains), and the worker's task-level access control beyond its identity model.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/api/src/lib/roles.ts` | Source | Trust tiers | `CROSS_TENANT_KEYS` (2) vs `ELEVATED_TENANT_KEYS` (6); `PLATFORM_ADMIN_KEYS` deprecated |
| `apps/api/src/lib/permissions.ts` | Source | Effective permissions | `ADMIN_BYPASS_KEYS` (2); resolver with overrides; super-admin bypass at :62 |
| `apps/api/src/middleware/permissions.ts` | Source | Route enforcement | `requirePermission(module,action)`; org-scoped resolution; admin fallback |
| `apps/api/src/middleware/admin.ts` | Source | Admin gate | Org-pinned admin semantics (ADMIN-P1-001 fix) |
| `apps/api/src/middleware/org-access.ts` | Source | Tenant gate | `requireOrgAccess`, `requireOrgAccessByParam`, `assertOrgScopeMatches`, `assertSharesActiveOrg` |
| `apps/api/src/lib/tenant.ts` | Source | Row-level checks | `assertResourceOrg` (404 semantics), `loadOwned` |
| `apps/api/src/services/supabase.ts` | Source | DB client selection | service-role default; `getScopedClient` allow-list + platform-admin fallback |
| `apps/api/src/lib/rls-startup-check.ts` | Source | Fail-closed boot | Production refuses empty `RLS_READS_ENABLED` |
| `apps/api/src/middleware/auth.ts` | Source | Authentication | HS256-pinned JWT, multi-secret, bounded Supabase fallback, API-key path, MFA gate |
| `apps/api/src/middleware/api-key.ts` | Source | Key verification | prefix lookup, constant-time hash compare, active/expiry enforcement |
| `apps/api/src/middleware/entitlement.ts` | Source | Plan gate | `requireEntitlement`/`requireActiveSubscription`, documented fail-open |
| `apps/api/src/routes/**` (60 files) | Source | Route matrix | 442 route definitions; 182 `requirePermission` sites; 94 distinct keys |
| `apps/web/lib/auth/*`, `components/{HasPermission,RouteGuard}.tsx` | Source | Client hiding | Documented defense-in-depth; server actions delegate to API |
| `supabase/migrations/5302026_...v3.sql` | Migration | RLS helpers/policies | `is_super_admin()` :638; `user_has_permission` :702; profiles policies :997/:1015 |
| `supabase/migrations/5302118/5302128/5302131/5302424/5302426` | Migration | Catalog + grants | 328 catalog keys; 13 roles |
| `supabase/migrations/5302032/5302042` | Migration | Secrets/keys | webhook `secret text`; api_keys `permissions jsonb`, `expires_at` |
| `supabase/migrations/5302116/5302434` | Migration | PostgREST grants | blanket `authenticated` DML; anon revoked to an allow-list |
| `supabase/migrations/5302435` | Migration | RPC identity | project-task RPCs reject `p_user_id ≠ auth.uid()` for end users |
| `docs/RLS-rollout.md`, `docs/RLS-coverage-matrix.md` | Docs | RLS rollout | allow-list operated via repo secrets (~44 read / ~17 write modules per docs) |
| `apps/api/src/__tests__/*` | Tests | Authz regression | middleware-permissions (15 cases), middleware-admin, tenant-scoping-guard, api-key-auth, get-scoped-client |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log -1` | Command | Bind commit | `8d299b8d` on `main` |
| `git log --oneline 9c0b88c..8d299b8d -- <ACM files>` | Command | Change detection | empty for roles/permissions/org-access/profiles/webhook-management/api-keys/ai/roles/me — ACM state is identical to the previously verified commit |
| Python route scan (`/tmp/opencode/acm_build_matrix.py`) | Command | Build matrix | 442 route definitions; router-level guard census; 182 `requirePermission` refs; 94 distinct keys |
| Python catalog scan (`/tmp/opencode/acm_catalog_check.py`) | Command | Code↔catalog drift | all 94 code-referenced keys exist in the catalog; 10 RLS-referenced keys do not |
| `grep -rn 'requirePermission(...,"view")'` + mutating-verb filter | Command | Action mismatch | exactly one mutating route still view-gated (`ai.ts:174`, documented in-code) |
| `grep -rln "permission.catalog|catalog-lint"` | Command | Catalog lint | no test/script/CI gate exists |
| `grep -rn "NEW.is_super_admin|before update on public.profiles"` | Command | Identity forgeability | no trigger/column guard protecting `is_super_admin` |
| `grep -rn "api_keys" apps/worker/src` | Command | Key pruning | no pruner task |
| `grep -rn "webhook" docs/SECRETS_ROTATION.md` | Command | Secret rotation | no webhook signing-secret rotation procedure |
| Read `client-onboarding-command-center.ts`, `webhook-management.ts`, `api-keys.ts`, `profiles.ts`, `ai.ts`, `roles.ts`, `me.ts`, `org-access.ts`, `admin.ts`, `permissions.ts`, `admin-scope.ts`, `tenant.ts`, `api-key.ts`, `auth.ts`, `supabase.ts`, `rls-startup-check.ts`, `entitlement.ts` | Walk | Reproduce prior findings | Outcomes in the findings list |

### Claim reproducibility summary (prior register rows)

| Prior claim | How checked | Outcome |
|---|---|---|
| ACM-P1-001 onboarding lacks `requirePermission` | Read file + route scan | **verified-fixed** (all routes gated) |
| ACM-P2-002 trust sets inconsistent | Read `roles.ts`/`permissions.ts`/`org-access.ts` | **verified-fixed** (split + consumers) |
| ACM-P2-003 service-role default / no RLS backstop | Read `supabase.ts` + `rls-startup-check.ts` + docs | **partially-fixed** (fail-closed boot + metering; writes still service role) |
| ACM-P2-004 view-gated writes | Full scan of `requirePermission(...,"view")` | **partially-fixed** (one deliberate residual: `ai.ts:174`) |
| ACM-P2-005 webhook reads not manage-gated | Read `webhook-management.ts` GETs | **still-open** |
| ACM-P2-006 API-key expiry unenforced/unpruned | Read `api-key.ts` + tests + worker grep | **partially-fixed** (enforcement added; no pruner) |
| ACM-P2-007 webhook secrets plaintext/no rotation | Read migration + route + docs | **still-open** |
| ACM-P2-008 profile enumeration | Read `profiles.ts` + RLS policy | **still-open** (now scoped to same-org by RLS) |
| ACM-P3-001 UI-only hiding | Read web guards + route scan | **partially-fixed** (API enforces broadly; no coverage gate) |
| ACM-P3-002 no catalog-lint | Grep tests/scripts/CI | **still-open** (code-side drift currently zero) |
| ACM-P3-003 public surface undocumented | Read docs + openapi.yaml | **still-open** (openapi marks `security: []` on 32 ops) |
| ACM-P3-004 `GET /roles/:id` ungated | Read `roles.ts` | **verified-fixed** (requireAdmin) |
| ACM-P3-005 dead RLS `manage` predicates | Catalog scan vs `user_has_permission` refs | **still-open** (10 keys) |
| Extended check: unforgeable identity | Read RLS policies + grants | **fails** — new P1 (`is_super_admin` self-writable) |
| Extended check: key lifecycle | Read issuance/expiry/revocation/pruning | issuance+expiry+revocation present; pruning absent; key `permissions` unenforced (new P2) |

## Executive Summary

The access-control system is materially sound at `8d299b8d`. Enforcement is data-driven and layered: 182 `requirePermission` call sites over 442 route definitions, an effective-permission resolver that unions approved-membership grants and per-org overrides, `requireOrgAccess` + `assertResourceOrg`/`loadOwned` for tenant scoping, a fail-closed RLS startup check, metered RLS bypass, and 18 test files asserting 403/FORBIDDEN behavior. The two headline problems from the previous run are closed: the client-onboarding router is fully permission-gated, and the cross-tenant trust set is now exactly `admin`/`super_admin` (elevated MSP roles no longer traverse tenants). `GET /roles/:id` is admin-gated, API-key expiry is enforced at authentication, and all 94 code-referenced permission keys exist in the catalog.

The remaining risk is concentrated in five places:

1. **A forgeable privilege flag (new, P1).** `profiles.is_super_admin` — the attribute that grants every API permission and unscoped all-tenant RLS reads — is writable by the `authenticated` role through the `profiles_update_self_or_super_admin` RLS policy (`5302026:1015-1026`) with no trigger or column guard. Direct PostgREST access requires the project anon key, which the repo keeps server-side (`5302434:12-15`), so today's exploitability is gated — but the attribute is not unforgeable, and the fix is a small migration.
2. **RLS is still opt-in per module (P2).** `getScopedClient` returns the service-role client unless the module is allow-listed; writes especially remain handler-scoped. Production now refuses to boot with an empty read list and bypass is metered, but the deployed allow-list is not verifiable from the repo.
3. **Read-side over-exposure (P2).** Webhook endpoint/delivery reads and the `api-keys` list are open to any org member; profiles are enumerable by email/id within a tenant; `ai.ts:174` still gates a write with `ai:view`; AI copilot routes are ungated.
4. **Secret/credential hygiene (P2).** Webhook signing secrets remain plaintext with no rotation/expiry; API keys have no pruner and their `permissions` column is decorative (keys act with the creator's full permissions).
5. **Model maintenance (P3).** No catalog-lint means 10 RLS-referenced keys (`documents:manage`, `projects:manage`, `tickets:comment`, …) are dead predicates; no single public-route inventory; no mutating-route guard-coverage gate.

Recommended order: lock `is_super_admin` at the DB (small, high value); then the read-gate fixes (webhooks, api-keys, profiles, AI routes); then catalog-lint (it would pass today and catch the RLS drift); continue the RLS write rollout.

## Inventory

### Role inventory (13 system roles)

| Role key | Tier | Source | Cross-tenant? | Permission bypass? |
|---|---|---|---|---|
| `super_admin` | Platform | `5302026:188-193` | yes (audited) | yes (profile flag + role) |
| `admin` | Platform | `5302026:188-193` | yes (audited) | yes |
| `dispatcher` | MSP elevated | `5302128:30-37` | no | no |
| `engineer` | MSP elevated | `5302128:30-37` | no | no |
| `security-analyst` | MSP elevated | `5302128:30-37` | no | no |
| `project-manager` | MSP elevated | `5302128:30-37` | no | no |
| `finance` | MSP elevated | `5302128:30-37` | no | no |
| `onboarding-specialist` | MSP elevated | `5302128:30-37` | no | no |
| `client_admin` | Client | `5302026:188-193` | no | no |
| `client_user` | Client | `5302026:188-193` | no | no |
| `client-viewer` | Client | `5302128:30-37` | no | no |
| `client-billing` | Client | `5302128:30-37` | no | no |
| `technician` | Internal legacy | `5302026:188-193` | no | no |

Code constants: `apps/api/src/lib/roles.ts:27-37` (tiers), `apps/api/src/lib/permissions.ts:26` (bypass). Web mirror `apps/web/lib/roles.ts:17-26` gates admin-portal visibility only (documented).

### Permission inventory

- Catalog: 328 `(module_key, action_key)` rows across `5302118` (base), `5302131` (governance `manage`), `5302423` (store portal scope), `5302424` (users/roles/organizations/memberships `manage`), `5302426` (`status` actions).
- Code references: 182 `requirePermission` sites / 94 distinct keys in `apps/api/src/routes/**`; all 94 exist in the catalog.
- Grant model: `super_admin` = all; `admin` = all except `:delete` (plus the middleware bypass preserves delete); MSP roles = explicit module unions (`5302128:46-236`); client roles = portal-scoped view (+create/edit on support-facing modules) and store view (`5302423`).
- Dead RLS references (not in catalog): `documents:manage`, `documents:upload`, `projects:manage`, `tickets:manage`, `tickets:comment`, `contracts:create`, `contracts:manage`, `appointments:schedule`, `appointments:manage`, `onboarding:update`.

### Route access matrix (summary; full scan in Appendix A)

| Guard shape | Count / notes |
|---|---|
| Router-level `requireAuth` + `requireOrgAccess` | majority of routers |
| Router-level `requireAdmin` | admin, bulk, business-os, dashboard, search, audit (+ inline on store/users/roles/organizations) |
| Router-level `requireEntitlement` | findings, governance, qbr, security-ops, service-catalog, training-hub |
| Per-route `requirePermission` | 182 sites / 94 keys |
| Public (no router auth) | auth, public, docs, health, webhooks, store/*, analytics (`POST /track` only), `GET /metrics` (shared-token, 404 otherwise) |
| Mutating route without `requirePermission` but admin-gated | `tickets.ts:555 /bulk`, `organizations.ts` domains, `client-portal.ts:137 PUT /entitlements`, store writes |
| Mutating route with no module gate (accepted/documented) | `billing.ts:383 POST /create-portal-session` (customer self-service, comment in-code), `notification-preferences.ts:43 PUT /` (self-scoped), `profiles.ts:120/204` (self-only), comments/updates in projects/assets/tickets, `ai.ts:357` reply-draft (new finding) |

### Sensitive action matrix

| Action | Route | Gate | Notes |
|---|---|---|---|
| Role/permission administration | `roles.ts:96,139,185,252` | `roles:manage` (global) | super_admin role permissions immutable (:269) |
| Membership invite/role change/remove | `memberships.ts:62,123,158`, `users.ts:390` | `users:manage` | org-scoped via `assertOrgScopeMatches` |
| Org lifecycle/domains | `organizations.ts:305,343,406,451-513,546` | `requireAdmin` / `organizations:manage` | |
| API key mint/revoke/delete | `api-keys.ts:56,94,146` | `api-keys:manage` | expiry enforced at auth; list ungated (new P3) |
| Webhook endpoint/delivery management | `webhook-management.ts:275,311,372,430` | `webhooks:manage` | reads ungated (still-open P2) |
| Impersonation audit read/export | `audit.ts:122,168` | `requireAdmin` + `allTenants` | super_admin only |
| Cross-tenant entry | `org-access.ts:48-60,122-124` | `isCrossTenantKey` | written to `impersonation_log` |
| Destructive deletes | most DELETE routes | `*:delete`/`*:manage` + `assertDeleteConfirmed` | |
| Billing portal session | `billing.ts:383` | any org member | documented self-service |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Roles | 4 | `roles.ts:27-37`; `5302128` | no test pinning the tiers; web/API copies | Add trust-set unit test |
| Permissions | 4 | 182 sites; resolver; 15 middleware tests | no catalog-lint; 10 dead RLS keys | Add lint (would pass today) |
| Org/tenant/workspace membership | 4 | `org-access.ts`, `tenant.ts`, `admin-scope.ts` | service-role default on unlisted modules | Continue RLS write rollout |
| Project/ticket/document/billing/API key/webhook permission | 3 | route scan | webhook reads, API-key list/permissions, profiles enumeration, AI routes | Read-gate fixes |
| Admin console | 4 | `requireAdmin` + `admin-scope.ts`; `roles/:id` fixed | impersonation trail needs alerting (sibling domain) | Alert on impersonation |
| Public/authenticated/internal routes | 3 | `app.ts`; openapi `security: []` | no inventory doc or guard | Generate public list from OpenAPI |
| Server actions | 4 | web actions delegate to API; API enforces | no coverage gate | Guard-coverage CI test |
| API endpoints | 4 | 442 defs; 94 keys all in catalog | exceptions above | Same |
| Background jobs | 3 | worker service-role only (`apps/worker/src/services/supabase.ts:13`) | no per-tenant identity; process-level trust only | Document job trust boundary |
| DB helpers | 3 | `user_has_permission` :702; `is_super_admin` :638 | `is_super_admin` forgeable; dead `manage` predicates | Lock the flag; clean predicates |
| Middleware | 4 | auth/admin/permissions/org-access/api-key | resolver uncached (sibling perf domain) | — |
| Client-side hiding | 4 | RouteGuard/HasPermission documented as UX-only | two server gaps | Keep defense-in-depth |

## Detailed Review

### Item: Trust tiers and identity resolution

- Evidence: `apps/api/src/lib/roles.ts:27-65`; `org-access.ts:44-61,111-152`; `admin.ts:40-58`; `admin-scope.ts:54-57`; `permissions.ts:62-75`; `5302026:638-650`.
- What it does: separates cross-tenant roles (audited) from in-tenant elevated staff; `admin-scope` additionally requires the `is_super_admin` profile flag for all-tenant reads.
- Current controls: org-pinned admin checks; impersonation logging; order-independent role scan.
- Missing controls: `is_super_admin` is user-writable under RLS (new P1); no test pins the tier sets.
- Risks: new P1 (forgeable flag); ACM-P2-002 residual (test only).
- Recommended improvement: DB-level lock on the flag; trust-set test.

### Item: Permission enforcement on routes

- Evidence: route scan (Appendix A); `middleware/permissions.ts:54-92`; `client-onboarding-command-center.ts:31-244`; `ai.ts:174,266,289,357`.
- What it does: per-route `module:action` checks with admin bypass and org-scoped resolution.
- Current controls: broad; all referenced keys exist; tenant-scoping static guard test.
- Missing controls: no coverage gate; AI routes ungated/`view`-gated; webhook/API-key reads ungated.
- Risks: ACM-P2-004/005, new P3s.
- Recommended improvement: coverage gate + read gates.

### Item: Tenant scoping of handlers

- Evidence: `lib/tenant.ts:32-97`; `tenant-scoping-guard.test.ts:1-160`; `org-access.ts:297-325`.
- What it does: 404 (not 403) for out-of-scope rows; `loadOwned` for :id loads; platform-admin traversal audited.
- Current controls: consistent; static guard with an explicit allow-list of known-unscoped files.
- Missing controls: heuristic-only (marker strings), allow-list is broad (e.g. `api-keys`, `webhook-management`, `tickets`).
- Risks: allow-listed files can regress without the guard noticing.
- Recommended improvement: shrink the allow-list as the RLS rollout lands; assert `.eq("organization_id"` for tenant tables.

### Item: Key and token lifecycle

- Evidence: `api-key.ts:68-102`; `auth.ts:46-52,67-88`; `routes/api-keys.ts`; `5302042:8`; `5302032:8`; `file-requests.ts:88,131`; `documents.ts:161`.
- What it does: API keys (hashed, prefix-indexed, expiry/active enforced, revocation, `last_used_at`); JWT multi-secret rotation; file-request/document share token expiry enforced; MFA recovery codes (`5302427`).
- Missing controls: no api_keys pruner; key `permissions` unenforced (new P2); webhook secrets plaintext/no rotation (still-open P2); no certificate inventory in repo (`Unknown`/N/A).
- Risks: ACM-P2-006 residual, ACM-P2-007, new P2.

### Item: Database-side authorization (RLS + helpers)

- Evidence: `5302026:638-734` (helpers keyed on `auth.uid()`); `5302026:997-1013,1015-1026,947-954,1683-1690`; `5302435`; `5302436`; `scripts/check-rls-predicate.mjs`; `scripts/verify-rls.mjs` (CI).
- What it does: identity from `auth.uid()`, approved-membership predicates, platform-admin gates via `user_has_role`, definer RPCs no longer trust caller-supplied ids.
- Missing controls: `is_super_admin` writable; 10 dead `manage`/`upload`/`comment` predicates; some policies still hardcode role lists (guarded by `5302436` assertions).
- Risks: new P1; ACM-P3-005.

### Item: Background jobs

- Evidence: `apps/worker/src/services/supabase.ts:13`; `apps/worker/src/tasks/*.ts` (`getSupabaseAdmin` throughout).
- What it does: every job runs with the service-role key; no user identity or RLS.
- Current controls: process isolation, queue auth, deploy gating (sibling domains).
- Missing controls: no per-tenant credential scoping; a task bug has full DB reach.
- Risks: blast radius (tracked as architecture risk, sibling domain).
- Recommended improvement: document the worker trust boundary; prefer service-role wrapper with audit for destructive tasks.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| S-01 | Roles & trust tiers | `roles.ts:27-37` | 2-tier split consumed by gates | No pinning test | P2→fixed | Test the sets |
| S-02 | Permission catalog consistency | 94 code keys vs 328 catalog keys | All code refs resolve | No lint; 10 dead RLS keys | P3 | Catalog-lint |
| S-03 | Org/tenant membership | `org-access.ts:177-255` | Resolve + verify + body-match | Service-role default on unlisted modules | P2 | RLS rollout |
| S-04 | Module CRUD (projects/tickets/documents/billing/keys/webhooks) | route scan | `module:action` guards | Webhook/API-key reads; AI routes | P2/P3 | Gate reads |
| S-05 | Admin console | `admin.ts:22-63`, `admin-scope.ts` | Org-pinned admin + allTenants flag | Impersonation alerting (sibling) | — | — |
| S-06 | Public/authenticated/internal routes | `app.ts:153-233`; openapi `security: []` | Per-route guards; metrics token | No inventory/guard | P3 | Generate inventory |
| S-07 | Server actions | `apps/web/.../actions.ts` | Delegate to API (enforced) | No coverage gate | P3 | CI guard |
| S-08 | API endpoints | 442 defs | Broad `requirePermission` | Exceptions | P2/P3 | Fix exceptions |
| S-09 | Background jobs | worker service-role | Process-level only | No tenant identity | P3 | Document boundary |
| S-10 | DB helpers | `5302026:638-734` | `auth.uid()` keyed | `is_super_admin` forgeable | P1 | Lock flag |
| S-11 | Middleware | auth/admin/permissions/org-access/api-key | Layered, ordered | Resolver uncached | — | (perf domain) |
| S-12 | Client-side hiding | `RouteGuard.tsx`, `HasPermission.tsx` | UX only, documented | Two server gaps | P3 | Keep + gate |

## Findings

The full finding records (severity, evidence, impact, recommendation, owner, status, note) are in `_domains/24_access_control_matrix_audit.json`. Titles and outcomes:

1. **Client-onboarding mutations run without any `requirePermission` gate** — P1, `verified-fixed` (all routes gated; add a 403 regression test).
2. **`PLATFORM_ADMIN_KEYS` (org traversal) and `ADMIN_BYPASS_KEYS` (permission bypass) are inconsistent trust sets** — P2, `verified-fixed` (split at `roles.ts:27-37`; residual: no pinning test, deprecated constant still used for MSP-staff semantics in `tickets.ts`).
3. **RLS is not a database backstop on API requests (service-role is the default client)** — P2, `partially-fixed` (fail-closed boot + metering; writes/unlisted modules still service role; deployed allow-list unverifiable).
4. **Write and state-transition actions gated by `view` permissions (action mismatch)** — P2, `partially-fixed` (only `ai.ts:174` remains, documented in-code).
5. **Webhook endpoint and delivery reads are available to any org member (not manage-gated)** — P2, `still-open`.
6. **API keys store `expires_at` but nothing enforces or prunes expiry** — P2, `partially-fixed` (enforcement + tests present; no pruner).
7. **Webhook signing secrets are stored plaintext with no rotation or expiry** — P2, `still-open`.
8. **Profiles are enumerable by email/id for any authenticated user** — P2, `still-open` (RLS narrows to same-org; `select('*')` returns `encrypted_pii`).
9. **Client-side permission hiding is UI-only for several module actions** — P3, `partially-fixed` (API enforces broadly; no coverage gate).
10. **No catalog-lint: referenced permission keys are not checked against the `permissions` table** — P3, `still-open` (code-side drift currently zero).
11. **Public route surface is broad and has no single documented inventory** — P3, `still-open` (openapi marks 32 public ops).
12. **`GET /roles/:id` and `GET /me/permissions` are readable without an admin gate** — P3, `verified-fixed` (roles admin-gated; me self-scoped by design).
13. **RLS policies reference `manage` permissions that no role holds (dead predicates)** — P3, `still-open` (10 keys).
14. **`profiles.is_super_admin` is user-writable under the RLS self-update policy (forgeable super-admin flag)** — P1, `open` (new).
15. **API-key `permissions` are decorative: keys act with the creator's full permissions and the column is never enforced** — P2, `open` (new).
16. **`GET /api-keys` lists org keys for any org member (no `api-keys:view` gate)** — P3, `open` (new).
17. **AI copilot endpoints have no permission gate** — P3, `open` (new).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Self-granted `is_super_admin` (anon-key precondition) | P1 | Low today / high if a direct Supabase client ships | All API permissions + all-tenant RLS reads | New P1 | Lock the column (revoke UPDATE / trigger) |
| Cross-tenant exposure from a handler scoping bug | P2 | Medium | Tenant data exposure | ACM-P2-003 | RLS write rollout + coverage checks |
| Integration topology / dead-letter PII to org members | P2 | Medium | Info disclosure | ACM-P2-005 | `webhooks:view` gate |
| Plaintext webhook signing secret | P2 | Low-Med | Receiver trust loss | ACM-P2-007 | Encrypt + rotate |
| Machine credential over-privilege | P2 | Medium | Blast radius of a leaked key | New P2 | Enforce key permissions or document |
| Profile enumeration within tenant | P2 | Medium | PII disclosure | ACM-P2-008 | Restrict collection endpoint |
| Silent authz drift | P3 | Medium | Unsatisfiable guards / dead RLS | ACM-P3-002/005 | Catalog-lint |

## Recommendations

### Immediate / Release Blocking

1. Lock `profiles.is_super_admin` at the database (revoke UPDATE on `profiles` from `authenticated` or add a `BEFORE UPDATE` guard trigger) — new P1.
2. Gate webhook read routes with `webhooks:view` (ACM-P2-005).

### This Week

1. Decide the API-key contract: enforce the key `permissions` column or remove/relabel it (new P2); add a pruner for expired keys (ACM-P2-006 residual).
2. Gate `GET /api-keys` with `api-keys:view` (new P3).
3. Restrict `GET /profiles` enumeration (`email` filter, `select('*')`) (ACM-P2-008).
4. Add a denial regression test for onboarding mutations (ACM-P1-001 residual).

### This Month

1. Add `permission-catalog.test.ts` covering `requirePermission` and RLS `user_has_permission` references (ACM-P3-002); delete or define the 10 dead RLS keys (ACM-P3-005).
2. Resolve `ai.ts:174` (`ai:create`) and gate the copilot routes (ACM-P2-004, new P3).
3. Encrypt/rotate webhook signing secrets (ACM-P2-007).
4. Continue the RLS rollout for writes on high-risk modules (ACM-P2-003).

### Later / Platform Evolution

1. Single declarative role/permission source consumed by API, web, and SQL.
2. Role × module × action × tenant authorization matrix run against a seeded database in CI.
3. Public-endpoint inventory generated from OpenAPI plus a guard test for new public handlers.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `is_super_admin` guard trigger/revoke | Closes the P1 escalation mechanism | new migration | user-scoped client cannot change the flag |
| `webhooks:view` on 4 GETs | Closes info disclosure | `routes/webhook-management.ts` | 403 test for client role |
| `api-keys:view` on GET / | Closes key-inventory exposure | `routes/api-keys.ts` | 403 test |
| Catalog-lint test | Passes today; prevents drift | new `__tests__/permission-catalog.test.ts` | Test green |
| Delete/define dead RLS keys | Removes review hazard | new migration | Catalog-lint green |
| AI route gates | Restores action vocabulary | `routes/ai.ts` | 403 for viewer |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Lock `is_super_admin` | P1 | API + DBA | S | — |
| Webhook read gate | P2 | API | S | — |
| API-key permission contract + pruner | P2 | API | M | product decision |
| Profiles enumeration fix | P2 | API | S | — |
| RLS write rollout | P2 | API + DBA | L | env allow-lists |
| Webhook secret encryption/rotation | P2 | API + security | M | secret management |
| Catalog-lint + guard-coverage CI gates | P3 | API | M | outlier fixes |
| Public-route inventory | P3 | API + docs | S | — |
| Worker trust-boundary doc | P3 | platform | S | — |

## Suggested Tests

- **Unit**: `requirePermission` denial for client roles on onboarding mutations; trust-set assertion (`CROSS_TENANT_KEYS === ADMIN_BYPASS_KEYS`, elevated keys never traverse); catalog-lint (code + RLS keys vs `permissions`); API-key permission enforcement (whichever contract is chosen).
- **Integration**: role × org matrix for a representative read/write route per module (200/403/404 expectations); expired/revoked key rejection (exists) plus pruner behavior; webhook read 403 for a `client_user`; profiles `?email=` denial for a non-admin.
- **DB/RLS**: user-scoped client cannot update `profiles.is_super_admin`; `documents:manage` clauses removed or satisfiable; platform-admin gates accept the documented role set.
- **CI**: mutating-route guard-coverage test with an explicit allow-list; openapi public-surface diff.
- **Manual**: verify a `finance` member cannot reach another tenant via `?organization_id=`; verify impersonation events appear in `GET /audit/impersonation`.

## Suggested Documentation Updates

- `docs/portal_admin_permissions_guide.md`: document the two trust tiers, the API-key permission contract, and the deliberate `ai:view` triage exception.
- `docs/RLS-rollout.md`: record the currently deployed allow-list (or a checked-in template) and the write-module roadmap.
- New `docs/access-control-matrix.md`: publish the role × permission × route matrix (this report's Appendix A) and the public-endpoint inventory.
- `docs/SECRETS_ROTATION.md`: add outbound webhook signing-secret rotation.
- `docs/modules/roles.md` (or equivalent): catalog-lint usage and the dead-predicate cleanup.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| What are the deployed `RLS_READS_ENABLED`/`RLS_WRITES_ENABLED` values? | Determines real RLS coverage | GitHub repo/env secrets (operator) |
| Is the Supabase anon key reachable by any end user today (mobile/other clients)? | Sets the true severity of the `is_super_admin` finding | Client inventory / key distribution |
| Are API keys meant to be permission-scoped? | Decides enforce vs remove | Product decision |
| Are webhook/API-key reads intentionally open to org members? | Decides gate vs document | Product decision |
| Is the `ai:view` triage gate permanent? | Action-vocabulary contract | Product decision |

## Appendix

### A. Route scan method

`/tmp/opencode/acm_build_matrix.py` (Python, read-only) parsed `apps/api/src/routes/**/*.ts` for `router.<verb>("path", …)` definitions, router-level `router.use(...)` guards, and `requirePermission("m","a")` occurrences in each route's middleware chain. Raw output: `/tmp/opencode/acm_routes.tsv` (442 definitions). Catalog comparison: `/tmp/opencode/acm_catalog_check.py` (328 catalog keys extracted from `insert into public.permissions` statements across 134 migrations).

### B. Router-level guard census (observed)

`requireAuth+requireOrgAccess` on ~45 routers; `+requireAdmin` on admin/bulk/business-os/dashboard/search/audit; `+requireEntitlement` on findings/governance/qbr/security-ops/service-catalog/training-hub; `requireAuth` only on organizations/roles/me/client-portal/search-portal; no router-level auth on auth/docs/health/public/store/webhooks/analytics (inline guards).

### C. Dead RLS permission references (ACM-P3-005)

`documents:manage` (22 refs), `projects:manage` (17), `documents:upload` (5), `contracts:manage` (4), `tickets:manage`/`tickets:comment`/`contracts:create`/`appointments:schedule`/`appointments:manage`/`onboarding:update` — all in `5302026_...v3.sql`; none defined by any migration.

### D. Verification command log (excerpt)

```
git -C /tmp/opencode/mct-audit-target log --oneline -1
  8d299b8d Merge PR #168: promote develop to main (metrics scrape fixes + register sync)
git log --oneline 9c0b88c..8d299b8d -- apps/api/src/routes/profiles.ts apps/api/src/routes/webhook-management.ts apps/api/src/routes/api-keys.ts apps/api/src/middleware/api-key.ts apps/api/src/routes/ai.ts apps/api/src/routes/roles.ts apps/api/src/routes/me.ts apps/api/src/middleware/org-access.ts apps/api/src/lib/roles.ts
  (empty)
python3 acm_catalog_check.py
  catalog keys: 328
  code-referenced keys NOT in catalog: (none)
  RLS user_has_permission keys NOT in catalog: 10 (listed above)
grep -rn 'requirePermission("[^"]*", *"view")' apps/api/src/routes | (mutating-verb filter)
  apps/api/src/routes/ai.ts:174:router.post("/triage/analyze", requirePermission("ai", "view"), ...
grep -rln "permission.catalog|catalog-lint" apps/api/src/__tests__ scripts .github
  (none)
```

## Findings

| ID | Severity | Title |
|---|---|---|
| ACM-P1-001 | P1 | Client-onboarding mutations run without any `requirePermission` gate |
| ACM-P2-001 | P2 | `PLATFORM_ADMIN_KEYS` (org traversal) and `ADMIN_BYPASS_KEYS` (permission bypass) are inconsistent trust sets |
| ACM-P2-002 | P2 | RLS is not a database backstop on API requests (service-role is the default client) |
| ACM-P2-003 | P2 | Write and state-transition actions gated by `view` permissions (action mismatch) |
| ACM-P2-004 | P2 | Webhook endpoint and delivery reads are available to any org member (not manage-gated) |
| ACM-P2-005 | P2 | API keys store `expires_at` but nothing enforces or prunes expiry |
| ACM-P2-006 | P2 | Webhook signing secrets are stored plaintext with no rotation or expiry |
| ACM-P2-007 | P2 | Profiles are enumerable by email/id for any authenticated user |
| ACM-P3-001 | P3 | Client-side permission hiding is UI-only for several module actions |
| ACM-P3-002 | P3 | No catalog-lint: referenced permission keys are not checked against the `permissions` table |
| ACM-P3-003 | P3 | Public route surface is broad and has no single documented inventory |
| ACM-P3-004 | P3 | `GET /roles/:id` and `GET /me/permissions` are readable without an admin gate |
| ACM-P3-005 | P3 | RLS policies reference `manage` permissions that no role holds (dead predicates) |
| ACM-P1-002 | P1 | `profiles.is_super_admin` is user-writable under the RLS self-update policy (forgeable super-admin flag) |
| ACM-P2-008 | P2 | API-key `permissions` are decorative: keys act with the creator's full permissions and the column is never enforced |
| ACM-P3-006 | P3 | `GET /api-keys` lists org keys for any org member (no `api-keys:view` gate) |
| ACM-P3-007 | P3 | AI copilot endpoints have no permission gate (any org member can run summarization and reply drafts) |
